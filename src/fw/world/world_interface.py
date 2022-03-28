"""Tento modul obsahuje definici rozhraní světa, se kterým robot pomocí svých
jednotek interaguje.

Rozhraní světa je přidanou vrstvou mezi svět a mezi robota tak, aby bylo možné
zabezpečit svět před nepovolenými interakcemi, pro zajištění jeho integrity a
pro stanovení jednotného a snazšího rozhraní pro manipulaci se světem."""

# Import standardních knihoven


# Import lokálních knihoven
import src.fw.world.world as world_module
import src.fw.robot.interaction as interaction_module


class WorldInterface(interaction_module.InteractionHandlerManager):
    """Instance této třídy slouží jako jakási fasáda světa. Tato vrstva mezi
    světem a robotem (resp. jeho jednotkami) je navržena tak, aby zpracovávala
    interakce robota a propisovala je do světa, stejně jako o světě vracela
    požadované informace."""

    def __init__(self, world: "world_module.World"):
        """Initor třídy, který přijímá instanci světa, kterému náleží a se
        kterým bude tato komunikovat.
        """
        interaction_module.InteractionHandlerManager.__init__(self)
        self._world = world

    @property
    def world(self) -> "world_module.World":
        """Svět, kterému toto rozhraní náleží."""
        return self._world

    def process_interaction(
            self, interaction: "interaction_module.Interaction") -> object:
        """Funkce odpovědná za zprocesování požadované interakce na úrovni
        světa, resp. jeho rozhraní.
        """
        return self.get_interaction_handler(interaction).execute(
            interaction, self)







