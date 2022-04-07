from src.fw.platform.platform import Platform
from src.fw.utils.loading.program_loader import DefaultProgramLoader
from src.fw.utils.loading.runtime_factory_loader import \
    DefaultRuntimeFactoryLoader
from src.fw.utils.loading.unit_factory_loader import DefaultUnitFactoryLoader


assignment = "assignment_playground"

platform = Platform(
    [DefaultUnitFactoryLoader()],
    [DefaultProgramLoader(assignment)],
    DefaultRuntimeFactoryLoader(assignment)
)

platform.load()
platform.run()