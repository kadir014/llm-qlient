"""

    llm-qlient - Qt desktop client for interacting with local LLMs

    This file is a part of the llm-qlient
    project and distributed under MIT license.
    https://github.com/kadir014/llm-qlient

"""

from typing import Callable, Any


class Broadcast:
    """
    Lightweight broadcast-listener system.

    Similar to Qt's signal & slot system, but much simpler and doesn't require
    QObject initialization.
    """

    def __init__(self) -> None:
        self._callbacks = set()

    def connect(self, func: Callable[..., Any]) -> Callable[..., Any]:
        """
        Connect a listener callback function to this broadcast.
        
        Doesn't modify the original function.

        Parameters
        ----------
        func
            Callback to connect
        """

        self._callbacks.add(func)
        return func
    
    def disconnect(self, func: Callable[..., Any]) -> None:
        """
        Disconnect a callback function from this broadcast.

        Parameters
        ----------
        func
            Callback to disconnect
        """

        if func in self._callbacks:
            self._callbacks.remove(func)
    
    def emit(self, *args, **kwargs) -> None:
        """ Emit the broadcast. """

        for callback in self._callbacks:
            callback(*args, **kwargs)