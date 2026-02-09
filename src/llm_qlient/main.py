"""

    llm-qlient  -  Qt desktop client for interacting with local LLMs

    This file is a part of the llm-qlient
    project and distributed under MIT license.
    https://github.com/kadir014/llm-qlient

"""

import sys
import platform
from datetime import datetime

from llm_qlient import shared
from llm_qlient.core import log
from llm_qlient.app import App


def log_diag() -> None:
    """
    Log system and platform specifications for debugging and diagnostics.
    """

    log.debug(datetime.today().strftime("Current system time: %d/%m/%Y, %H:%M:%S"))
    log.debug(f"Platform: {platform.platform()}")
    log.debug(f"Arch: {platform.machine()}")
    log.debug(f"Python: {platform.python_version()} {platform.python_compiler()}")


def main() -> None:
    """ Main entry point. """

    min_level = log.LogLevel.INFO
    if "--debug" in sys.argv:
        min_level = log.LogLevel.DEBUG

    log_file = open("llm-qlient.log", "w", encoding="utf-8")
    log.targets.add(log.LogTarget(sys.stdout, colored=True, min_level=min_level))
    log.targets.add(log.LogTarget(log_file, colored=False, min_level=min_level))

    log_diag()

    app = App()
    ret = app.run()
    log.debug(f"App return code: {hex(ret)}")

    shared.cleaner.cleanup()

    log_file.close()
    sys.exit(ret)


if __name__ == "__main__":
    main()