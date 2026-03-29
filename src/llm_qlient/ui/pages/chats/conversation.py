"""

    llm-qlient • Qt desktop client for interacting with local LLMs

    This file is a part of the llm-qlient
    project and distributed under MIT license.

    Repository: https://github.com/kadir014/llm-qlient
    Issues:     https://github.com/kadir014/llm-qlient/issues

"""

from typing import Iterator

from functools import partial

from PyQt6.QtCore import Qt, QObject, pyqtSlot
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QSizePolicy,
    QScrollArea,
    QSpacerItem
)
from freshqt.core import TypographyType
from freshqt.widgets import TypoLabel
from panllm import ChatChunk, GenerationStats

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
from llm_qlient.ui.pages.chats.input_composer import InputComposer
from llm_qlient.ui.pages.chats.bubble import ConversationBubble


class ConversationView(QWidget):
    """
    Conversation user interface view.
    """

    def __init__(self) -> None:
        super().__init__()

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 12)
        layout.setSpacing(0)
        self.setLayout(layout)

        self.bubbles_content = QWidget()
        self.bubbles_content.setMaximumWidth(880)
        self.bubbles_content.setStyleSheet("background-color: transparent;")
        self.bubbles_lyt = QVBoxLayout()
        self.bubbles_lyt.setContentsMargins(0, 0, 0, 0)
        self.bubbles_lyt.setSpacing(22)
        self.bubbles_content.setLayout(self.bubbles_lyt)
        self.bubbles_content.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        # Setting alignment to AlignTop messes label's word wrap,
        # so we just add an expanding spacer item at the bottom
        # self.bubbles_lyt.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.bottom_spacer = QSpacerItem(1, 175, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.content_scroller = QScrollArea()
        self.content_scroller.setWidget(self.bubbles_content)
        self.content_scroller.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.content_scroller.setWidgetResizable(True)
        self.content_scroller.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        layout.addWidget(self.content_scroller)
        self.content_scroller.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.content_scroller.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }
        """)

        layout.addSpacing(7)

        self.input_composer = InputComposer()
        self.input_composer.setFixedWidth(880)
        shared.theme.add_widget(self.input_composer)
        layout.addWidget(self.input_composer, alignment=Qt.AlignmentFlag.AlignHCenter)

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
        c.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)

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

        self.bubbles_lyt.removeItem(self.bottom_spacer)
        self.bubbles_lyt.addItem(self.bottom_spacer)

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

        self.stream_bubble.footer_edit_btn.hide()

        self.view.input_composer.set_buttons_state(True)

    @pyqtSlot(str, ChatChunk, GenerationStats)
    def _generation_finished(self,
            mode: str,
            chunk: ChatChunk,
            stats: GenerationStats
            ) -> None:
        # Clear the old non-formatted streamed text and add the formatted version
        self.stream_bubble.clear_content()
        self.stream_bubble.add_content(self.stream_msg.content)
        self.stream_bubble.set_word_wrapping(True)

        self.stream_bubble.footer_edit_btn.show()

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

        # Last widget so 'continue' mode can append to the latest content element
        last_cnt = self.stream_bubble.last_content_widget
        # TODO: There is the small chance of last content widget being a Code editor
        #       in that case, add a new label content and just keep appending
        if isinstance(last_cnt, TypoLabel):
            last_cnt.setText(self.stream_msg.content)
        self.stream_bubble.set_word_wrapping(True)

        #self.view.content_scroller.ensureWidgetVisible(self.stream_bubble, yMargin=120)

    def _chat_history_entry_clicked(self, convo: Conversation) -> None:
        self._remove_ref()

        for i, convo_ in enumerate(shared.convos):
            if convo_ is convo:
                shared.current_convo_idx = i
                break

        self.view.load_conversation()