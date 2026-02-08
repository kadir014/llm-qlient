"""

    llm-qlient  -  Qt desktop client for interacting with local LLMs

    This file is a part of the llm-qlient
    project and distributed under MIT license.
    https://github.com/kadir014/llm-qlient

"""

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtGui import QIcon, QPainter, QPainterPath
from freshqt.core import TypographyType
from freshqt.widgets import Button, Divider
from freshqt.animation import Tween, Easing

from llm_qlient import shared


class Sidebar(QWidget):
    def __init__(self) -> None:
        super().__init__()

        self.padding = 7
        self.button_size = 40
        self.icon_size = 24
        self.__open = False

        self.__resize_tween = Tween(
            start_value=self.button_size,
            end_value=self.button_size + 100
        )
        self.__resize_tween.finished.connect(self.__resize_finished)

        self.__cursor_tween = Tween()
        self.__cursor_widget: QWidget | None = None

        self.setFixedWidth(self.button_size + self.padding * 2)

        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.setContentsMargins(self.padding, self.padding, self.padding, self.padding)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.page_buttons: dict[str, Button] = {}

        self.add_page_button("LLM Qlient", shared.icons["windowicon"])
        self.add_divider()

        self.page_buttons["LLM Qlient"].clicked.connect(self.__home_clicked)
        self.page_buttons["LLM Qlient"].type = TypographyType.SUBTITLE

    def update(self) -> None:
        super().update()
        self.__resize_tween.update()
        self.__cursor_tween.update()

    def add_page_button(self, page_name: str, icon: QIcon) -> None:
        """
        Add a new page button to the sidebar.
        
        Parameters
        ----------
        page_name
            Name of the page
        icon
            Button icon
        """

        btn = Button(variant=Button.Variant.GHOST)
        shared.theme.add_widget(btn)
        self.layout().addWidget(btn)

        btn.setIcon(icon)
        btn.setIconSize(QSize(self.icon_size, self.icon_size))
        btn.setFixedSize(self.button_size, self.button_size)
        btn.border_radius = -1
        btn.text_alignment = Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter

        self.page_buttons[page_name] = btn

    def add_divider(self) -> None:
        """ Add divider. """

        dv = Divider(margin=30)
        shared.theme.add_widget(dv)
        self.layout().addWidget(dv)

    def change_cursor(self, page_name: str) -> None:
        """
        Move cursor to button with given page name.
        
        Parameters
        ----------
        page_name
            Page name of the button to move the cursor to
        """

        prev_widget = self.__cursor_widget
        
        if prev_widget is None:
            prev_y = 0.0
        else:
            prev_y = prev_widget.y()

        self.__cursor_widget = self.page_buttons[page_name]
        curr_y = self.__cursor_widget.y()

        # Same widget, no need to play moving animation
        if self.__cursor_widget is prev_widget:
            return

        # If prev_y is 0, it means there has not been a previous widget
        # So just don't play the animation at all
        if prev_y == 0.0:
            self.__cursor_tween.value = curr_y
            self.update()
            return

        self.__cursor_tween = Tween(prev_y, curr_y)
        self.__cursor_tween.play(0.3, easing=Easing.EASE_OUT_CUBIC)

        self.update()

    def __home_clicked(self) -> None:
        if self.__open:
            self.__open = False
            self.__resize_tween.play(0.2, reverse=True, easing=Easing.EASE_IN_SINE)

        else:
            self.__open = True
            self.__resize_tween.play(0.2, easing=Easing.EASE_IN_SINE)

            for page_name in self.page_buttons:
                button = self.page_buttons[page_name]
                button.text = page_name

        self.update()

    def paintEvent(self, e) -> None:
        super().paintEvent(e)

        pt = QPainter(self)
        pt.setRenderHint(QPainter.RenderHint.Antialiasing, on=True)

        # Draw cursor
        if self.__cursor_widget is not None:
            y = self.__cursor_tween.value

            # Cursor properties
            # TODO: Perhaps make these adjustable?
            cursor_w = 8.5
            cursor_h = 20.0
            cursor_r = 4.0
            x = -cursor_w * 0.5

            y_offset = self.__cursor_widget.height() * 0.5 - cursor_h * 0.5

            path = QPainterPath()
            path.addRoundedRect(
                x, y + y_offset,
                cursor_w, cursor_h,
                cursor_r, cursor_r, Qt.SizeMode.AbsoluteSize
            )
            pt.fillPath(path, shared.theme.qcolor(shared.theme.palette.brand_primary))

        # Update resizing animation
        self.setFixedWidth(round(self.__resize_tween.value + self.padding * 2))

        for page_name in self.page_buttons:
            button = self.page_buttons[page_name]
            button.setFixedWidth(round(self.__resize_tween.value))

        if self.__resize_tween.is_started or self.__cursor_tween.is_started:
            self.update()

    def __resize_finished(self) -> None:
        if not self.__open:
            for page_name in self.page_buttons:
                button = self.page_buttons[page_name]
                button.text = ""