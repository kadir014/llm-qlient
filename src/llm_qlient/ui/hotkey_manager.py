"""

    llm-qlient • Qt desktop client for interacting with local LLMs

    This file is a part of the llm-qlient
    project and distributed under MIT license.

    Repository: https://github.com/kadir014/llm-qlient
    Issues:     https://github.com/kadir014/llm-qlient/issues

"""

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QShortcut, QKeySequence

from llm_qlient.core import log


class HotkeyManager(QObject):
    """
    Global app hotkey manager.

    Signals
    -------
    invoked
        Emitted when a hotkey is pressed
    """

    invoked = pyqtSignal(str, str)

    def __init__(self, parent_window: QWidget) -> None:
        super().__init__()
        self._parent_window = parent_window

        # TODO: This will come from settings
        self._actions: dict[str, str | tuple[str]] = {
            "quit": ("Ctrl+Q", "Ctrl+W"),
        }

        self._shortcuts: dict[str, QShortcut] = {}
        for action, key_seq in self._actions.items():
            if isinstance(key_seq, str):
                self.bind(action, key_seq)

            elif isinstance(key_seq, tuple):
                for k in key_seq:
                    self.bind(action, k)

            else:
                log.error(f"Key sequence {key_seq} has wrong type {type(key_seq)}.")

    def bind(self, action: str, key_seq: str) -> None:
        """
        Bind a new hotkey to an action.

        Parameters
        ----------
        action
            Action name
        key_seq
            Key or key sequence
        """

        self._shortcuts[action] = QShortcut(
            QKeySequence(key_seq), self._parent_window
        )

        self._shortcuts[action].activated.connect(
            lambda: self.invoked.emit(action, key_seq)
        )

        log.debug(f"Action <fg.orange>'{action}'</> is bound to key sequence '<fg.green>{key_seq}</>'")