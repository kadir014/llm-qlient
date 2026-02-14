"""

    llm-qlient - Qt desktop client for interacting with local LLMs

    This file is a part of the llm-qlient
    project and distributed under MIT license.
    https://github.com/kadir014/llm-qlient

"""

from typing import Any

from dataclasses import dataclass
from enum import Enum, auto
from time import time
import uuid

from PyQt6.QtGui import QIcon

from llm_qlient.ui.pages.base_view import BaseView


def immutable_fields(*field_names: str):
    """
    Make certain fields immutable for a dataclass.

    This relies on `hasattr`, so assignment at initialization is allowed
    but reassignment after is not allowed.

    Parameters
    ----------
    field_names
        Names of the dataclass fields to make immutable
    """

    def wrapper(cls):
        original_setattr = cls.__setattr__

        def __setattr__(self, name: str, value: Any) -> None:
            if name in field_names and hasattr(self, name):
                raise AttributeError(f"{name} is immutable")
            original_setattr(self, name, value)

        cls.__setattr__ = __setattr__
        return cls

    return wrapper


@immutable_fields("id")
@dataclass
class Page:
    """
    Content page.

    Attributes
    ----------
    id
        Internal module representation
    name
        Display name
        Inferred from id if not given
    icon
        Themeable icon name or QIcon instance
    view
        Attached UI view
    """

    id: str
    icon: str | QIcon | None = None
    name: str = ""
    view: BaseView | None = None

    def __post_init__(self) -> None:
        if not self.name:
            self.name = self.id.capitalize()

    def __eq__(self, other: Any) -> bool:
       return isinstance(other, Page) and self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)
    

@dataclass
class Character:
    name: str


class ConversationRole(Enum):
    ASSISTANT = auto()
    USER = auto()

@immutable_fields("id")
@dataclass
class ConversationMessage:
    role: ConversationRole
    content: str
    timestamp: float

    def __post_init__(self) -> None:
        self.id = uuid.uuid4()

    def __eq__(self, other: Any) -> bool:
       return isinstance(other, ConversationMessage) and self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

@dataclass
class Conversation:
    messages: list[ConversationMessage]

    def add(self, role: str, content: str) -> ConversationMessage:
        """ Helper function to add new conversation messages. """

        convo_msg = ConversationMessage(
            ConversationRole[role.upper()], content, time()
        )
        self.messages.append(convo_msg)

        return convo_msg