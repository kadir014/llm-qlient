"""

    llm-qlient • Qt desktop client for interacting with local LLMs

    This file is a part of the llm-qlient
    project and distributed under MIT license.

    Repository: https://github.com/kadir014/llm-qlient
    Issues:     https://github.com/kadir014/llm-qlient/issues

"""

from functools import partial

from PyQt6.QtCore import Qt, QSize, QTimer
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PyQt6.QtGui import QPainter, QPainterPath, QColor
from freshqt.widgets import Button, TypoLabel
from freshqt.animation import Tween, Easing

from llm_qlient import shared


class Toast(QWidget):
    """
    Toast notification widget.

    Don't create manually, instead use the toast manager.
    """

    def __init__(self,
            parent: QWidget,
            icon: str,
            icon_color: QColor,
            text: str
        ) -> None:
        super().__init__(parent)

        self.setStyleSheet("background: none;")
        self.setFixedSize(210, 60)

        text_color = shared.theme.qcolor(shared.theme.palette.text_primary)

        layout = QHBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.setLayout(layout)

        self.icon_lbl = QLabel()
        self.icon_lbl.setPixmap(shared.icons.get(icon, icon_color).pixmap(24, 24))
        layout.addWidget(self.icon_lbl)

        self.text_lbl = TypoLabel(text)
        self.text_lbl.color = text_color
        shared.theme.add_widget(self.text_lbl)
        layout.addWidget(self.text_lbl)

        layout.addStretch()

        self.close_btn = Button(variant=Button.Variant.GHOST)
        self.close_btn.border_radius = -1
        self.close_btn.setFixedSize(26, 26)
        self.close_btn.setIcon(shared.icons.get("hi-x-mark", text_color))
        self.close_btn.setIconSize(QSize(20, 20))
        shared.theme.add_widget(self.close_btn)
        layout.addWidget(self.close_btn)

        self._slide_tween = Tween(
            start_value=0.0,
            end_value=1.0,
            value=0.0
        )

        shared.window_resize.connect(self._on_window_resize)

        # Handled by toast manager
        self.timer: QTimer | None = None
        self.current_i = 0

    def update(self) -> None:
        self._slide_tween.update()
        super().update()

    def _cleanup(self) -> None:
        shared.theme.remove_widget(self.text_lbl, update=False)
        shared.theme.remove_widget(self.close_btn, update=False)
        shared.window_resize.disconnect(self._on_window_resize)

    def slide_out(self) -> None:
        """ Slide the toast notification outside viewport. """
        self._slide_tween.play(0.4, reverse=True, easing=Easing.EASE_IN_CUBIC)
        self.update()

    def slide_in(self) -> None:
        """ Slide the toast notification inside viewport. """
        self._slide_tween.play(0.4, easing=Easing.EASE_OUT_CUBIC)
        self.update()

    def _move(self) -> None:
        w, h = self.width(), self.height()

        vw = self.parentWidget().geometry().width()
        vh = self.parentWidget().geometry().height()

        x_spacing = 6
        y_spacing = 6
        self.setGeometry(
            vw - (w + x_spacing) + int((1.0 - self._slide_tween.value) * (w + x_spacing)),
            vh - (h + y_spacing) * (self.current_i + 1),
            w,
            h
        )

    def _on_window_resize(self) -> None:
        # If the new resize is smaller than old, even a forced repaint doesn't work
        # so move the widget inside on main window resize.
        self._move()

    def paintEvent(self, e) -> None:
        pt = QPainter(self)
        pt.setRenderHint(QPainter.RenderHint.Antialiasing, on=True)

        w, h = self.width(), self.height()
        border_r = 10

        clippath = QPainterPath()
        clippath.addRoundedRect(0, 0, w, h, border_r, border_r)
        pt.setClipPath(clippath)

        bg_color = QColor(0, 0, 0, 220)
        pt.fillRect(0, 0, w, h, bg_color)

        self._move()

        # Force repaint & update if animation is not done
        if self._slide_tween.is_started:
            self.update()


class ToastManager:
    """
    Toast notification widget manager.
    """

    def __init__(self, parent: QWidget) -> None:
        """
        Parameters
        ----------
        parent
            Parent widget to show toast notifications on
        """
        self._parent = parent
        self._stack: list[Toast] = []

    def _anim_finished(self, toast: Toast) -> None:
        # The toast lifecycle only has one slide_in then one slide_out
        # if the animation was reverse, it means it was the slide_out
        if toast._slide_tween._reverse:
            # TODO: setParent(None) segfaults, tf?
            toast.hide()
            toast._cleanup()
            toast.deleteLater()

    def close(self, toast: Toast) -> None:
        """
        Close a toast notification and remove from stack.
        
        Parameters
        ----------
        toast
            Toast to close
        """

        # This method might have been invoked before timer
        toast.timer.timeout.disconnect()
        toast.timer.stop()
        toast.timer.deleteLater()

        i = self._stack.index(toast)

        # Move the rest of the stack down
        for j in range(i + 1, len(self._stack)):
            other = self._stack[j]
            other.current_i -= 1
            other._move()
            other.update()

        self._stack.remove(toast)

        toast.slide_out()
    
    def new(self,
            icon: str,
            icon_color: QColor = QColor(255, 255, 255),
            text: str = "",
            duration: float = 3.0
            ) -> Toast:
        """
        Spawn new toast.
        
        Parameters
        ----------
        icon
            Icon name
        icon_color
            Icon color
        text
            Toast text
        duration
            Duration of toast notification in seconds
        """

        toast = Toast(self._parent, icon, icon_color, text)

        toast._slide_tween.finished.connect(partial(self._anim_finished, toast))

        toast.slide_in()
        toast.show()

        self._stack.insert(0, toast)

        # Move the rest of the stack up
        for i in range(1, len(self._stack)):
            other = self._stack[i]
            other.current_i = i
            other._move()
            other.update()

        toast.close_btn.clicked.connect(partial(self.close, toast))

        toast.timer = QTimer()
        toast.timer.timeout.connect(partial(self.close, toast))
        toast.timer.setInterval(int(duration * 1000.0))
        toast.timer.setSingleShot(True)
        toast.timer.start()

        return toast

    def success(self, text: str = "", duration: float = 3.0) -> Toast:
        """
        Spawn new success toast.
        
        Parameters
        ----------
        text
            Toast text
        duration
            Duration of toast notification in seconds
        """

        return self.new(
            "hi-check-circle",
            shared.theme.qcolor(shared.theme.palette.state_success),
            text,
            duration
        )

    def error(self, text: str = "", duration: float = 3.0) -> Toast:
        """
        Spawn new error toast.
        
        Parameters
        ----------
        text
            Toast text
        duration
            Duration of toast notification in seconds
        """

        return self.new(
            "hi-exclamation-circle",
            shared.theme.qcolor(shared.theme.palette.state_error),
            text,
            duration
        )

    def warning(self, text: str = "", duration: float = 3.0) -> Toast:
        """
        Spawn new warning toast.
        
        Parameters
        ----------
        text
            Toast text
        duration
            Duration of toast notification in seconds
        """

        return self.new(
            "hi-exclamation-triangle",
            shared.theme.qcolor(shared.theme.palette.state_warning),
            text,
            duration
        )

    def info(self, text: str = "", duration: float = 3.0) -> Toast:
        """
        Spawn new information toast.
        
        Parameters
        ----------
        text
            Toast text
        duration
            Duration of toast notification in seconds
        """

        return self.new(
            "hi-information-circle",
            shared.theme.qcolor(shared.theme.palette.brand_primary),
            text,
            duration
        )