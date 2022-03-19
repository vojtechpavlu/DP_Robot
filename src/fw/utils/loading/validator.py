""""""

# Import standardních knihoven
from abc import ABC, abstractmethod

# Import lokálních knihoven
import src.fw.utils.loading.plugin as pl


class PluginValidator(ABC):
    """Validátor pluginů, který ověřuje, že dodané pluginy jsou skutečně
    dle dodaných pravidel validní a použitelné v daném kontextu."""

    @abstractmethod
    def is_valid_plugin(self, plugin: "pl.Plugin") -> bool:
        """Abstraktní funkce ověřuje, zda-li je dodaný plugin validní oproti
        pravidlům definovaným instancemi implementujícími tuto třídu."""









