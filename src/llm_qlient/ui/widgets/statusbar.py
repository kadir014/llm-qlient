"""

    llm-qlient • Qt desktop client for interacting with local LLMs

    This file is a part of the llm-qlient
    project and distributed under MIT license.

    Repository: https://github.com/kadir014/llm-qlient
    Issues:     https://github.com/kadir014/llm-qlient/issues

"""

from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot, QThread, QTimer
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel
from freshqt.core import TypographyType
from freshqt.widgets import TypoLabel
from panllm import ChatChunk, GenerationStats

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

        layout.addSpacing(35)

        self.model_icon_lbl = QLabel()
        layout.addWidget(self.model_icon_lbl)
        self._last_model_state = None

        self.model_lbl = TypoLabel(type=TypographyType.CAPTION)
        self.model_lbl.color = "text_secondary"
        shared.theme.add_widget(self.model_lbl)
        layout.addWidget(self.model_lbl)

        self.stats_template = "{tokens} tokens generated in {elapsed:.2f}s  •  {tps:.2f} t/s"
        self.model_lbl.setText(self.stats_template.format(tokens=0, elapsed=0, tps=0))

        self.model_state_timer = QTimer()
        self.model_state_timer.timeout.connect(self._update_model_state)
        self.model_state_timer.start(300)

        shared.gen.generation_finished.connect(self._generation_finished)

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

    def set_model_state_icon(self, state: bool) -> None:
        """ Change the current model state icon. """

        if state:
            icon = shared.icons.get("hi-fire", shared.theme.palette.state_warning)
        else:
            icon = shared.icons.get("hi-pause-circle", shared.theme.palette.state_success)

        icon_size = 16
        self.model_icon_lbl.setPixmap(icon.pixmap(icon_size, icon_size))

    def set_model_state(self, stats: GenerationStats) -> None:
        """ Change the current model state text. """

        stats_str = self.stats_template.format(
            tokens=stats.tokens,
            elapsed=stats.elapsed,
            tps=stats.tokens_per_second
        )
        self.model_lbl.setText(stats_str)

    @pyqtSlot(str, ChatChunk, GenerationStats)
    def _generation_finished(self,
            mode: str,
            chunk: ChatChunk,
            stats: GenerationStats
            ) -> None:
        self.set_model_state(stats)

    def _update_model_state(self) -> None:
        if shared.gen.is_generating:
            stats = shared.gen.stats
            self.set_model_state(stats)

        if self._last_model_state != shared.gen.is_generating:
            self._last_model_state = shared.gen.is_generating

            self.set_model_state_icon(self._last_model_state)

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