"""

    llm-qlient • Qt desktop client for interacting with local LLMs

    This file is a part of the llm-qlient
    project and distributed under MIT license.

    Repository: https://github.com/kadir014/llm-qlient
    Issues:     https://github.com/kadir014/llm-qlient/issues

"""

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QSizePolicy, QHBoxLayout
from PyQt6.QtGui import QPainter, QPainterPath, QPixmap
from freshqt.widgets import Button, Avatar

from llm_qlient import shared
from llm_qlient.core import log, path
from llm_qlient.ui.factories import *
from llm_qlient.core.models import Character
from llm_qlient.ui.pages.base_view import BaseView


class CharacterCard(QWidget):
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
        layout.addWidget(self.avatar)

        layout.addSpacing(7)

        # Character information
        char_info_lyt = QVBoxLayout()
        char_info_lyt.setContentsMargins(0, 0, 0, 0)
        char_info_lyt.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addLayout(char_info_lyt)

        self.ui_name_lbl = h3(character.ui_name, char_info_lyt)

        # Character interactions
        char_interact_lyt = QVBoxLayout()
        char_interact_lyt.setContentsMargins(0, 0, 0, 0)
        char_interact_lyt.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addLayout(char_interact_lyt)

        self.edit_btn = Button("Edit", icon_name="hi-pencil", variant=Button.Variant.OUTLINE)
        self.edit_btn.setIconSize(QSize(20, 20))
        shared.theme.add_widget(self.edit_btn)
        char_interact_lyt.addWidget(self.edit_btn)

        self.chat_btn = Button("Chat", icon_name="hi-chat-bubble-oval-left")
        self.chat_btn.setIconSize(QSize(20, 20))
        self.chat_btn.background_color = "state_success"
        shared.theme.add_widget(self.chat_btn)
        char_interact_lyt.addWidget(self.chat_btn)
        self.chat_btn.clicked.connect(self.start_chat)

    def start_chat(self) -> None:
        """ Start chatting with this card's character. """

        shared.main_window.change_page("chats")

        # TODO: Need to find a better interface than this tight coupling
        shared.main_window.get_page_from_id("chats").view.convo_cont.new_conversation(self._character)
    
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

        h1("Settings", self.content_lyt)

        self.content_lyt.addSpacing(25)

        self.load_cards()

    def load_cards(self) -> None:
        """ Load character card widgets from character models. """

        for char in shared.characters:
            card = CharacterCard(char)
            self.content_lyt.addWidget(card)