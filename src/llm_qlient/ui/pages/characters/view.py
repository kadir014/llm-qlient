"""

    llm-qlient • Qt desktop client for interacting with local LLMs

    This file is a part of the llm-qlient
    project and distributed under MIT license.

    Repository: https://github.com/kadir014/llm-qlient
    Issues:     https://github.com/kadir014/llm-qlient/issues

"""

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QScrollArea,
    QSizePolicy,
    QHBoxLayout
)
from PyQt6.QtGui import QPainter, QPainterPath
from freshqt.core import Theme, Themeable, TypographyType
from freshqt.widgets import Button, Avatar, LineEdit, TypoLabel

from llm_qlient import shared
from llm_qlient.ui.factories import *
from llm_qlient.core.models import Character
from llm_qlient.ui.pages.base_view import BaseView
from llm_qlient.ui.widgets.auto_pair_editor import AutoPairEditor


class CharacterCard(QWidget, Themeable):
    """
    Character card panel widget.
    """

    def __init__(self, character: Character) -> None:
        super().__init__()
        self._character = character

        layout = QHBoxLayout()
        layout.setContentsMargins(17, 17, 17, 17)
        self.setLayout(layout)

        self.avatar = Avatar(character.avatar_pixmap)
        self.avatar.colorize = False
        self.avatar.setFixedSize(95, 95)
        self.avatar.radius = 7
        shared.theme.add_widget(self.avatar)
        layout.addWidget(self.avatar, alignment=Qt.AlignmentFlag.AlignTop)

        layout.addSpacing(7)

        # Character information
        self.char_info_lyt = QVBoxLayout()
        self.char_info_lyt.setContentsMargins(0, 0, 0, 0)
        self.char_info_lyt.setSpacing(15)
        self.char_info_lyt.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addLayout(self.char_info_lyt)

        self.ui_name_lbl = h3(character.ui_name, self.char_info_lyt)
        self.name_lbl = body(character.name, self.char_info_lyt)

        # Character editing
        self.edit_fields: dict[str, list[QWidget]] = {}
        self.add_edit_field("Name", "name")
        self.add_edit_field("Avatar Path", "avatar_path")
        self.add_edit_field("System Prompt", "system_prompt", multiline=True)
        self.add_edit_field("Personality", "personality", multiline=True)

        # Character interactions
        char_interact_lyt = QVBoxLayout()
        char_interact_lyt.setContentsMargins(0, 0, 0, 0)
        char_interact_lyt.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addLayout(char_interact_lyt)

        self.edit_btn = Button("Edit", icon_name="hi-pencil", variant=Button.Variant.OUTLINE)
        self.edit_btn.setIconSize(QSize(20, 20))
        shared.theme.add_widget(self.edit_btn)
        char_interact_lyt.addWidget(self.edit_btn, alignment=Qt.AlignmentFlag.AlignTop)
        self.edit_btn.clicked.connect(self._edit_btn_clicked)

        self.chat_btn = Button("Chat", icon_name="hi-chat-bubble-oval-left")
        self.chat_btn.setIconSize(QSize(20, 20))
        self.chat_btn.background_color = "brand_primary"
        shared.theme.add_widget(self.chat_btn)
        char_interact_lyt.addWidget(self.chat_btn)
        self.chat_btn.clicked.connect(self.start_chat)

        self.__edit_mode = None
        self.edit_mode = False

    @property
    def edit_mode(self) -> bool:
        """ Message editing mode. """
        return self.__edit_mode
    
    @edit_mode.setter
    def edit_mode(self, mode: bool) -> None:
        if mode == self.__edit_mode:
            return
        
        self.__edit_mode = mode

        if mode:
            self.ui_name_lbl.hide()
            self.name_lbl.hide()

            self.chat_btn.hide()
            
            self.edit_btn.text = "Done"
            self.edit_btn.icon_name = "hi-check"
            self.edit_btn.background_color = "state_success"
            self.edit_btn.variant = Button.Variant.BRAND

            for wdgs in self.edit_fields.values():
                for w in wdgs:
                    w.show()
        
        else:
            self.ui_name_lbl.show()
            self.name_lbl.show()

            self.chat_btn.show()

            self.edit_btn.text = "Edit"
            self.edit_btn.icon_name = "hi-pencil"
            self.edit_btn.background_color = "background_secondary"
            self.edit_btn.variant = Button.Variant.OUTLINE

            for wdgs in self.edit_fields.values():
                for w in wdgs:
                    w.hide()

    def toggle_edit_mode(self) -> None:
        """ Toggle enable or disable message editing mode. """
        self.edit_mode = not self.edit_mode

    def start_chat(self) -> None:
        """ Start chatting with this card's character. """

        shared.main_window.change_page("chats")

        # TODO: Need to find a better interface than this tight coupling
        shared.main_window.get_page_from_id("chats").view.convo_cont.new_conversation(self._character)

    def add_edit_field(self,
            label: str,
            attr: str,
            multiline: bool = False
            ) -> None:
        """ Add a new editable field for character model. """

        field_lyt = QHBoxLayout()
        field_lyt.setContentsMargins(0, 0, 20, 0)
        self.char_info_lyt.addLayout(field_lyt)

        content = getattr(self._character, attr)

        lbl = TypoLabel(label, TypographyType.BODY)
        shared.theme.add_widget(lbl)
        field_lyt.addWidget(lbl, alignment=Qt.AlignmentFlag.AlignTop)

        if multiline:
            line = AutoPairEditor()
            line.setPlainText(content)
            field_lyt.addWidget(line)
        else:
            line = LineEdit(content)
            shared.theme.add_widget(line)
            field_lyt.addWidget(line)

        line.setFixedWidth(520)

        self.edit_fields[attr] = (line, lbl)

    def _edit_btn_clicked(self) -> None:
        if self.edit_mode:
            for attr, wdgs in self.edit_fields.items():
                line = wdgs[0]

                if isinstance(line, LineEdit):
                    content = line.text()
                else:
                    content = line.toPlainText()

                setattr(self._character, attr, content)

            self.name_lbl.setText(self._character.name)

            shared.contents.save_characters()

        self.toggle_edit_mode()

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
                padding: 5px;
            }}
        """)
    
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


class View(BaseView):
    """
    Character browser user interface view.
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
            QScrollArea {
                background: transparent;
                border: none;
            }
        """)

        content.setStyleSheet("background: transparent;")

        self.content_lyt = QVBoxLayout()
        self.content_lyt.setContentsMargins(0, 30, 0, 0)
        self.content_lyt.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.content_lyt.setSpacing(15)
        content.setLayout(self.content_lyt)

        h1("Characters", self.content_lyt)

        self.content_lyt.addSpacing(25)

        self.load_cards()

    def load_cards(self) -> None:
        """ Load character card widgets from character models. """

        for char in shared.characters:
            card = CharacterCard(char)
            shared.theme.add_widget(card)
            self.content_lyt.addWidget(card)