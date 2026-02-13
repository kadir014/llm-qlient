"""

    llm-qlient  -  Qt desktop client for interacting with local LLMs

    This file is a part of the llm-qlient
    project and distributed under MIT license.
    https://github.com/kadir014/llm-qlient

"""

import re

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QSizePolicy, QLineEdit, QScrollArea, QPlainTextEdit, QSpacerItem
from PyQt6.QtGui import QIcon, QPainter, QPainterPath, QColor, QFontMetrics
from freshqt.core import TypographyType, Theme, Themeable, SyntaxLanguage
from freshqt.core import __version__ as __freshqt_version__
from freshqt.widgets import Button, Divider, TypoLabel, Switch, LineEdit, BadgeLabel, Avatar, Code
from freshqt.animation import Tween, Easing
from freshqt.palettes.catppuccin import SYNTAX_CATPPUCCIN_MOCHA, SYNTAX_CATPPUCCIN_LATTE
from panllm import __version__ as __panllm_version__

from llm_qlient import shared
from llm_qlient.core import log


class InputComposer(QWidget, Themeable):
    def __init__(self) -> None:
        super().__init__()

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        composer_height = 90
        btn_height = round(composer_height / 3.5)
        icon_height = round(composer_height / 4.7)
        self.setMaximumHeight(composer_height)

        self.editor = QPlainTextEdit()
        layout.addWidget(self.editor)

        buttons_lyt = QVBoxLayout()
        buttons_lyt.setContentsMargins(0, 0, 0, 0)
        buttons_lyt.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        layout.addLayout(buttons_lyt)

        self.send_btn = Button(icon_name="hi-paper-airplane", variant=Button.Variant.GHOST)
        self.send_btn.setFixedSize(btn_height, btn_height)
        self.send_btn.setIconSize(QSize(icon_height, icon_height))
        self.send_btn.border_radius = -1
        shared.theme.add_widget(self.send_btn)
        buttons_lyt.addWidget(self.send_btn)

        self.retry_btn = Button(icon_name="hi-arrow-path", variant=Button.Variant.GHOST)
        self.retry_btn.setFixedSize(btn_height, btn_height)
        self.retry_btn.setIconSize(QSize(icon_height, icon_height))
        self.retry_btn.border_radius = -1
        shared.theme.add_widget(self.retry_btn)
        buttons_lyt.addWidget(self.retry_btn)

        self.continue_btn = Button(icon_name="hi-forward", variant=Button.Variant.GHOST)
        self.continue_btn.setFixedSize(btn_height, btn_height)
        self.continue_btn.setIconSize(QSize(icon_height, icon_height))
        self.continue_btn.border_radius = -1
        shared.theme.add_widget(self.continue_btn)
        buttons_lyt.addWidget(self.continue_btn)

    def update_theme(self, theme: Theme) -> None:
        font_size = int(round(theme.get_typo_size(TypographyType.BODY) * theme.font_scale))
        if font_size <= 0:
            font_size = 1

        self.setStyleSheet(f"""
            QPlainTextEdit {{
                font-family: {theme.font_family};
                font-size: {font_size}px;
                color: {theme.qss(theme.palette.text_primary)};
                background-color: {theme.qss(theme.palette.background_secondary)};
                border: 1px solid {theme.qss(theme.palette.text_tertiary)};
                border-radius: 10px;
                selection-background-color: {theme.qss(theme.palette.text_selection)};
            }}
        """)


class ConversationBubble(QWidget, Themeable):
    def __init__(self, parent: QWidget, rtl: bool = False) -> None:
        super().__init__(parent=parent)

        layout = QVBoxLayout()
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(16)
        self.setLayout(layout)

        #self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)

        title_lyt = QHBoxLayout()
        title_lyt.setContentsMargins(0, 0, 0, 0)
        title_lyt.setSpacing(12)
        layout.addLayout(title_lyt)

        self.avatar = Avatar()
        shared.theme.add_widget(self.avatar)
        title_lyt.addWidget(self.avatar)

        self.name_lbl = TypoLabel(type=TypographyType.SUBTITLE)
        self.name_lbl.setText("Chatgippity")
        shared.theme.add_widget(self.name_lbl)

        if rtl:
            title_lyt.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            title_lyt.addWidget(self.name_lbl)
            title_lyt.addWidget(self.avatar)

        else:
            title_lyt.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            title_lyt.addWidget(self.avatar)
            title_lyt.addWidget(self.name_lbl)

        self.content_lyt = QVBoxLayout()
        self.content_lyt.setContentsMargins(0, 0, 0, 0)
        self.content_lyt.setSpacing(10)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addLayout(self.content_lyt)

        self.__theme: Theme | None = None
        self.__content_wdgs: list[QWidget] = []

    def update_theme(self, theme: Theme) -> None:
        self.__theme = theme

        palette = SYNTAX_CATPPUCCIN_MOCHA if theme.palette.is_dark else SYNTAX_CATPPUCCIN_LATTE

        for wdg in self.__content_wdgs:
            if isinstance(wdg, Code):
                wdg.syntax_palette = palette
    
    def set_word_wrapping(self, wrap: bool = True) -> None:
        max_width = 0
        for wdg in self.__content_wdgs:
            if isinstance(wdg, TypoLabel):
                wdg.setWordWrap(wrap)

                fm = QFontMetrics(wdg.font())
                width = fm.boundingRect(wdg.text()).width() + 30
                #wdg.setFixedWidth(width)

                max_width = max(width, max_width)
                #if width < TextBubbleView.MAX_WIDTH:
                #    self.setFixedWidth(width)
                #else:
                #    self.setFixedWidth(TextBubbleView.MAX_WIDTH)

        self.setFixedWidth(min(max_width, 880))

    def add_content(self, content: str) -> None:
        max_size = 0

        i = 0
        subcontent = ""
        entered_code_block = True
        while i < len(content):
            char = content[i]

            if char == "`" and content[i + 1] == "`" and content[i + 2] == "`":

                if entered_code_block:
                    lbl = TypoLabel(subcontent)
                    lbl.setWordWrap(False)
                    shared.theme.add_widget(lbl)
                    self.content_lyt.addWidget(lbl)
                    self.__content_wdgs.append(lbl)
                    max_size = max(lbl.sizeHint().width(), max_size)
                else:
                    code = Code()
                    code.text = subcontent.strip()
                    code.language = SyntaxLanguage.PYTHON
                    code.hide_status_bar()
                    code.set_readonly(True)
                    code.setMaximumHeight(250)
                    shared.theme.add_widget(code)
                    self.content_lyt.addWidget(code)
                    self.__content_wdgs.append(code)
                    max_size = max(code.sizeHint().width(), max_size)

                entered_code_block = not entered_code_block

                subcontent = ""
                i += 3
                continue

            subcontent += char
            i += 1

        # End of text, add according to last state
        if entered_code_block:
            lbl = TypoLabel(subcontent)
            lbl.setWordWrap(False)
            shared.theme.add_widget(lbl)
            self.content_lyt.addWidget(lbl)
            self.__content_wdgs.append(lbl)
            max_size = max(lbl.sizeHint().width(), max_size)
        else:
            code = Code()
            code.text = subcontent.strip()
            code.language = SyntaxLanguage.PYTHON
            code.hide_status_bar()
            code.set_readonly(True)
            code.setMaximumHeight(250)
            shared.theme.add_widget(code)
            self.content_lyt.addWidget(code)
            self.__content_wdgs.append(code)
            max_size = max(code.sizeHint().width(), max_size)

        # Recover from word wrapping
        #max_size += 300

        #self.setMaximumWidth(min(max_size, 880))

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


class ConversationView(QWidget):
    def __init__(self) -> None:
        super().__init__()

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 12, 0, 12)
        layout.setSpacing(0)
        self.setLayout(layout)

        self.bubbles_content = QWidget()
        self.bubbles_content.setMaximumWidth(880)
        self.bubbles_content.setStyleSheet("background-color: transparent;")
        self.bubbles_lyt = QVBoxLayout()
        self.bubbles_lyt.setContentsMargins(0, 0, 0, 0)
        self.bubbles_lyt.setSpacing(22)
        self.bubbles_lyt.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.bubbles_content.setLayout(self.bubbles_lyt)
        
        c = ConversationBubble(self, rtl=True)
        shared.theme.add_widget(c)
        c.add_content("WHAT ARE PYTHON PROPERTIES???T ARE PYTHON PROPERTIES???T ARE PYTHON PROPERTIES???T WHAT ARE PYTHON PROPERTIES???T ARE PYTHON PROPERTIES???T ARE PYTHON PROPERTIES???T")
        c.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        single_bubble_lyt = QHBoxLayout()
        single_bubble_lyt.setContentsMargins(0, 0, 0, 0)
        single_bubble_lyt.setSpacing(0)
        single_bubble_lyt.addStretch()
        single_bubble_lyt.addWidget(c)
        self.bubbles_lyt.addLayout(single_bubble_lyt)
        c.set_word_wrapping(True)

        c = ConversationBubble(self)
        shared.theme.add_widget(c)
        c.add_content("""
Of course! Here's how to use property decorators in Python: Of course! Here's how to use property decorators in Python: Of course! Here's how to use property decorators in Python:
```
@property
def attr(self) -> int:
    return self._attr

@attr.setter
def attr(self, value: int) -> None:
    self._attr = value
```
As you can see, Python properties are very useful.
""".strip())
        c.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        single_bubble_lyt = QHBoxLayout()
        single_bubble_lyt.setContentsMargins(0, 0, 0, 0)
        single_bubble_lyt.setSpacing(0)
        single_bubble_lyt.addStretch()
        single_bubble_lyt.addWidget(c)
        self.bubbles_lyt.addLayout(single_bubble_lyt)
        c.set_word_wrapping(True)

        #self.bottom_spacer = QSpacerItem(1, 1, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        content_scroller = QScrollArea()
        content_scroller.setWidget(self.bubbles_content)
        content_scroller.setWidgetResizable(True)
        content_scroller.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        layout.addWidget(content_scroller)
        content_scroller.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        content_scroller.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }
        """)

        layout.addSpacing(7)

        self.input_composer = InputComposer()
        shared.theme.add_widget(self.input_composer)
        layout.addWidget(self.input_composer)
        self.input_composer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

class ConversationController:
    def __init__(self) -> None:
        pass