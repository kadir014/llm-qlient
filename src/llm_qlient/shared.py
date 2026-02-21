"""

    llm-qlient • Qt desktop client for interacting with local LLMs

    This file is a part of the llm-qlient
    project and distributed under MIT license.

    Repository: https://github.com/kadir014/llm-qlient
    Issues:     https://github.com/kadir014/llm-qlient/issues

"""

from freshqt.core import Theme
from panllm.backends.base import BaseLLM

from llm_qlient.ui.icon_manager import IconManager
from llm_qlient.core.broadcast import Broadcast
from llm_qlient.core.settings import Settings
from llm_qlient.core.models import Conversation, UserPersona, Character
from llm_qlient.core.generator import Generator


# LLM Qlient version
__version__ = "0.0.1"


################################################################################
#                                                                              #
#                                 App Context                                  #
#                                                                              #
################################################################################

theme = Theme()

icons = IconManager()
theme.icons = icons

cleanup = Broadcast()


################################################################################
#                                                                              #
#                                   Models                                     #
#                                                                              #
################################################################################

characters: list[Character] = []

personas: list[UserPersona] = []
current_persona_idx: int = 0

convos: list[Conversation] = []
current_convo_idx: int = 0


################################################################################
#                                                                              #
#                                 LLM Context                                  #
#                                                                              #
################################################################################

model: BaseLLM | None = None

gen: Generator | None = None


################################################################################
#                                                                              #
#                               Configuration                                  #
#                                                                              #
################################################################################

settings = Settings({
    "system_metrics_show": True,
    "system_metrics_interval": 2.0,
    "system_metrics_formatter": "CPU: {cpu}%     ┆     GPU: {gpu}%     ┆     RAM: {ram_used}GB     ┆     VRAM: {vram_used}GB"
})