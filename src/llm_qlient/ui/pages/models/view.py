"""

    llm-qlient • Qt desktop client for interacting with local LLMs

    This file is a part of the llm-qlient
    project and distributed under MIT license.

    Repository: https://github.com/kadir014/llm-qlient
    Issues:     https://github.com/kadir014/llm-qlient/issues

"""

import os
from pathlib import Path
from time import perf_counter

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QSizePolicy, QLineEdit, QScrollArea, QLayout, QFileDialog
from PyQt6.QtGui import QIcon, QPainter, QPainterPath, QColor
from freshqt.core import TypographyType, Theme, Themeable
from freshqt.core import __version__ as __freshqt_version__
from freshqt.widgets import Button, Divider, TypoLabel, Switch, LineEdit, BadgeLabel
from freshqt.animation import Tween, Easing
from panllm import LLM, LLMConfig, LLMBackend

from llm_qlient import shared
from llm_qlient.core import log
from llm_qlient.ui.pages.base_view import BaseView
from llm_qlient.ui.factories import *


class ModelPanel(QWidget, Themeable):
    """
    Model details & loading panel widget.
    """

    def __init__(self) -> None:
        super().__init__()

        layout = QHBoxLayout()
        layout.setContentsMargins(15, 22, 15, 22)
        self.setLayout(layout)

        # Model information
        model_info_lyt = QVBoxLayout()
        model_info_lyt.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(model_info_lyt)

        h3("Current Model", model_info_lyt)

        self.name_lbl = info_label_pair("Name:", "", model_info_lyt)
        self.size_lbl = info_label_pair("Disk Size:", "", model_info_lyt)
        self.type_lbl = info_label_pair("Type:", "", model_info_lyt)
        self.update_model_info()

        # Model loading
        model_load_lyt = QVBoxLayout()
        model_load_lyt.setContentsMargins(0, 0, 0, 0)
        model_load_lyt.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addLayout(model_load_lyt)

        h3("Load From Disk", model_load_lyt)

        load_lyt = QHBoxLayout()
        load_lyt.setContentsMargins(0, 0, 0, 0)
        model_load_lyt.addLayout(load_lyt)

        self.load_input = LineEdit()
        self.load_input.setFixedWidth(400)
        self.load_input.setPlaceholderText(".../path/to/your/model")
        shared.theme.add_widget(self.load_input)
        load_lyt.addWidget(self.load_input)

        self.browse_btn = Button(icon_name="hi-magnifying-glass", variant=Button.Variant.OUTLINE)
        self.browse_btn.border_radius = -1
        self.browse_btn.setFixedSize(35, 35)
        shared.theme.add_widget(self.browse_btn)
        load_lyt.addWidget(self.browse_btn)

        btns_lyt = QHBoxLayout()
        btns_lyt.setContentsMargins(0, 0, 0, 0)
        model_load_lyt.addLayout(btns_lyt)

        self.load_btn = Button("Load", icon_name="hi-arrow-down-circle")
        self.load_btn.setIconSize(QSize(20, 20))
        self.load_btn.background_color = "state_success"
        shared.theme.add_widget(self.load_btn)
        btns_lyt.addWidget(self.load_btn)

        self.unload_btn = Button("Unload", icon_name="hi-x-circle")
        self.unload_btn.setIconSize(QSize(20, 20))
        self.unload_btn.background_color = "state_error"
        shared.theme.add_widget(self.unload_btn)
        btns_lyt.addWidget(self.unload_btn)

        self.__theme: Theme | None = None

    def update_theme(self, theme: Theme) ->  None:
        self.__theme = theme

    def update_model_info(self) -> None:
        """ Update model information labels. """

        if shared.model is None or shared.model.backend == LLMBackend.DUMMY:
            self.name_lbl.setText("Not loaded")
            self.size_lbl.setText("0.0 GB")
            self.type_lbl.setText("Unknown")
            return

        path = Path(shared.model.model_config.path)

        model_name = path.stem
        model_type = path.suffix.replace(".", "")
        model_size = os.path.getsize(path)
        model_size /= 1073741824.0

        self.name_lbl.setText(model_name)
        self.size_lbl.setText(f"{round(model_size, 2)} GB")
        self.type_lbl.setText(model_type.upper())
    
    def paintEvent(self, e) -> None:
        if self.__theme is None: return

        pt = QPainter(self)
        pt.setRenderHint(QPainter.RenderHint.Antialiasing, on=True)

        w, h = self.width(), self.height()
        border_r = 12

        clippath = QPainterPath()
        clippath.addRoundedRect(0, 0, w, h, border_r, border_r)
        pt.setClipPath(clippath)

        pt.fillRect(0, 0, w, h, self.__theme.qcolor(self.__theme.palette.background_tertiary))


class ModelConfiguration(QWidget):
    """
    Model configuration panel widget.
    """

    def __init__(self) -> None:
        super().__init__()

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)


class View(BaseView):
    """
    Models user interface view.
    """

    def __init__(self) -> None:
        super().__init__()

        outer_layout = QVBoxLayout()
        outer_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(outer_layout)

        content = QWidget()
        content.setMaximumWidth(880)
        content.setMinimumWidth(620)

        content_scroller = QScrollArea()
        content_scroller.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        content_scroller.setWidget(content)
        content_scroller.setWidgetResizable(True)
        content_scroller.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        outer_layout.addWidget(content_scroller)

        content_scroller.setStyleSheet(f"""
            background: transparent;
            border: none;
        """)

        self.content_lyt = QVBoxLayout()
        self.content_lyt.setContentsMargins(0, 30, 0, 0)
        self.content_lyt.setAlignment(Qt.AlignmentFlag.AlignTop)
        content.setLayout(self.content_lyt)

        h1("Models", self.content_lyt)

        self.content_lyt.addSpacing(20)

        self.model_panel = ModelPanel()
        shared.theme.add_widget(self.model_panel)
        self.content_lyt.addWidget(self.model_panel)

        self.content_lyt.addSpacing(20)

        self.model_config = ModelConfiguration()
        self.content_lyt.addWidget(self.model_config)

        self.controller = Controller(self)


class Controller:
    """
    Models user interface controller.
    """

    def __init__(self, view: View) -> None:
        self.view = view

        self.view.model_panel.browse_btn.clicked.connect(self.browse)
        self.view.model_panel.load_btn.clicked.connect(self.load_model)
        self.view.model_panel.unload_btn.clicked.connect(self.unload_model)

    def browse(self) -> None:
        path = QFileDialog.getOpenFileName(
            self.view,
            "Chose model to load",
            str(Path.cwd().absolute()),
            #options=QFileDialog.Option.ShowDirsOnly
        )[0]

        if path:
            self.view.model_panel.load_input.setText(path)

    def load_model(self) -> None:
        path = self.view.model_panel.load_input.text()
        
        # if not path or not (os.path.exists(path) and os.path.isdir(path) and os.listdir(path)):
        #     log.debug(f"<fg.yellow>'{path}'</> is not a valid directory.")
        #     return

        # Unload the previously loaded model
        if shared.model is not None:
            shared.model.release()
        
        cfg = LLMConfig(path, 32 * 320, verbose=False)
        try:
            _start = perf_counter()
            shared.model = LLM(cfg, LLMBackend.LLAMA_CPP)
            _elapsed = perf_counter() - _start
            log.info(f"Model loaded successfully in <fg.lightcyan>{round(_elapsed,2)}s</> at <fg.darkgray>'{path}'</>")
        except Exception as e:
            log.error(f"Failed to load model at <fg.darkgray>'{path}'</>. Exception:\n{e}")

        self.view.model_panel.update_model_info()

    def unload_model(self) -> None:
        if shared.model is not None:
            shared.model.release()

        shared.model = None

        self.view.model_panel.update_model_info()

        log.info(f"Model unloaded successfully")