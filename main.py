from src.fw.platform.platform import Platform
from src.fw.utils.loading.program_loader import DefaultProgramLoader
from src.fw.utils.loading.runtime_factory_loader import (
    DefaultRuntimeFactoryLoader)
from src.fw.utils.loading.unit_factory_loader import DefaultUnitFactoryLoader

import src.fw.target.results.html_results as html

from src.fw.gui.visualization import (build_graphical_interface, window_close,
                                      update_runtime)
import threading
import time


def _build_platform(assignment: str):
    platform = Platform(
        assignment,
        [DefaultUnitFactoryLoader()],
        [DefaultProgramLoader(assignment)],
        DefaultRuntimeFactoryLoader(assignment),
        update_runtime,
    )
    return platform


def _run_platform(platform: Platform):
    time.sleep(1)
    platform.load()
    platform.run()

    html.PlatformHTMLBuilder(platform).build()
    window_close()


assgn = "assignment_playground"
pltf = _build_platform(assgn)

platform_thread = threading.Thread(target=_run_platform, args=(pltf,))
platform_thread.setDaemon(True)
platform_thread.start()

build_graphical_interface(pltf)

