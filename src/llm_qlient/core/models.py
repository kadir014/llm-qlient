"""

    llm-qlient - Qt desktop client for interacting with local LLMs

    This file is a part of the llm-qlient
    project and distributed under MIT license.
    https://github.com/kadir014/llm-qlient

"""

from dataclasses import dataclass

from PyQt6.QtGui import QIcon

from llm_qlient.ui.pages.base_view import BaseView


@dataclass
class Page:
    """
    Content page.

    Attributes
    ----------
    id
        Internal module name
    name
        Display name
        Inferred from id if not given
    icon
        Themeable icon name or QIcon instance
    view
        Attached UI view
    """

    id: str
    icon: str | QIcon
    name: str = ""
    view: BaseView | None = None

    def __post_init__(self) -> None:
        self.name = self.id.capitalize()