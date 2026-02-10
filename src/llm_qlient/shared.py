"""

    llm-qlient  -  Qt desktop client for interacting with local LLMs

    This file is a part of the llm-qlient
    project and distributed under MIT license.
    https://github.com/kadir014/llm-qlient

"""

from typing import TYPE_CHECKING, Any

from freshqt.core import Theme

from llm_qlient.ui.icon_manager import IconManager
from llm_qlient.core.cleaner import Cleaner
from llm_qlient.core.settings import Settings

if TYPE_CHECKING:
    ...


################################################################################
#                                                                              #
#                             Global App Context                               #
#                                                                              #
################################################################################

theme = Theme()

icons = IconManager()
theme.icons = icons

cleaner = Cleaner()


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