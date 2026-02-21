"""

    llm-qlient • Qt desktop client for interacting with local LLMs

    This file is a part of the llm-qlient
    project and distributed under MIT license.

    Repository: https://github.com/kadir014/llm-qlient
    Issues:     https://github.com/kadir014/llm-qlient/issues

"""

from pathlib import Path

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QScrollArea, QSizePolicy
from PyQt6.QtGui import QIcon, QPainter, QPainterPath, QColor
from freshqt.core import TypographyType
from freshqt.widgets import Button, Divider, TypoLabel
from freshqt.animation import Tween, Easing

from llm_qlient import shared
from llm_qlient.core import log
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
        #self.convo_view.setMinimumWidth(620)
        self.convo_view.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        outer_layout.addWidget(self.convo_view)

        outer_layout.addStretch()
        outer_layout.addSpacing(self.chat_history.size().width())

        self.convo_cont = ConversationController(self.convo_view, self.chat_history)