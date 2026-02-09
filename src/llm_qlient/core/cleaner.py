"""

    llm-qlient - Qt desktop client for interacting with local LLMs

    This file is a part of the llm-qlient
    project and distributed under MIT license.
    https://github.com/kadir014/llm-qlient

"""

from typing import Callable


class Cleaner:
    """
    Cleanup manager.

    Whole point of this class is to not rely on __del__, and instead register
    our own cleanup methods. For stuff like joining threads or releasing resources.
    """

    def __init__(self) -> None:
        self.__funcs: list[Callable] = []

    def register(self, func: Callable) -> None:
        """ Regsiter a callback for cleanup. """
        self.__funcs.append(func)

    def cleanup(self) -> None:
        """ Cleanup time. """
        
        for func in self.__funcs:
            func()