"""

    llm-qlient • Qt desktop client for interacting with local LLMs

    This file is a part of the llm-qlient
    project and distributed under MIT license.

    Repository: https://github.com/kadir014/llm-qlient
    Issues:     https://github.com/kadir014/llm-qlient/issues

"""

from typing import TYPE_CHECKING

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QSizePolicy
from PyQt6.QtGui import QPainter, QPainterPath, QFontMetrics, QCursor
from freshqt.core import TypographyType, Theme, Themeable, SyntaxLanguage
from freshqt.widgets import Button, TypoLabel, Avatar, Code
from freshqt.palettes.catppuccin import (
    SYNTAX_CATPPUCCIN_MOCHA,
    SYNTAX_CATPPUCCIN_LATTE
)

from llm_qlient import shared
from llm_qlient.core.models import ConversationMessage
from llm_qlient.ui.layout_utils import recursive_clear
from llm_qlient.ui.widgets.auto_pair_editor import AutoPairEditor

if TYPE_CHECKING:
    from llm_qlient.ui.pages.chats.conversation import ConversationView


class ConversationBubble(QWidget, Themeable):
    """
    Conversation message bubble widget.
    """

    def __init__(self, 
            parent: "ConversationView",
            convo_msg: ConversationMessage,
            name: str,
            rtl: bool = False
            ) -> None:
        """
        Parameters
        ----------
        parent
            Parent view widget
        convo_msg
            Referenced conversation message model
        rtl
            Right-to-left or left-to-right
        """
        super().__init__(parent=parent)
        self._convo_msg = convo_msg

        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)
        self.setLayout(layout)

        title_lyt = QHBoxLayout()
        title_lyt.setContentsMargins(0, 0, 0, 0)
        title_lyt.setSpacing(12)
        layout.addLayout(title_lyt)

        if rtl:
            pixmap = shared.personas[shared.current_persona_idx].avatar_pixmap
        else:
            pixmap = shared.convos[shared.current_convo_idx].character.avatar_pixmap

        self.avatar = Avatar(pixmap)
        self.avatar.colorize = False
        shared.theme.add_widget(self.avatar)
        title_lyt.addWidget(self.avatar)

        self.name_lbl = TypoLabel(type=TypographyType.SUBTITLE)
        self.name_lbl.setText(name)
        shared.theme.add_widget(self.name_lbl)

        self.footer_edit_btn = Button(icon_name="hi-pencil", variant=Button.Variant.GHOST)
        shared.theme.add_widget(self.footer_edit_btn)
        self.footer_edit_btn.border_radius = -1
        self.footer_edit_btn.setIconSize(QSize(18, 18))
        self.footer_edit_btn.setFixedSize(26, 26)
        self.footer_edit_btn.clicked.connect(self.toggle_edit_mode)

        self.footer_copy_btn = Button(icon_name="hi-square-2-stack", variant=Button.Variant.GHOST)
        shared.theme.add_widget(self.footer_copy_btn)
        self.footer_copy_btn.border_radius = -1
        self.footer_copy_btn.setIconSize(QSize(18, 18))
        self.footer_copy_btn.setFixedSize(26, 26)
        self.footer_copy_btn.clicked.connect(self.copy)

        self.footer_edit_btn.setToolTip("Edit message content")
        self.footer_copy_btn.setToolTip("Copy message content")

        if rtl:
            title_lyt.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            title_lyt.addWidget(self.footer_copy_btn)
            title_lyt.addWidget(self.footer_edit_btn)

            title_lyt.addStretch()

            title_lyt.addWidget(self.name_lbl)
            title_lyt.addWidget(self.avatar)

        else:
            title_lyt.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            title_lyt.addWidget(self.avatar)
            title_lyt.addWidget(self.name_lbl)

            title_lyt.addStretch()

            title_lyt.addWidget(self.footer_copy_btn)
            title_lyt.addWidget(self.footer_edit_btn)

        self.content_lyt = QVBoxLayout()
        self.content_lyt.setContentsMargins(0, 0, 0, 0)
        self.content_lyt.setSpacing(10)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addLayout(self.content_lyt)

        self.__edit_mode = False

        self.editor = AutoPairEditor()
        self.editor.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.editor.hide()
        self.editor.setObjectName("msg_editor")
        self.content_lyt.addWidget(self.editor)

        self.__content_wdgs: list[QWidget] = []

    @property
    def content(self) -> list[TypoLabel | Code]:
        """ Reference list to conversation bubble's content. """
        return self.__content_wdgs.copy()
    
    @property
    def last_content_widget(self) -> None | TypoLabel | Code:
        """ Last inserted widget to content, None if empty. """
        return self.__content_wdgs[-1] if len(self.__content_wdgs) > 0 else None
    
    @property
    def edit_mode(self) -> bool:
        """ Message editing mode. """
        return self.__edit_mode
    
    @edit_mode.setter
    def edit_mode(self, mode: bool) -> None:
        if mode == self.__edit_mode:
            return
        
        self.__edit_mode = mode
        self._sync_content()

        if mode:
            self.editor.show()
            for widget in self.__content_wdgs:
                widget.hide()
            
            self.footer_edit_btn.icon_name = "hi-check"
        
        else:
            self.editor.hide()
            for widget in self.__content_wdgs:
                widget.show()

                self.footer_edit_btn.icon_name = "hi-pencil"

    def toggle_edit_mode(self) -> None:
        """ Toggle enable or disable message editing mode. """
        self.edit_mode = not self.edit_mode

    def _sync_content(self) -> None:
        """
        Sync content between message editor and content widgets.

        This is called when editing, you don't have a reason to use this manually.
        """

        if self.__edit_mode:
            self.editor.setPlainText(self._convo_msg.content)

        else:
            new_content = self.editor.toPlainText()
            self._convo_msg.content = new_content

            self.clear_content()
            self.add_content(self._convo_msg.content)
            self.set_word_wrapping(True)
            
            shared.contents.save_conversations()
            shared.toasts.success("Message edited.")

    def update_theme(self, theme: Theme) -> None:
        palette = SYNTAX_CATPPUCCIN_MOCHA if theme.palette.is_dark else SYNTAX_CATPPUCCIN_LATTE

        for wdg in self.__content_wdgs:
            if isinstance(wdg, Code):
                wdg.syntax_palette = palette

        font_size = int(round(theme.get_typo_size(TypographyType.BODY) * theme.font_scale))
        if font_size <= 0:
            font_size = 1

        self.setStyleSheet(f"""
            QPlainTextEdit#msg_editor {{
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

    def theme_removed(self) -> None:
        shared.theme.remove_widget(self.avatar, update=False)
        shared.theme.remove_widget(self.name_lbl, update=False)
        shared.theme.remove_widget(self.footer_edit_btn, update=False)
        shared.theme.remove_widget(self.footer_copy_btn, update=False)
        shared.theme.remove_widget(self.editor, update=False)

        recursive_clear(self.layout())

        self.clear_content()

    def copy(self) -> None:
        """ Copy message bubble text content into clipboard. """
        shared.toasts.success("Message copied.")
        shared.qapp.clipboard().setText(self._convo_msg.content)

    def clear_content(self) -> None:
        """ Clear messabe bubble content. """

        for widget in self.__content_wdgs:
            shared.theme.remove_widget(widget, update=False)
            self.content_lyt.removeWidget(widget)
            widget.setParent(None)
            widget.deleteLater()

        self.__content_wdgs = []
    
    def set_word_wrapping(self, wrap: bool = True) -> None:
        """
        Set word wrapping for all non-code text sections.

        Parameters
        ----------
        wrap
            Enable word wrapping or not
        """
        max_width = 0
        for wdg in self.__content_wdgs:
            if isinstance(wdg, TypoLabel):
                wdg.setWordWrap(wrap)

                fm = QFontMetrics(wdg.font())
                # To prevent unnecessary wrapping
                padding = 34
                width = fm.boundingRect(wdg.text()).width() + padding

                max_width = max(width, max_width)

        # Make sure bubble title or footer doesn't collapse
        title_width = (
            self.name_lbl.sizeHint().width() + 
            self.avatar.width() +
            self.footer_copy_btn.width() + 
            self.footer_edit_btn.width() +
            100
        )
        max_width = max(max_width, title_width)

        self.setFixedWidth(min(max_width, 880))

    def _add_subcontent_label(self, content: str) -> None:
        content = content.replace("\n", "\n\n")
        lbl = TypoLabel(content)

        lbl.setWordWrap(False)
        lbl.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse | Qt.TextInteractionFlag.LinksAccessibleByMouse)
        lbl.setTextFormat(Qt.TextFormat.MarkdownText)
        lbl.setCursor(QCursor(Qt.CursorShape.IBeamCursor))

        shared.theme.add_widget(lbl)
        self.content_lyt.addWidget(lbl)
        self.__content_wdgs.append(lbl)

    def _add_subcontent_code(self, content: str) -> None:
        code = Code()

        code.text = content.strip()
        code.language = SyntaxLanguage.PYTHON
        code.hide_status_bar()
        code.set_readonly(True)
        code.setMaximumHeight(250)

        shared.theme.add_widget(code)
        self.content_lyt.addWidget(code)
        self.__content_wdgs.append(code)

    def add_content(self, content: str) -> QWidget | None:
        """
        Add new content.

        Text is parsed and sections between triple backquotes are added as code blocks.

        Returns the last created widget or None if failed.

        Parameters
        ----------
        content
            Text content to be added
        """
        i = 0
        subcontent = ""
        entered_code_block = True

        while i < len(content):
            char = content[i]

            if i + 2 < len(content) and char == "`" and content[i + 1] == "`" and content[i + 2] == "`":

                if entered_code_block:
                    self._add_subcontent_label(subcontent)
                else:
                    self._add_subcontent_code(subcontent)

                entered_code_block = not entered_code_block

                subcontent = ""
                i += 3
                continue

            subcontent += char
            i += 1

        # End of text, add according to last state
        if entered_code_block:
            self._add_subcontent_label(subcontent)
        else:
            self._add_subcontent_code(subcontent)

        return self.last_content_widget

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