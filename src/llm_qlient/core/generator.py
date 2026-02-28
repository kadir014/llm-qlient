"""

    llm-qlient • Qt desktop client for interacting with local LLMs

    This file is a part of the llm-qlient
    project and distributed under MIT license.

    Repository: https://github.com/kadir014/llm-qlient
    Issues:     https://github.com/kadir014/llm-qlient/issues

"""

import queue

from PyQt6.QtCore import QThread, pyqtSignal, pyqtSlot

from panllm import GenerationConfig, ChatChunk, LLMBackend

from llm_qlient import shared
from llm_qlient.core import log
from llm_qlient.core.models import GenerationRequest


class Generator(QThread):
    """
    Text generation thread.

    Signals
    -------
    generation_started
        The thread has started to generate text
    generation_finished
        The thread has finished generating text
    new_chat_chunk
        New text chat chunk generated
    """

    generation_started = pyqtSignal(str)
    generation_finished = pyqtSignal(str, ChatChunk)
    new_chat_chunk = pyqtSignal(str, ChatChunk)

    def __init__(self) -> None:
        super().__init__()

        self.should_run = True

        self._queue: queue.Queue[GenerationRequest] = queue.Queue(1)
        self._is_generating = False

    @property
    def is_generating(self) -> bool:
        """ Is the thread still generating new tokens? """
        return self._is_generating
    
    @pyqtSlot(GenerationRequest)
    def start_gen(self, request: GenerationRequest) -> None:
        """ Start generating. """
        self._queue.put(request)

    @pyqtSlot()
    def stop_gen(self) -> None:
        """ Stop generating. """
        self._is_generating = False

    def _log_repr(self) -> str:
        return f"<fg.blue>[Thrd#{int(self.currentThreadId())}] GEN:</>"
    
    def run(self) -> None:
        log.info(f"{self._log_repr()} Generator started")

        while self.should_run:
            try:
                request = self._queue.get()
            except queue.ShutDown:
                break
            except Exception as e:
                raise e
            
            log.debug(f"{self._log_repr()} New request ({request.mode})")
            
            self._is_generating = True
            self.generation_started.emit(request.mode)

            cfg = GenerationConfig(
                max_tokens=256,
                temperature=0.7
            )

            # FIXME
            if shared.model is not None and shared.model.backend != LLMBackend.DUMMY:
                shared.model._llama.reset()

            # Flatten conversation messages into what chat formatter expects
            messages = [
                {"role": msg.role.name.lower(), "content": msg.content}
                for msg in request.convo.messages
            ]

            # Adjust sent messages for models that enforce role order
            if request.mode == "retry" and messages[-1]["role"] == "assistant":
                messages = messages[:-1]

            stream = shared.model.stream_chat(
                messages,
                generation_config=cfg
            )

            full_content = ""
            last_chunk: ChatChunk | None = None
            for chunk in stream:
                last_chunk = chunk

                full_content += chunk.content
                self.new_chat_chunk.emit(request.mode, chunk)

                # This might be altered mid-generation
                if not self._is_generating:
                    break

            if last_chunk is None:
                log.error(f"{self._log_repr()} Stream was empty, so assistant role is assumed.")
                full_chunk = ChatChunk("assistant", full_content)
            
            else:
                # Every chunk will carry the role, so we can just use the last chunk
                full_chunk = ChatChunk(last_chunk.role, full_content)

            log.debug(
                f"{self._log_repr()} Generation finished:\n"
                f"<fg.lightcyan>{stream.stats.tokens}</> tokens\n"
                f"<fg.lightcyan>{round(stream.stats.elapsed, 2)}</> s\n"
                f"<fg.lightcyan>{round(stream.stats.tokens_per_second, 2)}</> t/s"
            )

            # The queue might have been exhausted by the main thread for termination
            if self.should_run:
                self._queue.task_done()
                self._is_generating = False
                self.generation_finished.emit(request.mode, full_chunk)

        log.info(f"{self._log_repr()} Generator finished")