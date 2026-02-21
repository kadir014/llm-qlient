"""

    llm-qlient • Qt desktop client for interacting with local LLMs

    This file is a part of the llm-qlient
    project and distributed under MIT license.

    Repository: https://github.com/kadir014/llm-qlient
    Issues:     https://github.com/kadir014/llm-qlient/issues

"""

import queue

from PyQt6.QtCore import QThread, pyqtSignal

from panllm import GenerationConfig, ChatChunk

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

    generation_started = pyqtSignal()
    generation_finished = pyqtSignal(ChatChunk)
    new_chat_chunk = pyqtSignal(ChatChunk)

    def __init__(self) -> None:
        super().__init__()

        self.should_run = True

        self._queue: queue.Queue[GenerationRequest] = queue.Queue(1)
        self._is_generating = False

    @property
    def is_generating(self) -> bool:
        """ Is the thread still generating new tokens? """
        return self._is_generating
    
    def start_gen(self, request: GenerationRequest) -> None:
        """ Start generating. """
        self._queue.put(request)

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
            
            log.debug(f"{self._log_repr()} New request")
            
            self._is_generating = True
            self.generation_started.emit()

            cfg = GenerationConfig(
                max_tokens=256,
                temperature=0.7
            )

            # FIXME
            #shared.model._llm.reset()

            # Flatten conversation messages into what chat formatter expects
            messages = [
                {"role": msg.role.name.lower(), "content": msg.content}
                for msg in request.convo.messages
            ]

            stream = shared.model.stream_chat(
                messages,
                generation_config=cfg
            )

            full_content = ""
            for chunk in stream:
                full_content += chunk.content
                self.new_chat_chunk.emit(chunk)

                # This can be modified mid-generation
                if not self._is_generating:
                    break

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
                self.generation_finished.emit(ChatChunk(chunk.role, full_content))

        log.info(f"{self._log_repr()} Generator finished")