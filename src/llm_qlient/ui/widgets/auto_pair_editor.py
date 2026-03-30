"""

    llm-qlient • Qt desktop client for interacting with local LLMs

    This file is a part of the llm-qlient
    project and distributed under MIT license.

    Repository: https://github.com/kadir014/llm-qlient
    Issues:     https://github.com/kadir014/llm-qlient/issues

"""

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QPlainTextEdit

from llm_qlient import shared


class AutoPairEditor(QPlainTextEdit):
    """
    Plain text editor with auto-pairing.

    Signals
    -------
    only_return_pressed
        Return or enter key is pressed.
    shift_return_pressed
    """

    return_pressed = pyqtSignal(bool)
    
    PAIRS = {
        "\"": "\"",
        "(": ")",
        "{": "}",
        "[": "]",
        "<": ">"
    }

    def keyPressEvent(self, e) -> None:
        if e.key() == Qt.Key.Key_Return or e.key() == Qt.Key.Key_Enter:
            if e.modifiers() == Qt.KeyboardModifier.ShiftModifier:
                self.return_pressed.emit(True)

            else:
                self.return_pressed.emit(False)
                if shared.settings["editor_enter_sends"]:
                    return

        super().keyPressEvent(e)

        if not shared.settings["editor_auto_pair"]:
            return
        
        key = e.text()

        if key in AutoPairEditor.PAIRS:
            cursor = self.textCursor()
            pos = cursor.position()

            pair = AutoPairEditor.PAIRS[key]
            edited = self.toPlainText()
            edited = edited[:pos] + pair + edited[pos:]
            self.setPlainText(edited)

            cursor.setPosition(pos)
            self.setTextCursor(cursor)