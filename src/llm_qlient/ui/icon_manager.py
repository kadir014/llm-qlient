"""

    llm-qlient • Qt desktop client for interacting with local LLMs

    This file is a part of the llm-qlient
    project and distributed under MIT license.

    Repository: https://github.com/kadir014/llm-qlient
    Issues:     https://github.com/kadir014/llm-qlient/issues

"""

from pathlib import Path

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QPainter, QColor, QPixmap
from freshqt.core import BaseIconManager

from llm_qlient.core import log
from llm_qlient.core.types import PathLike


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
        
    def load_single(self, path: PathLike) -> None:
        """ Load a single icon at given path. """

        path = Path(path)

        icon_name = path.stem
        icon = QIcon(str(path.absolute()))
        self.__cache[icon_name] = {None: icon}
        log.info(f"Icon <fg.yellow>{icon_name}</> loaded at path <fg.darkgray>'{path}'</>")
        
    def load(self, path: PathLike) -> None:
        """ Load all icons in the given directory path. """

        path = Path(path)

        if not path.is_dir():
            log.error(f"Given path <fg.yellow>{path}</> for IconManager.load is not a directory")
            return

        for _, _, files in path.walk():
            for name in files:
                self.load_single(path / name)

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