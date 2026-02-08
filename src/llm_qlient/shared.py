"""

    llm-qlient  -  Qt desktop client for interacting with local LLMs

    This file is a part of the llm-qlient
    project and distributed under MIT license.
    https://github.com/kadir014/llm-qlient

"""

from typing import TYPE_CHECKING

from freshqt.core import Theme

if TYPE_CHECKING:
    from PyQt6.QtGui import QIcon


################################################################################
#                                                                              #
#                             Global App Context                               #
#                                                                              #
################################################################################

theme = Theme()

icons: dict[str, "QIcon"] = {}