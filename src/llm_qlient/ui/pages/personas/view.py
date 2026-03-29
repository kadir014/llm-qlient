"""

    llm-qlient • Qt desktop client for interacting with local LLMs

    This file is a part of the llm-qlient
    project and distributed under MIT license.

    Repository: https://github.com/kadir014/llm-qlient
    Issues:     https://github.com/kadir014/llm-qlient/issues

"""

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QScrollArea,
    QSizePolicy
)
from PyQt6.QtGui import QPainter, QPainterPath, QPen
from freshqt.core import Theme, Themeable, TypographyType
from freshqt.widgets import Avatar, Button, LineEdit, TypoLabel

from llm_qlient import shared
from llm_qlient.core.models import UserPersona
from llm_qlient.ui.factories import *
from llm_qlient.ui.pages.base_view import BaseView
from llm_qlient.ui.widgets.auto_pair_editor import AutoPairEditor


class UserPersonaCard(QWidget, Themeable):
    """
    User persona card panel widget.
    """

    def __init__(self, persona: UserPersona) -> None:
        super().__init__()
        self._persona = persona

        layout = QHBoxLayout()
        layout.setContentsMargins(17, 17, 17, 17)
        self.setLayout(layout)

        self.avatar = Avatar(persona.avatar_pixmap)
        self.avatar.colorize = False
        self.avatar.setFixedSize(95, 95)
        self.avatar.radius = 7
        shared.theme.add_widget(self.avatar)
        layout.addWidget(self.avatar, alignment=Qt.AlignmentFlag.AlignTop)

        layout.addSpacing(7)

        # User persona information
        self.persona_info_lyt = QVBoxLayout()
        self.persona_info_lyt.setContentsMargins(0, 0, 0, 0)
        self.persona_info_lyt.setSpacing(15)
        self.persona_info_lyt.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addLayout(self.persona_info_lyt)

        self.ui_name_lbl = h3(persona.ui_name, self.persona_info_lyt)
        self.name_lbl = body(persona.name, self.persona_info_lyt)

        # User persona editing
        self.edit_fields: dict[str, list[QWidget]] = {}
        self.add_edit_field("Name", "name")
        self.add_edit_field("Avatar Path", "avatar_path")
        self.add_edit_field("Personality", "personality", multiline=True)

        # Interactions
        persona_interact_lyt = QVBoxLayout()
        persona_interact_lyt.setContentsMargins(0, 0, 0, 0)
        persona_interact_lyt.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addLayout(persona_interact_lyt)

        self.edit_btn = Button("Edit", icon_name="hi-pencil", variant=Button.Variant.OUTLINE)
        self.edit_btn.setMinimumWidth(85)
        self.edit_btn.setIconSize(QSize(20, 20))
        shared.theme.add_widget(self.edit_btn)
        persona_interact_lyt.addWidget(self.edit_btn, alignment=Qt.AlignmentFlag.AlignTop)
        self.edit_btn.clicked.connect(self._edit_btn_clicked)

        self.use_btn = Button("Use", icon_name="hi-user")
        self.use_btn.setMinimumWidth(85)
        self.use_btn.setIconSize(QSize(20, 20))
        self.use_btn.background_color = "brand_primary"
        shared.theme.add_widget(self.use_btn)
        persona_interact_lyt.addWidget(self.use_btn)
        self.use_btn.clicked.connect(self.use)

        self.set_use_button_state(not self.is_used)

        shared.persona_changed.connect(self._persona_changed)

        self.__edit_mode = None
        self.edit_mode = False

    @property
    def edit_mode(self) -> bool:
        """ Message editing mode. """
        return self.__edit_mode
    
    @edit_mode.setter
    def edit_mode(self, mode: bool) -> None:
        if mode == self.__edit_mode:
            return
        
        self.__edit_mode = mode

        if mode:
            self.ui_name_lbl.hide()
            self.name_lbl.hide()

            self.use_btn.hide()
            
            self.edit_btn.text = "Done"
            self.edit_btn.icon_name = "hi-check"
            self.edit_btn.background_color = "state_success"
            self.edit_btn.variant = Button.Variant.BRAND

            for wdgs in self.edit_fields.values():
                for w in wdgs:
                    w.show()
        
        else:
            self.ui_name_lbl.show()
            self.name_lbl.show()

            self.use_btn.show()

            self.edit_btn.text = "Edit"
            self.edit_btn.icon_name = "hi-pencil"
            self.edit_btn.background_color = "background_secondary"
            self.edit_btn.variant = Button.Variant.OUTLINE

            for wdgs in self.edit_fields.values():
                for w in wdgs:
                    w.hide()

    @property
    def is_used(self) -> None:
        """ Is this user persona the currently used one? """
        return self._persona is shared.personas[shared.current_persona_idx]
    
    def toggle_edit_mode(self) -> None:
        """ Toggle enable or disable message editing mode. """
        self.edit_mode = not self.edit_mode

    def use(self) -> None:
        """ Use this persona. """
        shared.current_persona_idx = shared.personas.index(self._persona)
        shared.persona_changed.emit()

        self.set_use_button_state(False)

        self.update()

    def set_use_button_state(self, state: bool) -> None:
        """ Set state of the use button. """
        
        if state:
            self.use_btn.variant = Button.Variant.BRAND
            self.use_btn.background_color = "brand_primary"
            self.use_btn.text = "Use"
            self.use_btn.icon_name = "hi-user"
        else:
            self.use_btn.variant = Button.Variant.GHOST
            self.use_btn.background_color = None
            self.use_btn.text = "In Use"
            self.use_btn.icon_name = "hi-check"

        self.use_btn.setEnabled(state)

    def add_edit_field(self,
            label: str,
            attr: str,
            multiline: bool = False
            ) -> None:
        """
        Add a new editable field for user persona model.
        
        Parameters
        ----------
        label
            Text content of label
        attr
            Attribute responding in dataclass model
        multiline
            Whether the editable field is multiline or not
        """

        field_lyt = QHBoxLayout()
        field_lyt.setContentsMargins(0, 0, 20, 0)
        self.persona_info_lyt.addLayout(field_lyt)

        content = getattr(self._persona, attr)

        lbl = TypoLabel(label, TypographyType.BODY)
        shared.theme.add_widget(lbl)
        field_lyt.addWidget(lbl, alignment=Qt.AlignmentFlag.AlignTop)

        if multiline:
            line = AutoPairEditor()
            line.setPlainText(content)
            line.setMinimumHeight(200)
            field_lyt.addWidget(line)
        else:
            line = LineEdit(content)
            shared.theme.add_widget(line)
            field_lyt.addWidget(line)

        line.setFixedWidth(520)

        self.edit_fields[attr] = (line, lbl)

    def _edit_btn_clicked(self) -> None:
        if self.edit_mode:
            for attr, wdgs in self.edit_fields.items():
                line = wdgs[0]

                if isinstance(line, LineEdit):
                    content = line.text()
                else:
                    content = line.toPlainText()

                setattr(self._persona, attr, content)

            self.name_lbl.setText(self._persona.name)

            shared.contents.save_user_personas()

        self.toggle_edit_mode()

    def _persona_changed(self) -> None:
        if self.is_used:
            return
    
        self.set_use_button_state(True)

        self.update()

    def update_theme(self, theme: Theme) -> None:
        font_size = int(round(theme.get_typo_size(TypographyType.BODY) * theme.font_scale))
        if font_size <= 0:
            font_size = 1

        self.setStyleSheet(f"""
            QPlainTextEdit {{
                font-family: {theme.font_family};
                font-size: {font_size}px;
                color: {theme.qss(theme.palette.text_primary)};
                background-color: {theme.qss(theme.palette.background_secondary)};
                border: 1px solid {theme.qss(theme.palette.text_tertiary)};
                border-radius: 10px;
                selection-background-color: {theme.qss(theme.palette.text_selection)};
                padding: 5px;
            }}
        """)

    def paintEvent(self, e) -> None:
        pt = QPainter(self)
        pt.setRenderHint(QPainter.RenderHint.Antialiasing, on=True)

        w, h = self.width(), self.height()
        border_r = 12

        clippath = QPainterPath()
        clippath.addRoundedRect(0, 0, w, h, border_r, border_r)
        pt.setClipPath(clippath)

        bg_color = shared.theme.qcolor(shared.theme.palette.background_tertiary)
        pt.fillRect(0, 0, w, h, bg_color)

        if self.is_used:
            pen = QPen(shared.theme.qcolor(shared.theme.palette.state_success))
            pen.setWidthF(3.5)
            pt.setPen(pen)
            pt.drawRoundedRect(0, 0, w, h, border_r, border_r)


class View(BaseView):
    """
    User persona browser user interface view.
    """

    def __init__(self) -> None:
        super().__init__()

        outer_layout = QVBoxLayout()
        outer_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(outer_layout)

        content = QWidget()
        content.setMaximumWidth(880)
        content.setMinimumWidth(620)

        content_scroller = QScrollArea()
        content_scroller.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        content_scroller.setWidget(content)
        content_scroller.setWidgetResizable(True)
        content_scroller.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        outer_layout.addWidget(content_scroller)

        content_scroller.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }
        """)

        content.setStyleSheet("background: transparent;")

        self.content_lyt = QVBoxLayout()
        self.content_lyt.setContentsMargins(0, 30, 0, 0)
        self.content_lyt.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.content_lyt.setSpacing(15)
        content.setLayout(self.content_lyt)

        h1("User Personas", self.content_lyt)

        self.content_lyt.addSpacing(25)

        self.load_cards()

        self.content_lyt.addSpacing(25)

        add_lyt = QHBoxLayout()
        add_lyt.setContentsMargins(0, 0, 0, 0)
        add_lyt.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.content_lyt.addLayout(add_lyt)

        self.add_input = LineEdit()
        self.add_input.setMaximumWidth(250)
        self.add_input.setPlaceholderText("UI name of your new user persona")
        
        shared.theme.add_widget(self.add_input)
        add_lyt.addWidget(self.add_input)

        self.add_button = Button(icon_name="hi-plus")
        self.add_button.background_color = "state_success"
        self.add_button.border_radius = -1.0
        self.add_button.setIconSize(QSize(22, 22))
        self.add_button.setFixedSize(35, 35)
        self.add_button.clicked.connect(self.new_card)

        shared.theme.add_widget(self.add_button)
        add_lyt.addWidget(self.add_button)

        disc_lbl = body(
            "'UI names' are different from actual names of cards, they are used as unique identifiers internally and NOT included in prompts.\nThus you can't change them after creating.",
            self.content_lyt
        )
        disc_lbl.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self.content_lyt.addSpacing(35)

    def load_cards(self) -> None:
        """ Load user persona card widgets from models. """

        for persona in shared.personas:
            card = UserPersonaCard(persona)
            shared.theme.add_widget(card)
            self.content_lyt.addWidget(card)

    def new_card(self) -> None:
        """ Add a new user persona card. """

        ui_name = self.add_input.text().strip()
        if len(ui_name) == 0:
            shared.toasts.error("Enter a UI name!")
            return

        self.add_input.clear()

        persona = UserPersona(ui_name, "User", "", "")
        persona.avatar_pixmap = shared.default_user_pixmap
        shared.personas.append(persona)
        shared.contents.save_user_personas()

        card = UserPersonaCard(persona)
        shared.theme.add_widget(card)
        self.content_lyt.insertWidget(self.content_lyt.count() - 4, card)