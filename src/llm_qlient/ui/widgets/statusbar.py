"""

    llm-qlient • Qt desktop client for interacting with local LLMs

    This file is a part of the llm-qlient
    project and distributed under MIT license.

    Repository: https://github.com/kadir014/llm-qlient
    Issues:     https://github.com/kadir014/llm-qlient/issues

"""

from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot, QTimer, QThread
from PyQt6.QtWidgets import QWidget, QHBoxLayout
from PyQt6.QtGui import QIcon, QPainter, QPainterPath, QColor
from freshqt.core import TypographyType
from freshqt.widgets import Button, Divider, TypoLabel
from freshqt.animation import Tween, Easing

from llm_qlient import shared
from llm_qlient.core import log
from llm_qlient.core.types import SettingsDict
from llm_qlient.core.sysinfo import get_utilization_summary, UtilizationSummary


class UtilizationFetcher(QThread):

    new_data = pyqtSignal(UtilizationSummary, name="new_data")

    def __init__(self) -> None:
        super().__init__()

        self.should_run = True
        self.interval_sec = 2.0

    def run(self) -> None:
        log.info(f"<fg.blue>[Thrd#{int(self.currentThreadId())}]</> Utilization fetcher started")

        self.setPriority(QThread.Priority.LowestPriority)

        while self.should_run:
            if shared.settings["system_metrics_show"]:
                util = get_utilization_summary()
                self.new_data.emit(util)

            # Skip the sleep if we can break out of loop
            if not self.should_run:
                break

            # Sleep later so the first data is fetched instantly
            self.msleep(int(self.interval_sec * 1000))

        log.info(f"<fg.blue>[Thrd#{int(self.currentThreadId())}]</> Utilization fetcher finished")


class StatusBar(QWidget):
    def __init__(self) -> None:
        super().__init__()

        self.setFixedHeight(24)

        layout = QHBoxLayout()
        layout.setContentsMargins(10, 0, 10, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.setLayout(layout)

        self.page_name_lbl = TypoLabel(type=TypographyType.CAPTION)
        self.page_name_lbl.color = "text_secondary"
        shared.theme.add_widget(self.page_name_lbl)
        layout.addWidget(self.page_name_lbl)

        layout.addStretch()

        self.utilization_lbl = TypoLabel(type=TypographyType.CAPTION)
        self.utilization_lbl.color = "text_secondary"
        shared.theme.add_widget(self.utilization_lbl)
        layout.addWidget(self.utilization_lbl)

        self.util_thrd = UtilizationFetcher()
        self.util_thrd.new_data.connect(self._update_util_label)
        self.util_thrd.start()

        shared.settings.changed.connect(self._settings_changed)
        shared.cleanup.connect(self.cleanup)

    def cleanup(self) -> None:
        self.util_thrd.should_run = False
        self.util_thrd.wait(5000)

    @pyqtSlot(UtilizationSummary)
    def _update_util_label(self, util: UtilizationSummary) -> None:
        template = shared.settings["system_metrics_formatter"]

        render = template
        render = render.replace("{cpu}", str(round(util.cpu * 100.0, 1)))
        render = render.replace("{gpu}", str(round(util.gpu * 100.0, 1)))
        render = render.replace("{ram_total}", str(round(util.ram_total / 1073741824.0, 1)))
        render = render.replace("{ram_used}", str(round(util.ram_used / 1073741824.0, 1)))
        render = render.replace("{ram_percent}", str(round(util.ram_percent * 100.0, 1)))
        render = render.replace("{vram_total}", str(round(util.vram_total / 1073741824.0, 1)))
        render = render.replace("{vram_used}", str(round(util.vram_used / 1073741824.0, 1)))
        render = render.replace("{vram_percent}", str(round(util.vram_percent * 100.0, 1)))

        self.utilization_lbl.setText(render)

    def _settings_changed(self, changed: SettingsDict) -> None:
        if "system_metrics_show" in changed:
            self.utilization_lbl.setVisible(changed["system_metrics_show"])

        if "system_metrics_interval" in changed:
            self.util_thrd.interval_sec = float(changed["system_metrics_interval"])