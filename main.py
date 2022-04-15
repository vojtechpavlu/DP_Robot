from src.fw.platform.platform import Platform
from src.fw.utils.loading.program_loader import DefaultProgramLoader
from src.fw.utils.loading.runtime_factory_loader import (
    DefaultRuntimeFactoryLoader)
from src.fw.utils.loading.unit_factory_loader import DefaultUnitFactoryLoader

import src.fw.target.results.html_results as html

assignment = "assignment_3_robots_units"

platform = Platform(
    [DefaultUnitFactoryLoader()],
    [DefaultProgramLoader(assignment)],
    DefaultRuntimeFactoryLoader(assignment)
)

platform.load()
platform.run()


html.PlatformHTMLBuilder(platform).build()
