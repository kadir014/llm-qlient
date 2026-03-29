"""

    llm-qlient • Qt desktop client for interacting with local LLMs

    This file is a part of the llm-qlient
    project and distributed under MIT license.

    Repository: https://github.com/kadir014/llm-qlient
    Issues:     https://github.com/kadir014/llm-qlient/issues

"""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLayout, QHBoxLayout
from freshqt.core import TypographyType
from freshqt.widgets import TypoLabel, BadgeLabel, Divider

from llm_qlient import shared


def hdivider(margin: int, layout: QLayout) -> TypoLabel:
    lbl = Divider(margin, orientation=Qt.Orientation.Horizontal)
    shared.theme.add_widget(lbl)
    layout.addWidget(lbl)
    return lbl

def vdivider(margin: int, layout: QLayout) -> TypoLabel:
    lbl = Divider(margin, orientation=Qt.Orientation.Vertical)
    shared.theme.add_widget(lbl)
    layout.addWidget(lbl)
    return lbl

def caption(text: str, layout: QLayout) -> TypoLabel:
    lbl = TypoLabel(text, TypographyType.CAPTION)
    shared.theme.add_widget(lbl)
    layout.addWidget(lbl)
    return lbl

def body(text: str, layout: QLayout) -> TypoLabel:
    lbl = TypoLabel(text, TypographyType.BODY)
    shared.theme.add_widget(lbl)
    layout.addWidget(lbl)
    return lbl

def h1(text: str, layout: QLayout) -> TypoLabel:
    lbl = TypoLabel(text, TypographyType.TITLE1)
    shared.theme.add_widget(lbl)
    layout.addWidget(lbl)
    return lbl

def h2(text: str, layout: QLayout) -> TypoLabel:
    lbl = TypoLabel(text, TypographyType.TITLE2)
    shared.theme.add_widget(lbl)
    layout.addWidget(lbl)
    return lbl

def h3(text: str, layout: QLayout) -> TypoLabel:
    lbl = TypoLabel(text, TypographyType.TITLE3)
    shared.theme.add_widget(lbl)
    layout.addWidget(lbl)
    return lbl

def info_label_pair(desc: str, info: str, layout: QLayout) -> BadgeLabel:
    pair_lyt = QHBoxLayout()
    pair_lyt.setContentsMargins(0, 0, 0, 0)
    pair_lyt.setAlignment(Qt.AlignmentFlag.AlignLeft)
    layout.addLayout(pair_lyt)

    desc_lbl = TypoLabel(desc)
    shared.theme.add_widget(desc_lbl)
    pair_lyt.addWidget(desc_lbl)

    info_lbl = BadgeLabel(info, color="brand_primary")
    shared.theme.add_widget(info_lbl)
    pair_lyt.addWidget(info_lbl)

    return info_lbl


__all__ = (
    "hdivider",
    "vdivider",
    "caption",
    "body",
    "h1",
    "h2",
    "h3",
    "info_label_pair"
)