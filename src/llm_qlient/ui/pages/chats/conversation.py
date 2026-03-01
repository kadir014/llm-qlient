"""

    llm-qlient • Qt desktop client for interacting with local LLMs

    This file is a part of the llm-qlient
    project and distributed under MIT license.

    Repository: https://github.com/kadir014/llm-qlient
    Issues:     https://github.com/kadir014/llm-qlient/issues

"""

from typing import Iterator

from functools import partial
from datetime import datetime

from PyQt6.QtCore import Qt, QSize, QObject, pyqtSlot
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QSizePolicy,
    QScrollArea,
    QPlainTextEdit,
    QBoxLayout
)
from PyQt6.QtGui import QPainter, QPainterPath, QFontMetrics
from freshqt.core import TypographyType, Theme, Themeable, SyntaxLanguage
from freshqt.widgets import Button, TypoLabel, Avatar, Code
from freshqt.palettes.catppuccin import (
    SYNTAX_CATPPUCCIN_MOCHA,
    SYNTAX_CATPPUCCIN_LATTE
)
from panllm import ChatChunk

from llm_qlient import shared
from llm_qlient.core import log
from llm_qlient.core.models import (
    Conversation,
    ConversationMessage,
    ConversationRole,
    Character,
    GenerationRequest
)
from llm_qlient.ui.pages.chats.chat_history import ChatHistory


class InputComposer(QWidget, Themeable):
    """
    Input message composer widget.
    """

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

        self.stop_btn = Button(icon_name="hi-pause", variant=Button.Variant.GHOST)
        self.stop_btn.setFixedSize(btn_height, btn_height)
        self.stop_btn.setIconSize(QSize(icon_height, icon_height))
        self.stop_btn.border_radius = -1
        shared.theme.add_widget(self.stop_btn)
        buttons_lyt.addWidget(self.stop_btn)

        self.set_buttons_state(False)

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

    def get_message(self) -> str:
        """ Get input message text. """
        return self.editor.toPlainText().strip()
    
    def clear_message(self) -> None:
        """ Clear input message text. """
        self.editor.clear()

    def set_buttons_state(self, generating: bool) -> None:
        """
        Set control buttons state.

        Either show action buttons or show the stop button.
        
        Parameters
        ----------
        generating
            Generation state
        """

        if generating:
            self.send_btn.hide()
            self.retry_btn.hide()
            self.continue_btn.hide()
            self.stop_btn.show()

        else:
            self.send_btn.show()
            self.retry_btn.show()
            self.continue_btn.show()
            self.stop_btn.hide()


def recursive_clear(
        layout: QBoxLayout,
        remove_layouts: bool = True,
        remove_widgets: bool = True,
        remove_items: bool = True
        ) -> None:
    """
    Clear out a layout recursively.

    Parameters
    ----------
    layout
        Layout to clear recursively
    remove_layouts
        Remove children layouts
    remove_widgets
        Remove children widgets
    remove_items
        Remove children spacer items
    """
    for i in reversed(range(layout.count())):
        item = layout.itemAt(i)

        if remove_layouts:
            lyt = item.layout()
            if lyt is not None:
                recursive_clear(
                    lyt, remove_layouts, remove_widgets, remove_items
                )
                layout.removeItem(lyt)
                lyt.setParent(None)
                lyt.deleteLater()

        if remove_widgets:
            wdg = item.widget()
            if wdg is not None:
                shared.theme.remove_widget(wdg, update=False)
                layout.removeWidget(wdg)
                wdg.setParent(None)
                wdg.deleteLater()

        if remove_items:
            s = item.spacerItem()
            if s is not None:
                layout.removeItem(s)


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

        self.avatar = Avatar()
        shared.theme.add_widget(self.avatar)
        title_lyt.addWidget(self.avatar)

        self.name_lbl = TypoLabel(type=TypographyType.SUBTITLE)
        self.name_lbl.setText(name)
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

        self.__edit_mode = False

        self.editor = QPlainTextEdit()
        self.editor.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.editor.hide()
        self.editor.setObjectName("msg_editor")
        self.content_lyt.addWidget(self.editor)

        self.__content_wdgs: list[QWidget] = []

        self.footer_lyt = QHBoxLayout()
        self.footer_lyt.setContentsMargins(0, 0, 0, 0)
        self.footer_lyt.setSpacing(5)
        layout.addLayout(self.footer_lyt)

        self.footer_avatar = Avatar()
        shared.theme.add_widget(self.footer_avatar)
        self.footer_avatar.setFixedSize(16, 16)

        dt = datetime.fromtimestamp(convo_msg.timestamp)
        self.footer_text = TypoLabel(f"Sent by {name} at {dt.strftime('%H:%M')}", type=TypographyType.CAPTION)
        shared.theme.add_widget(self.footer_text)

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

        if rtl:
            self.footer_lyt.addWidget(self.footer_copy_btn)
            self.footer_lyt.addWidget(self.footer_edit_btn)
            self.footer_lyt.addWidget(self.footer_text, alignment=Qt.AlignmentFlag.AlignRight)
            self.footer_lyt.addWidget(self.footer_avatar)
        else:
            self.footer_lyt.addWidget(self.footer_avatar)
            self.footer_lyt.addWidget(self.footer_text)
            self.footer_lyt.addWidget(self.footer_copy_btn, alignment=Qt.AlignmentFlag.AlignRight)
            self.footer_lyt.addWidget(self.footer_edit_btn)

    @property
    def content(self) -> list[TypoLabel | Code]:
        """ Reference list to conversation bubble's content. """
        return self.__content_wdgs.copy()
    
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

        self.footer_text.color = theme.qcolor(theme.palette.text_tertiary)

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
            }}
        """)

    def theme_removed(self) -> None:
        shared.theme.remove_widget(self.avatar, update=False)
        shared.theme.remove_widget(self.name_lbl, update=False)
        shared.theme.remove_widget(self.footer_avatar, update=False)
        shared.theme.remove_widget(self.footer_text, update=False)
        shared.theme.remove_widget(self.footer_edit_btn, update=False)
        shared.theme.remove_widget(self.footer_copy_btn, update=False)
        shared.theme.remove_widget(self.editor, update=False)

        recursive_clear(self.layout())
        
        for widget in self.__content_wdgs:
            shared.theme.remove_widget(widget, update=False)
            widget.setParent(None)
        self.__content_wdgs = []

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
        title_width = self.name_lbl.sizeHint().width() + self.avatar.width() + 36
        footer_width = (
            self.footer_avatar.width() + 
            self.footer_copy_btn.width() + self.footer_edit_btn.width() + 
            self.footer_text.sizeHint().width() + 40
        )
        max_width = max(max_width, max(title_width, footer_width))

        self.setFixedWidth(min(max_width, 880))

    def _add_subcontent_label(self, content: str) -> None:
        content = content.replace("\n", "\n\n")
        lbl = TypoLabel(content)
        lbl.setWordWrap(False)
        lbl.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse | Qt.TextInteractionFlag.LinksAccessibleByMouse)
        lbl.setTextFormat(Qt.TextFormat.MarkdownText)
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

    def add_content(self, content: str) -> QWidget:
        """
        Add new content.

        Text is parsed and sections between triple backquotes are added as code blocks.

        Returns the last created widget.

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

            if char == "`" and content[i + 1] == "`" and content[i + 2] == "`":

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

        return self.__content_wdgs[-1]

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


class ConversationView(QWidget):
    """
    Conversation user interface view.
    """

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
        self.bubbles_content.setLayout(self.bubbles_lyt)

        self.bubbles_lyt.setAlignment(Qt.AlignmentFlag.AlignTop)
        #self.bottom_spacer = QSpacerItem(1, 1, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.content_scroller = QScrollArea()
        self.content_scroller.setWidget(self.bubbles_content)
        self.content_scroller.setWidgetResizable(True)
        self.content_scroller.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        layout.addWidget(self.content_scroller)
        self.content_scroller.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.content_scroller.setStyleSheet("""
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

        # Disclaimer for when there are not conversations
        self.disclaimer = QWidget()
        layout.addWidget(self.disclaimer, alignment=Qt.AlignmentFlag.AlignCenter)
        disc_layout = QVBoxLayout()
        disc_layout.setContentsMargins(0, 0, 0, 0)
        disc_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.disclaimer.setLayout(disc_layout)

        lbl = TypoLabel("You have no conversations. 💔", type=TypographyType.LARGE_TITLE)
        shared.theme.add_widget(lbl)
        disc_layout.addWidget(lbl)

        lbl = TypoLabel("Choose a character and start chatting!", type=TypographyType.BODY)
        shared.theme.add_widget(lbl)
        disc_layout.addWidget(lbl, alignment=Qt.AlignmentFlag.AlignHCenter)

        self.toggle_disclaimer_state(True)

    def toggle_disclaimer_state(self, disclaimer: bool) -> None:
        """ Choose whether to display conversation widgets or the disclaimer. """

        if disclaimer:
            self.disclaimer.show()
            self.content_scroller.hide()
            self.bubbles_content.hide()
            self.input_composer.hide()

        else:
            self.disclaimer.hide()
            self.content_scroller.show()
            self.bubbles_content.show()
            self.input_composer.show()

    def add_bubble(self,
            convo_msg: ConversationMessage,
            character: Character
            ) -> ConversationBubble:
        """
        Add new chat message bubble.
        
        Parameters
        ----------
        convo_msg
            Conversation message model to get data from
        character
            Conversation character
        """

        rtl = convo_msg.role == ConversationRole.USER

        # Since user persona can be changed at anytime, always use the most recent
        # user persona for chat bubble title, instead of storing the user persona
        # too with conversation data.
        if rtl:
            name = shared.personas[shared.current_persona_idx].name
        else:
            name = character.ui_name

        c = ConversationBubble(self, convo_msg, name, rtl=rtl)
        shared.theme.add_widget(c)
        c.add_content(convo_msg.content.strip())
        c.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)

        single_bubble_lyt = QHBoxLayout()
        single_bubble_lyt.setObjectName("single_bubble_lyt")
        single_bubble_lyt.setContentsMargins(0, 0, 0, 0)
        single_bubble_lyt.setSpacing(0)
        if rtl:
            single_bubble_lyt.addStretch()
            single_bubble_lyt.addWidget(c)
        else:
            single_bubble_lyt.addWidget(c)
            single_bubble_lyt.addStretch()
        self.bubbles_lyt.addLayout(single_bubble_lyt)

        c.set_word_wrapping(True)

        return c
    
    def iter_bubbles(self) -> Iterator[ConversationBubble]:
        """ Iterate over message bubble widgets. """

        for i in range(self.bubbles_lyt.count()):
            bubble_lyt = self.bubbles_lyt.itemAt(i).layout()
            if bubble_lyt is not None:

                for j in range(bubble_lyt.count()):
                    bubble = bubble_lyt.itemAt(j).widget()

                    if bubble is not None and isinstance(bubble, ConversationBubble):
                        yield bubble
    
    def get_bubble_by_message(self,
            convo_msg: ConversationMessage
            ) -> ConversationBubble | None:
        """
        Get message bubble by conversation message model.
        
        Parameters
        ----------
        convo_msg
            Conversation message model
        """

        for bubble in self.iter_bubbles():
            if bubble._convo_msg == convo_msg:
                return bubble
            
    def clear(self) -> None:
        """ Clear all bubble widgets from layout. """

        # Remove references from theme
        shared.theme.remove_widgets_by_type(ConversationBubble, update=False)

        # https://stackoverflow.com/a/25330164
        # Remove items parents as well, allowing them to be deleted gracefully
        for i in reversed(range(self.bubbles_lyt.count())):
            w = self.bubbles_lyt.itemAt(i).layout()
            if w is not None and w.objectName() == "single_bubble_lyt":
                self.bubbles_lyt.removeItem(w)
                w.setParent(None)
                w.deleteLater()
            
    def load_conversation(self) -> None:
        """
        Load a new conversation after clearing the current one.
        
        Parameters
        ----------
        convo
            Conversation to be loaded
        """

        self.clear()

        if len(shared.convos) > 0:
            convo = shared.convos[shared.current_convo_idx]

            for convo_msg in convo.messages:
                self.add_bubble(convo_msg, convo.character)

            shared.theme.update_last_widgets()

            self.toggle_disclaimer_state(False)

            log.info(f"Loaded conversation <fg.yellow>{convo.character.ui_name}</> (index <fg.lightcyan>{shared.current_convo_idx}</>)")

        else:
            self.toggle_disclaimer_state(True)

            log.info("No conversation to load.")

        # TODO: I need to investigate this, if I don't repaint after clearing up
        #       the content, some stuff remains
        self.repaint()


class ConversationController(QObject):
    """
    Conversation user interface controller.
    """

    def __init__(self, view: ConversationView, history: ChatHistory) -> None:
        super().__init__()
        self.view = view
        self.history = history

        # Gets updated by thread signals
        self.stream_bubble: ConversationBubble | None = None
        self.stream_msg: ConversationMessage | None = None

        for convo in shared.convos:
            entry = history.add_entry(convo)
            entry.button.clicked.connect(partial(self._chat_history_entry_clicked, convo))

        self.view.toggle_disclaimer_state(len(shared.convos) == 0)

        self.view.input_composer.send_btn.clicked.connect(self.send_new)
        self.view.input_composer.retry_btn.clicked.connect(self.retry_last)
        self.view.input_composer.continue_btn.clicked.connect(self.continue_last)
        self.view.input_composer.stop_btn.clicked.connect(shared.gen.stop_gen)

        self.change_conversation_index(0)

        shared.gen.generation_started.connect(self._generation_started)
        shared.gen.generation_finished.connect(self._generation_finished)
        shared.gen.new_chat_chunk.connect(self._new_chat_chunk)

    def _remove_ref(self) -> None:
        """
        Remove references to streaming widgets to they don't remain and get GC'd.
        """
        self.stream_bubble = None
        self.stream_msg = None

    def send_new(self) -> None:
        """ Send current message to current conversation. """

        if shared.gen.is_generating:
            log.debug("Already generating, skipping 'send'.")
            return

        text = self.view.input_composer.get_message().strip()

        if not text:
            log.debug("Input message is empty, skipping 'send'.")
            return

        self.view.input_composer.clear_message()

        curr_convo = shared.convos[shared.current_convo_idx]

        user_msg = curr_convo.add("user", text)
        self.view.add_bubble(user_msg, curr_convo.character)

        shared.gen.start_gen(GenerationRequest(curr_convo, "new"))

    def retry_last(self) -> None:
        """ Regenerate the last assistant message. """

        if shared.gen.is_generating:
            log.debug("Already generating, skipping 'retry'.")
            return

        if self.stream_msg is None or self.stream_bubble is None:
            self.get_last_assistant_message()

            if self.stream_msg is None or self.stream_bubble is None:
                log.debug("No assistant message found yet, skipping 'retry'.")
                return

        self.stream_msg.content = ""
        self.stream_bubble.clear_content()

        curr_convo = shared.convos[shared.current_convo_idx]
        shared.gen.start_gen(GenerationRequest(curr_convo, "retry"))

    def continue_last(self) -> None:
        """ Continue generating the last assistant message. """

        if shared.gen.is_generating:
            log.debug("Already generating, skipping 'continue'.")
            return
        
        if self.stream_msg is None or self.stream_bubble is None:
            self.get_last_assistant_message()

            if self.stream_msg is None or self.stream_bubble is None:
                log.debug("No assistant message found yet, skipping 'continue'.")
                return
            
        curr_convo = shared.convos[shared.current_convo_idx]
        shared.gen.start_gen(GenerationRequest(curr_convo, "continue"))

    def new_conversation(self, character: Character) -> None:
        """ Start new conversation with character and load it. """

        convo = Conversation(character, [])
        shared.convos.append(convo)
        shared.contents.save_conversations()

        entry = self.history.add_entry(convo)
        entry.button.clicked.connect(partial(self._chat_history_entry_clicked, convo))

        self.change_conversation_index(len(shared.convos) - 1)

    def change_conversation_index(self, convo_idx: int) -> None:
        """ Change current conversation index and load it. """
        
        self._remove_ref()

        shared.current_convo_idx = convo_idx
        self.view.load_conversation()

    def get_last_assistant_message(self) -> None:
        """
        Try to find the latest assistant message.
        
        This overwrites the current streaming message state if found.
        """
        curr_convo = shared.convos[shared.current_convo_idx]

        if len(curr_convo.messages) == 0:
            return

        last_msg = curr_convo.messages[-1]

        if last_msg.role == ConversationRole.ASSISTANT:
            self.stream_msg = last_msg
            self.stream_bubble = self.view.get_bubble_by_message(last_msg)

    @pyqtSlot(str)
    def _generation_started(self, mode: str) -> None:
        curr_convo = shared.convos[shared.current_convo_idx]

        if mode == "new":
            self.stream_msg = curr_convo.add("assistant", "")
            self.stream_bubble = self.view.add_bubble(self.stream_msg, curr_convo.character)

        self.view.input_composer.set_buttons_state(True)

    @pyqtSlot(str, ChatChunk)
    def _generation_finished(self, mode: str, chunk: ChatChunk) -> None:
        # Clear the old non-formatted streamed text and add the formatted version
        self.stream_bubble.clear_content()
        self.stream_bubble.add_content(self.stream_msg.content)
        self.stream_bubble.set_word_wrapping(True)

        self.view.input_composer.set_buttons_state(False)

        shared.contents.save_conversations()

    @pyqtSlot(str, ChatChunk)
    def _new_chat_chunk(self, mode: str, chunk: ChatChunk) -> None:
        # This should never happen, but let's not ignore it
        if self.stream_msg is None or self.stream_bubble is None:
            log.error("Streaming message bubble not found.")
            return

        self.stream_msg.content += chunk.content
        
        if len(self.stream_bubble.content) == 0:
            self.stream_bubble.add_content("")

        # -1 so 'continue' mode can append to the latest content element
        last_cnt = self.stream_bubble.content[-1]
        # TODO: There is the small chance of last content widget being a Code editor
        #       in that case, add a new label content and just keep appending
        if isinstance(last_cnt, TypoLabel):
            last_cnt.setText(self.stream_msg.content)
        self.stream_bubble.set_word_wrapping(True)

        self.view.content_scroller.ensureWidgetVisible(self.stream_bubble, yMargin=120)

    def _chat_history_entry_clicked(self, convo: Conversation) -> None:
        self._remove_ref()

        for i, convo_ in enumerate(shared.convos):
            if convo_ is convo:
                shared.current_convo_idx = i
                break

        self.view.load_conversation()