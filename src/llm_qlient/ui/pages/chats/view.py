"""

    llm-qlient • Qt desktop client for interacting with local LLMs

    This file is a part of the llm-qlient
    project and distributed under MIT license.

    Repository: https://github.com/kadir014/llm-qlient
    Issues:     https://github.com/kadir014/llm-qlient/issues

"""

from pathlib import Path

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QScrollArea, QSizePolicy, QSpacerItem
from PyQt6.QtGui import QIcon, QPainter, QPainterPath, QColor
from freshqt.core import TypographyType
from freshqt.widgets import Button, Divider, TypoLabel
from freshqt.animation import Tween, Easing

from llm_qlient import shared
from llm_qlient.core import log
from llm_qlient.core.types import SettingsDict
from llm_qlient.core.content import load_content
from llm_qlient.core.models import Conversation
from llm_qlient.ui.pages.base_view import BaseView
from llm_qlient.ui.pages.chats.conversation import ConversationView, ConversationController
from llm_qlient.ui.pages.chats.chat_history import ChatHistory


class View(BaseView):
    def __init__(self) -> None:
        super().__init__()

        outer_layout = QHBoxLayout()
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.setLayout(outer_layout)

        self.chat_history = ChatHistory()
        shared.theme.add_widget(self.chat_history)
        outer_layout.addWidget(self.chat_history)

        outer_layout.addStretch()

        self.convo_view = ConversationView()
        self.convo_view.setFixedWidth(880)
        self.convo_view.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        outer_layout.addWidget(self.convo_view)

        outer_layout.addStretch()
        self.hidden_spacer = QSpacerItem(
            self.chat_history.size().width(),
            10,
            QSizePolicy.Policy.Fixed,
            QSizePolicy.Policy.Preferred
        )
        outer_layout.addItem(self.hidden_spacer)

        self.convo_cont = ConversationController(self.convo_view, self.chat_history)

        shared.settings.changed.connect(self._settings_changed)

    def _settings_changed(self, changed: SettingsDict) -> None:
        if "center_conversation_view" in changed:
            self.set_convo_view_centered(changed["center_conversation_view"])

    def set_convo_view_centered(self, centered: bool) -> None:
        """
        Set whether the conversation view is centered relative to
        window or current view layout.

        Parameters
        ----------
        centered
            Change centered
        """

        if centered:
            self.hidden_spacer.changeSize(
                self.chat_history.size().width(),
                10,
                QSizePolicy.Policy.Fixed,
                QSizePolicy.Policy.Preferred
            )
        
        else:
            self.hidden_spacer.changeSize(
                0, 10, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred
            )

        self.layout().update()
        self.update()