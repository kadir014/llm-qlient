"""

    llm-qlient • Qt desktop client for interacting with local LLMs

    This file is a part of the llm-qlient
    project and distributed under MIT license.

    Repository: https://github.com/kadir014/llm-qlient
    Issues:     https://github.com/kadir014/llm-qlient/issues

"""

import queue

from PyQt6.QtCore import QThread, pyqtSignal, pyqtSlot

from panllm import (
    GenerationConfig,
    ChatChunk,
    LLMBackend,
    BaseStream,
    GenerationStats
)

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
    generation_finished = pyqtSignal(str, ChatChunk, GenerationStats)
    new_chat_chunk = pyqtSignal(str, ChatChunk)

    def __init__(self) -> None:
        super().__init__()

        self.should_run = True

        self._queue: queue.Queue[GenerationRequest] = queue.Queue(1)
        self._is_generating = False

        self._last_stream: BaseStream | None = None

    @property
    def is_available(self) -> bool:
        """ Is currently a model loaded or a proper backend is selected? """
        if shared.settings["dev_allow_dummy_gen"]: return True
        return shared.model is not None and shared.model.backend != LLMBackend.DUMMY

    @property
    def is_generating(self) -> bool:
        """ Is the thread still generating new tokens? """
        return self._is_generating
    
    @property
    def stats(self) -> GenerationStats:
        """ Current generation statistics. """
        if self._last_stream is None:
            return GenerationStats()
        
        return self._last_stream.stats
    
    @pyqtSlot(GenerationRequest)
    def start_gen(self, request: GenerationRequest) -> None:
        """ Start generating chat. """
        self._queue.put(request)

    @pyqtSlot()
    def stop_gen(self) -> None:
        """ Stop generating. """
        self._is_generating = False

    def _log_repr(self) -> str:
        return f"<fg.blue>[Thrd#{int(self.currentThreadId())}] GEN:</>"
    
    def _log_config(self, cfg: GenerationConfig) -> None:
        log.debug(
            f"{self._log_repr()} Generation config:\n"
            f"Max length:    <fg.lightcyan>{cfg.max_tokens}</> tokens\n"
            f"Seed:          <fg.lightcyan>{shared.model.seed}</>\n"
            f"Temperature:   <fg.lightcyan>{cfg.temperature}</>\n"
            f"top-p: <fg.lightcyan>{cfg.top_p}</> min-p: <fg.lightcyan>{cfg.min_p}</> top-k: <fg.lightcyan>{cfg.top_k}</>\n"
            f"Freq. Penalty: <fg.lightcyan>{cfg.frequence_penalty}</>\n"
            f"Pres. Penalty: <fg.lightcyan>{cfg.presence_penalty}</>"
        )

    def _log_stats(self, stream: BaseStream) -> None:
        log.debug(
            f"{self._log_repr()} Generation finished:\n"
            f"<fg.lightcyan>{stream.stats.tokens}</> tokens\n"
            f"<fg.lightcyan>{round(stream.stats.elapsed, 2)}</> s\n"
            f"<fg.lightcyan>{round(stream.stats.tokens_per_second, 2)}</> t/s"
        )

    @staticmethod
    def render_system_prompt(request: GenerationRequest) -> str:
        character = request.convo.character
        user = shared.personas[shared.current_persona_idx]

        prompt = character.system_prompt
        prompt = prompt.replace("{{char}}", character.name)
        prompt = prompt.replace("{{user}}", user.name)
        prompt = prompt.replace("{{char_personality}}", character.personality)
        prompt = prompt.replace("{{user_personality}}", user.personality)

        return prompt
    
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
                max_tokens=shared.settings["gen_length"],
                temperature=shared.settings["gen_temp"],
                top_p=shared.settings["gen_top_p"],
                min_p=shared.settings["gen_min_p"],
                top_k=shared.settings["gen_top_k"],
                frequence_penalty=shared.settings["gen_frequence_penalty"],
                presence_penalty=shared.settings["gen_presence_penalty"]
            )

            self._log_config(cfg)

            # FIXME
            if self.is_available and shared.model.backend == LLMBackend.LLAMA_CPP:
                shared.model._llama.reset()

            shared.model.seed = shared.settings["gen_seed"]

            if request.mode in {"new", "retry", "continue"}:
                # Flatten conversation messages into what chat formatter expects
                messages = [
                    {"role": msg.role.name.lower(), "content": msg.content}
                    for msg in request.convo.messages
                ]

                system_msg = {"role": "system", "content": self.render_system_prompt(request)}
                messages.insert(0, system_msg)

                # Adjust sent messages for models that enforce role order
                if request.mode == "retry" and messages[-1]["role"] == "assistant":
                    messages = messages[:-1]

                if (self.is_available and shared.model.backend == LLMBackend.LLAMA_CPP) and request.mode == "continue":
                    # Remove the last assistant message so we can insert generation tag
                    # It will be added later
                    prompt_msgs = messages[:-1]

                    formatter_state = shared.model._formatter.add_generation_prompt
                    shared.model._formatter.add_generation_prompt = True
                    prompt: str = shared.model._formatter(messages=prompt_msgs).prompt
                    shared.model._formatter.add_generation_prompt = formatter_state

                    # chatml-like formats place a '\n' after role tags
                    # prompt = prompt.rstrip()

                    # Append the unfinished assistant content back
                    prompt += messages[-1]["content"]

                    # I haven't encountered this, but remove any leftover tokens
                    # so it can continue generating smoothly just in case
                    prompt = prompt.removesuffix(shared.model.eos_token)
                    prompt = prompt.removeprefix(shared.model.bos_token)

                    stream = shared.model.stream(
                        prompt,
                        generation_config=cfg
                    )

                else:
                    stream = shared.model.stream_chat(
                        messages,
                        generation_config=cfg
                    )

            elif request.mode in {"text"}:
                stream = shared.model.stream(
                    request.convo,
                    generation_config=cfg
                )

            self._last_stream = stream

            full_content = ""
            last_chunk: ChatChunk | str | None = None
            for chunk in stream:
                # In 'continue' and 'text' mode, regular text generation is done
                if isinstance(chunk, str):
                    chunk = ChatChunk("assistant", chunk)

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

            last_stats = stream.stats

            self._log_stats(stream)
            self._last_stream = None

            # The queue might have been exhausted by the main thread for termination
            if self.should_run:
                self._queue.task_done()
                self._is_generating = False
                self.generation_finished.emit(request.mode, full_chunk, last_stats)

        log.info(f"{self._log_repr()} Generator finished")