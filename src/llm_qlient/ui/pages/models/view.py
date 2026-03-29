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

from PyQt6.QtCore import Qt, QObject, QSize, QThread, pyqtSlot, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QSizePolicy,
    QScrollArea,
    QFileDialog
)
from PyQt6.QtGui import QPainter, QPainterPath
from freshqt.core import Themeable, TypographyType
from freshqt.widgets import Button, LineEdit, TypoLabel
from panllm import LLM, LLMConfig, LLMBackend

from llm_qlient import shared
from llm_qlient.core import log
from llm_qlient.core.types import SettingsDict
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
        self.ctx_lbl = info_label_pair("Context:", "", model_info_lyt)
        self.size_lbl = info_label_pair("Disk Size:", "", model_info_lyt)
        self.type_lbl = info_label_pair("Type:", "", model_info_lyt)
        self.update_model_info()

        # Model loading
        model_load_wdg = QWidget()
        model_load_wdg.setFixedWidth(500)

        model_load_lyt = QVBoxLayout()
        model_load_lyt.setContentsMargins(0, 0, 0, 0)
        model_load_lyt.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        model_load_wdg.setLayout(model_load_lyt)
        layout.addWidget(model_load_wdg)

        h3("Load From Disk", model_load_lyt)

        load_lyt = QHBoxLayout()
        load_lyt.setContentsMargins(0, 0, 0, 0)
        model_load_lyt.addLayout(load_lyt)

        self.load_input = LineEdit()
        self.load_input.setPlaceholderText(".../path/to/your/model")
        shared.theme.add_widget(self.load_input)
        load_lyt.addWidget(self.load_input)

        self.browse_btn = Button(icon_name="hi-magnifying-glass", variant=Button.Variant.OUTLINE)
        self.browse_btn.border_radius = -1
        self.browse_btn.setFixedSize(35, 35)
        shared.theme.add_widget(self.browse_btn)
        load_lyt.addWidget(self.browse_btn)

        ctx_lyt = QHBoxLayout()
        ctx_lyt.setContentsMargins(0, 0, 0, 0)
        model_load_lyt.addLayout(ctx_lyt)

        ctx_lbl = TypoLabel("Context length:")
        shared.theme.add_widget(ctx_lbl)
        ctx_lyt.addWidget(ctx_lbl)

        self.ctx_input = LineEdit(str(shared.settings["model_ctx"]))
        self.ctx_input.setPlaceholderText("1024")
        self.ctx_input.setToolTip("You need to reload the model for context length to be updated.")
        shared.theme.add_widget(self.ctx_input)
        ctx_lyt.addWidget(self.ctx_input)

        @self.ctx_input.editingFinished.connect
        def _():
            value = self.ctx_input.text()
            
            try:
                value = int(value)
            except ValueError:
                value = shared.settings["model_ctx"]

            shared.settings["model_ctx"] = value
            self.ctx_input.setText(str(value))

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

    @pyqtSlot()
    def update_model_info(self) -> None:
        """ Update model information labels. """

        if shared.model is None or shared.model.backend == LLMBackend.DUMMY:
            self.name_lbl.setText("Not loaded")
            self.ctx_lbl.setText("0 tokens")
            self.size_lbl.setText("0.0 GB")
            self.type_lbl.setText("Unknown")
            return

        path = Path(shared.model.model_config.path)

        model_name = path.stem
        model_type = path.suffix.replace(".", "")
        model_size = os.path.getsize(path)
        model_size /= 1073741824.0
        model_ctx = shared.model.model_config.context

        self.name_lbl.setText(model_name)
        self.ctx_lbl.setText(f"{model_ctx} tokens")
        self.size_lbl.setText(f"{round(model_size, 2)} GB")
        self.type_lbl.setText(model_type.upper())
    
    def paintEvent(self, e) -> None:
        pt = QPainter(self)
        pt.setRenderHint(QPainter.RenderHint.Antialiasing, on=True)

        w, h = self.width(), self.height()
        border_r = 12

        clippath = QPainterPath()
        clippath.addRoundedRect(0, 0, w, h, border_r, border_r)
        pt.setClipPath(clippath)

        bg_color = shared.theme.qcolor(shared.theme.palette.background_tertiary)
        pt.fillRect(0, 0, w, h, bg_color)


# TODO: Generalize this & put in a common module because it's used in multiple widgets
class Panel(QWidget, Themeable):
    def paintEvent(self, e) -> None:
        pt = QPainter(self)
        pt.setRenderHint(QPainter.RenderHint.Antialiasing, on=True)

        w, h = self.width(), self.height()
        border_r = 12

        clippath = QPainterPath()
        clippath.addRoundedRect(0, 0, w, h, border_r, border_r)
        pt.setClipPath(clippath)

        bg_color = shared.theme.qcolor(shared.theme.palette.background_tertiary)
        pt.fillRect(0, 0, w, h, bg_color)


class ModelConfiguration(QWidget):
    """
    Model configuration panel widget.
    """

    def __init__(self) -> None:
        super().__init__()

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self._last_row: QHBoxLayout | None = None
        self.new_row()

        self.add_config_field(
            "Generation Length",
            "Maximum number of tokens the model can generate for one inference.",
            "gen_length"
        )

        self.add_config_field(
            "Seed",
            "Sampling seed.\nLeave at -1 to shuffle the seed randomly for each new generation.",
            "gen_seed"
        )

        self.add_config_field(
            "Temperature",
            "Sampling temperature.\nHigher values increase the diversity of new tokens, lower values make it more deterministic.",
            "gen_temp"
        )

        self.new_row()

        self.add_config_field(
            "top-p",
            "Threshold value for nucleus (Top-P) sampling.",
            "gen_top_p"
        )

        self.add_config_field(
            "min-p",
            "Value to use for Minimum P sampling.",
            "gen_min_p"
        )

        self.add_config_field(
            "top-k",
            "Top-K value to use for sampling.",
            "gen_top_k"
        )

        self.new_row()

        self.add_config_field(
            "Frequence Penalty",
            "The penalty value to apply to tokens based on their frequency in the current context.",
            "gen_frequence_penalty"
        )

        self.add_config_field(
            "Presence Penalty",
            "The penalty value to control whether to apply a penalty to tokens that are already present in the current context.",
            "gen_presence_penalty"
        )

        layout.addStretch()

        layout.addSpacing(40)

    def new_row(self) -> None:
        """ Add a new row. """

        self.layout().addSpacing(15)

        self._last_row = QHBoxLayout()
        self._last_row.setContentsMargins(0, 0, 0, 0)
        self._last_row.setSpacing(15)
        self._last_row.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.layout().addLayout(self._last_row)

    def add_config_field(self,
            title: str,
            desc: str = "",
            setting: str = ""
            ) -> None:
        """
        Add new configuration section.

        Parameters
        ----------
        title
            Short title of the field
        desc
            Description of the field
        setting
            Setting key
        """
        if self._last_row.count() >= 3:
            self.new_row()

        field_lyt = QVBoxLayout()
        field_pad = 10
        field_lyt.setContentsMargins(field_pad, field_pad, field_pad, field_pad)

        field_wdg = Panel()
        field_wdg.setLayout(field_lyt)
        self._last_row.addWidget(field_wdg)

        title_lbl = TypoLabel(title, TypographyType.SUBTITLE)
        shared.theme.add_widget(title_lbl)
        field_lyt.addWidget(title_lbl)

        if desc:
            desc_lbl = TypoLabel(desc, TypographyType.BODY)
            desc_lbl.setWordWrap(True)
            desc_lbl.color = "text_secondary"
            shared.theme.add_widget(desc_lbl)
            field_lyt.addWidget(desc_lbl)

        field_lyt.addStretch()

        # TODO: Make this reusable, settings View also uses exact same stuff
        #       something like SettingsLineEdit?
        if setting:
            if isinstance(shared.settings[setting], str):
                line = LineEdit(shared.settings[setting])
                shared.theme.add_widget(line)
                field_lyt.addWidget(line, alignment=Qt.AlignmentFlag.AlignBottom)

                @line.editingFinished.connect
                def _():
                    shared.settings[setting] = line.text()

            elif isinstance(shared.settings[setting], int):
                line = LineEdit(str(shared.settings[setting]))
                shared.theme.add_widget(line)
                field_lyt.addWidget(line, alignment=Qt.AlignmentFlag.AlignBottom)

                @line.editingFinished.connect
                def _():
                    value = line.text()
                    
                    try:
                        value = int(value)
                    except ValueError:
                        value = shared.settings[setting]

                    shared.settings[setting] = value
                    line.setText(str(value))

            elif isinstance(shared.settings[setting], float):
                line = LineEdit(str(shared.settings[setting]))
                shared.theme.add_widget(line)
                field_lyt.addWidget(line, alignment=Qt.AlignmentFlag.AlignBottom)

                @line.editingFinished.connect
                def _():
                    value = line.text()
                    
                    try:
                        value = float(value)
                    except ValueError:
                        value = shared.settings[setting]

                    shared.settings[setting] = value
                    line.setText(str(value))

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

        content_scroller.setStyleSheet("""
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

        self.content_lyt.addSpacing(45)

        h1("Model Configuration", self.content_lyt)

        self.model_config = ModelConfiguration()
        self.content_lyt.addWidget(self.model_config)

        self.controller = Controller(self)


class LoaderWorker(QThread):
    """
    Threaded model loader.
    """

    load_success = pyqtSignal()
    load_fail = pyqtSignal()

    def __init__(self, cfg: LLMConfig) -> None:
        super().__init__()
        self._cfg = cfg

    def _log_repr(self) -> str:
        return f"<fg.blue>[Thrd#{int(self.currentThreadId())}] LOADER:</>"

    def run(self) -> None:
        log.debug(f"{self._log_repr()} Started.")

        try:
            _start = perf_counter()
            shared.model = LLM(self._cfg, LLMBackend.LLAMA_CPP)
            _elapsed = perf_counter() - _start

            log.info(f"{self._log_repr()} Model loaded successfully in <fg.lightcyan>{round(_elapsed,2)}s</> at <fg.darkgray>'{self._cfg.path}'</>")
            self.load_success.emit()
        
        except ValueError as e:
            log.error(f"{self._log_repr()} Failed to load model at <fg.darkgray>'{self._cfg.path}'</>. Exception:\n{e}")
            self.load_fail.emit()

        log.debug(f"{self._log_repr()} Finished.")


class Controller(QObject):
    """
    Models user interface controller.
    """

    def __init__(self, view: View) -> None:
        super().__init__()
        self.view = view

        self.view.model_panel.browse_btn.clicked.connect(self.browse_models)
        self.view.model_panel.load_btn.clicked.connect(self.load_current_model)
        self.view.model_panel.unload_btn.clicked.connect(self._unload_model)

        shared.settings.changed.connect(self._settings_changed)

        self._worker: LoaderWorker | None = None

    def _settings_changed(self, changed: SettingsDict) -> None:
        if "model_path" in changed and changed["model_path"] is not None:
            self.load_model(changed["model_path"])
            self.view.model_panel.load_input.setText(changed["model_path"])

    @pyqtSlot()
    def _worker_cleanup(self) -> None:
        if self._worker is not None:
            self._worker.deleteLater()
            self._worker = None
        
        self.view.model_panel.update_model_info()

    def browse_models(self) -> None:
        """ Browse filesytem for models. """

        path = QFileDialog.getOpenFileName(
            self.view,
            "Chose model to load",
            str(Path.cwd().absolute()),
            #options=QFileDialog.Option.ShowDirsOnly
        )[0]

        if path:
            self.view.model_panel.load_input.setText(path)

    def load_model(self, path: str) -> None:
        """
        Load the LLM model at given filepath.

        Parameters
        ----------
        path
            Path to try load the model from
        """
        
        # FIXME
        # if not path or not (os.path.exists(path) and os.path.isdir(path) and os.listdir(path)):
        #     log.debug(f"<fg.yellow>'{path}'</> is not a valid directory.")
        #     return

        # Unload the previously loaded model
        self.unload_model(notify=False)

        context_length = shared.settings["model_ctx"]
        
        shared.toasts.info("Loading model...")
        log.debug(f"Model loading with requested context length <fg.lightcyan>{context_length}</> tokens.")


        cfg = LLMConfig(path=path, context=context_length, verbose=True)
        self._worker = LoaderWorker(cfg)
        self._worker.finished.connect(self._worker_cleanup)
        self._worker.load_success.connect(lambda: shared.toasts.success("Model loaded."))
        self._worker.load_fail.connect(lambda: shared.toasts.error("Failed to load model."))
        self._worker.start()

    def load_current_model(self) -> None:
        """ Load the current model given in search interface. """

        path = self.view.model_panel.load_input.text()
        shared.settings["model_path"] = path

    def _unload_model(self) -> None:
        shared.settings["model_path"] = None
        self.unload_model()

    def unload_model(self, notify: bool = True) -> None:
        """ Unload the current model. """

        if shared.model is not None and shared.model.backend != LLMBackend.DUMMY:
            shared.model.release()

            if notify:
                shared.toasts.success("Model unloaded.")

        elif notify:
            shared.toasts.info("No model to unload.")

        shared.model = LLM(LLMConfig(""), LLMBackend.DUMMY)

        self.view.model_panel.update_model_info()

        log.debug("Model unloaded & panel updated.")