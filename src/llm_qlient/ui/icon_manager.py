"""

    llm-qlient  -  Qt desktop client for interacting with local LLMs

    This file is a part of the llm-qlient
    project and distributed under MIT license.
    https://github.com/kadir014/llm-qlient

"""

from pathlib import Path

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QPainter, QColor, QPixmap
from freshqt.core import BaseIconManager

from llm_qlient.core import log


class IconManager(BaseIconManager):
    def __init__(self) -> None:
        self.__cache: dict[str, dict[tuple[int, int, int] | None, QIcon]] = {}

    def get(self, name: str, color: QColor | None = None) -> QIcon:
        if color is None:
            return self.__cache[name][None]

        rgb = (color.red(), color.green(), color.blue())
        hit = self.__cache[name]

        if rgb in hit:
            return hit[rgb]
        
        else:
            log.debug(f"No cache found for <fg.yellow>{name}</> <fg.darkgray>-></> ({rgb[0]}, {rgb[1]}, {rgb[2]}), caching...")
            colored = self.colorize_icon(hit[None], color)
            self.__cache[name][rgb] = colored
            return colored
        
    def load(self, path: Path) -> None:
        """ Load the icons in the given path. """

        for _, _, files in path.walk():
            for name in files:
                p = path / name

                icon_name = p.stem
                icon = QIcon(str(p.absolute()))
                self.__cache[icon_name] = {None: icon}
                log.info(f"Icon {icon_name} loaded at path '{p}'")

    @staticmethod
    def colorize_icon(icon: QIcon, color: QColor) -> QIcon:
        """
        Colorize an icon using its transparency as a mask.

        Note that this doesn't tint the hue, it paints all the visible pixels.

        Parameters
        ----------
        icon
            Source icon (unmodified)
        color
            Target color
        """

        fallback_size = QSize(256, 256)
        size = icon.actualSize(fallback_size)

        src = icon.pixmap(size)
        if src.isNull():
            return icon

        dst = QPixmap(src.size())
        dst.fill(Qt.GlobalColor.transparent)

        painter = QPainter(dst)

        # Original alpha mask
        painter.drawPixmap(0, 0, src)

        # Tint using alpha as mask
        painter.setCompositionMode(
            QPainter.CompositionMode.CompositionMode_SourceIn
        )
        painter.fillRect(dst.rect(), color)

        painter.end()
        return QIcon(dst)