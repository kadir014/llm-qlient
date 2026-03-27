"""

    llm-qlient • Qt desktop client for interacting with local LLMs

    This file is a part of the llm-qlient
    project and distributed under MIT license.

    Repository: https://github.com/kadir014/llm-qlient
    Issues:     https://github.com/kadir014/llm-qlient/issues

"""

from typing import Iterator

from PyQt6.QtWidgets import QWidget, QLayout, QSpacerItem, QWidgetItem

from llm_qlient import shared


def iter_widgets(layout: QLayout, object_name: str = "") -> Iterator[QWidget]:
    """
    Iterate over children widgets of a layout.

    Parameters
    ----------
    layout
        Layout to iterate over
    object_name
        Optional object name filter
    """

    for i in range(layout.count()):
        item = layout.itemAt(i)

        wdg = item.widget()

        if wdg is not None:
            if len(object_name) > 0 and wdg.objectName() != object_name:
                continue

            yield wdg


def recursive_clear(
        layout: QLayout,
        remove_layouts: bool = True,
        remove_widgets: bool = True,
        remove_items: bool = True
        ) -> None:
    """
    Clear out a layout recursively.

    Parameters
    ----------
    layout
        Layout to clear recursively
    remove_layouts
        Remove children layouts
    remove_widgets
        Remove children widgets
    remove_items
        Remove children spacer items
    """

    for i in reversed(range(layout.count())):
        item = layout.itemAt(i)
        if item is None:
            continue

        if remove_layouts:
            lyt = item.layout()
            if lyt is not None:
                recursive_clear(
                    lyt, remove_layouts, remove_widgets, remove_items
                )
                layout.removeItem(lyt)
                lyt.setParent(None)
                lyt.deleteLater()

        if remove_widgets and isinstance(item, QWidgetItem):
            wdg = item.widget()
            if wdg is not None:
                shared.theme.remove_widget(wdg, update=False)
                layout.removeWidget(wdg)
                wdg.setParent(None)
                wdg.deleteLater()

        if remove_items and isinstance(item, QSpacerItem):
            # TODO: This makes illegal memory access and crashes, what...
            #       (QWidgetItem -> spacerItem())
            s = item.spacerItem()
            if s is not None:
                layout.removeItem(s)