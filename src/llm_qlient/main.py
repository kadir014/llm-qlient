"""

    llm-qlient  -  Qt desktop client for interacting with local LLMs

    This file is a part of the llm-qlient
    project and distributed under MIT license.
    https://github.com/kadir014/llm-qlient

"""

import sys

from llm_qlient.core import log
from llm_qlient.app import App


def main() -> None:
    log_file = open("llm-qlient.log", "w", encoding="utf-8")
    log.targets.add(log.LogTarget(sys.stdout, colored=True, min_level=log.LogLevel.DEBUG))
    log.targets.add(log.LogTarget(log_file, colored=False, min_level=log.LogLevel.DEBUG))

    app = App()
    ret = app.run()

    log_file.close()
    sys.exit(ret)


if __name__ == "__main__":
    main()