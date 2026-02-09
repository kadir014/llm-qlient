"""

    llm-qlient  -  Qt desktop client for interacting with local LLMs

    This file is a part of the llm-qlient
    project and distributed under MIT license.
    https://github.com/kadir014/llm-qlient

"""

from PyQt6.QtWidgets import QWidget


# abc.ABC and QWidgets are unfortunately not compatible
# so we have to enforce abstract methods manually
class BaseView(QWidget):
    def __init__(self) -> None:
        super().__init__()

        return NotImplementedError("BaseView.__init__ is not implemented in the subclass.")