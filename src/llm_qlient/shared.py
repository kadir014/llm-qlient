"""

    llm-qlient  -  Qt desktop client for interacting with local LLMs

    This file is a part of the llm-qlient
    project and distributed under MIT license.
    https://github.com/kadir014/llm-qlient

"""

from typing import TYPE_CHECKING

from freshqt.core import Theme

from llm_qlient.core.cleaner import Cleaner

if TYPE_CHECKING:
    from llm_qlient.ui.icon_manager import IconManager


################################################################################
#                                                                              #
#                             Global App Context                               #
#                                                                              #
################################################################################

theme = Theme()

icons: "IconManager"

cleaner = Cleaner()