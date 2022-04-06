"""Modul 'evaluation_function.py' obsahuje definici obecných evaluačních
funkcí.

Obsahuje tu nejobecnější definici, tedy abstraktní třídu EvaluationFunction,
dále definice spojkových funkcí (potomci třídy EvaluationFunctionJunction),
které se starají dle jejich implementace o vyhodnocování více evaluačních
funkcí zároveň, a konečně negaci - pro snazší použití evaluačních funkcí.
"""

# Import standardních knihoven
from abc import ABC, abstractmethod

# Import lokálních knihoven
from typing import Iterable

from src.fw.utils.error import PlatformError
from src.fw.utils.identifiable import Identifiable
from src.fw.utils.named import Named
from src.fw.target.event_handling import EventEmitter, Event

import src.fw.target.task as task_module
import src.fw.robot.robot as robot_module
import src.fw.target.event_handling as event_module
import src.fw.world.world_events as world_events
import src.fw.robot.robot_events as robot_events


class EvaluationFunction(Named, Identifiable, event_module.EventHandler):
    """Evaluační funkce slouží k vyhodnocení splnění daného úkolu.
    Tato abstraktní třída definuje obecný protokol pro takovou funkci.

    Kromě toho, že je tato abstraktní třída potomkem tříd Identifiable
    a Named, je také potomkem třídy EventHandler, která umožňuje této
    evaluační funkci naslouchat událostem ve sledovaných objektech."""

    def __init__(self, name: str):
        """Initor třídy, který přijímá člověku čitelný název evaluační
        funkce. Tento initor je odpovědný za iniciaci předků, tedy tříd
        Identifiable, Named a EventHandler.

        Kromě toho také deklaruje proměnnou pro úkol, kterému bude náležet.
        Ten je ovšem v momentě zpracování initoru neznámý; nastavován je až
        za běhu životního cyklu instance."""

        # Volání předků
        Identifiable.__init__(self)
        Named.__init__(self, name)
        event_module.EventHandler.__init__(self)

        """Úkol, ke kterému evaluační funkce náleží"""
        self._task: "task_module.Task" = None

    @property
    def task(self) -> "task_module.Task":
        """Vlastnost, která vrací referenci na úkol, ke kterému tato
        evaluační funkce náleží."""
        return self._task

    @task.setter
    def task(self, task: "task_module.Task"):
        """Vlastnost se pokusí nastavit dodaný úkol jako vlastníka této
        evaluační funkce.

        Tento dodaný úkol nesmí být None a stejně tak nesmí být již jednou
        jedna instance úkolu být této funkci přiřazena. V opačném případě
        je vyhozena příslušná výjimka.
        """
        if task is None:
            raise EvaluationFunctionError(f"Dodaný úkol nesmí být None", self)
        elif self.task is not None:
            raise EvaluationFunctionError(
                f"Úkol nelze znovu přenastavovat", self)
        self._task = task

    @abstractmethod
    def eval(self) -> bool:
        """Jádrem evaluační funkce je právě tato metoda, která umožňuje
        vyhodnocení splnění stanoveného úkolu."""

    @abstractmethod
    def configure(self):
        """Abstraktní funkce, která umožňuje provedení konfigurace. Typicky
        je tato funkce volána teprve až v situaci, kdy jsou všechny prostředky
        stanoveny a lze tedy tuto evaluační funkci napojit."""


class EvaluationFunctionJunction(EvaluationFunction):
    """Spojka evaluačních funkcí slouží jako společný předek všem typům
    evaluačních funkcí, které se sestávají z vyhodnocování více funkcí
    najednou. Zároveň instance této třídy vystupují v roli evaluační funkce
    jako takové, jde totiž o potomka třídy 'EvaluationFunction'."""

    def __init__(self, name: str):
        """Jednoduchý initor spojky evaluačních funkcí"""
        EvaluationFunction.__init__(self, name)
        self._eval_funcs: "list[EvaluationFunction]" = []

    @property
    def evaluation_functions(self) -> "tuple[EvaluationFunction]":
        """Vlastnost vrací ntici evaluačních funkcí, ze kterých se spojka
        skládá."""
        return tuple(self._eval_funcs)

    def add_eval_func(self, fun: "EvaluationFunction"):
        """Metoda umožňující dynamicky přidávat instance evaluačních funkcí
        do této instance."""
        self._eval_funcs.append(fun)

    def update(self, emitter: "EventEmitter", event: "Event"):
        """Funkce je odpovědná za postoupení události všem svým evaluačním
        funkcím, které tato sdružuje.
        """
        for evaluation_function in self.evaluation_functions:
            evaluation_function.update(emitter, event)

    def configure(self):
        """Tato funkce pouze zavolá konfigurační proceduru nad všemi svými
        evaluačními funkcemi."""
        for eval_fun in self.evaluation_functions:
            eval_fun.configure()


class Conjunction(EvaluationFunctionJunction):
    """Instance třídy 'Conjunction' slouží k zpracovávání více evaluačních
    funkcí najednou, přičemž všechny musí být splněny, aby i tato vracela
    hodnotu o splnění."""

    def __init__(self, name: str):
        """Initor třídy, který pouze postupuje dodaný název svému předkovi."""
        EvaluationFunctionJunction.__init__(self, name)

    def eval(self) -> bool:
        """Jádro spojené evaluační funkce, které prochází všechny spojované.
        Je-li jediná nepravdivá, je vráceno (po vzoru konjunkce) False, jinak
        je vrácena hodnota True."""
        for ef in self.evaluation_functions:
            if not ef.eval():
                return False
        return True


class Disjunction(EvaluationFunctionJunction):
    """Instance třídy 'Disjunction' slouží k zpracovávání více evaluačních
    funkcí najednou, přičemž stačí, aby byla splněna jen jediná, aby i tato
    vracela hodnotu o splnění."""

    def __init__(self, name: str):
        """"""
        EvaluationFunctionJunction.__init__(self, name)

    def eval(self) -> bool:
        """Jádro spojené evaluační funkce, které prochází všechny spojované.
        Je-li jediná pravdivá, je vráceno (po vzoru disjunkce) True, jinak
        je vrácena hodnota False."""
        if len(self.evaluation_functions) == 0:
            return True
        for ef in self.evaluation_functions:
            if ef.eval():
                return True
        return False


class Negation(EvaluationFunction):
    """Instance třídy Negation má za cíl převracet hodnotu vložené evaluační
    funkce."""

    def __init__(self, name: str, ef: "EvaluationFunction"):
        """Initor třídy, který je odpovědná za postoupení názvu evaluační
        funkce svému předkovi, stejně jako je odpovědný za uložení reference
        na vyhodnocovací funkci, jejíž hodnotu bude negovat."""

        # Volání předka
        EvaluationFunction.__init__(self, name)

        """Vyhodnocovací funkce, jejíž hodnotu bude tato instance vracet 
        znegovanou"""
        self._eval_fun = ef

    @property
    def evaluation_function(self) -> "EvaluationFunction":
        """Vlastnost vrací evaluační funkci, jejíž hodnotu tato instance
        obrací."""
        return self._eval_fun

    def eval(self) -> bool:
        """Vrací převrácenou hodnotu vnitřní evaluační funkce."""
        return not self.evaluation_function.eval()


class EvaluationFunctionError(PlatformError):
    """Tato výjimka symbolizuje chyby, které můžou nastat v kontextu
    vyhodnocovacích funkcí. Svého předka rozšiřuje o referenci na evaluační
    funkci, v jejímž kontextu došlo k chybě."""

    def __init__(self, message: str, eval_fun: "EvaluationFunction"):
        """Initor, který postupuje zprávu o chybě svému předkovi a ukládá
        referenci na evaluační funkci, jejímž kontextu došlo k chybě.
        """

        # Volání předka
        PlatformError.__init__(self, message)

        # Evaluační funkce, v jejímž kontextu došlo k chybě
        self._eval_fun = eval_fun

    @property
    def evaluation_function(self) -> "EvaluationFunction":
        """Vlastnost vrací referenci na evaluační funkci, v jejímž kontextu
        došlo k chybě."""
        return self._eval_fun


class AlwaysTrueEvaluationFunction(EvaluationFunction):
    """Tato třída reprezentuje vyhodnocovací funkci, která je za všech
    okolností pravdivá. V praxi to znamená, že nic fakticky nevyhodnocuje,
    na požádání o vyhodnocení automaticky vrací hodnotu True.

    Instance této třídy se vlastně nemusí ani registrovat u žádné instance
    třídy 'EventEmitter', neboť de facto nic nevyhodnocují a není tedy třeba
    ani žádného ověřování."""

    def __init__(self):
        """Jednoduchý initor třídy, který pouze iniciuje předka s defaultním
        názvem evaluační funkce."""
        EvaluationFunction.__init__(self, "Always True")

    def eval(self) -> bool:
        """Funkce, jejímž cílem je vždy vrátit jen a pouze hodnotu True."""
        return True

    def update(self, emitter: "EventEmitter", event: "Event"):
        """Elementární implementace funkce 'update' pro funkci vždy pravdu
        vracející. De facto není třeba cokoliv vyhodnocovat a tedy ani
        ověřovat."""
        pass

    def configure(self):
        """Tato funkce není v případě této implementace potřeba."""
        pass


class AlwaysFalseEvaluationFunction(EvaluationFunction):
    """Tato třída reprezentuje vyhodnocovací funkci, která je za všech
    okolností nepravdivá. V praxi to znamená, že nic fakticky nevyhodnocuje,
    na požádání o vyhodnocení automaticky vrací hodnotu False.

    Instance této třídy se vlastně nemusí ani registrovat u žádné instance
    třídy 'EventEmitter', neboť de facto nic nevyhodnocují a není tedy třeba
    ani žádného ověřování."""

    def __init__(self):
        """Jednoduchý initor třídy, který pouze iniciuje předka s defaultním
        názvem evaluační funkce."""
        EvaluationFunction.__init__(self, "Always False")

    def eval(self) -> bool:
        """Funkce, jejímž cílem je vždy vrátit jen a pouze hodnotu False."""
        return True

    def update(self, emitter: "EventEmitter", event: "Event"):
        """Elementární implementace funkce 'update' pro funkci vždy nepravdu
        vracející. De facto není třeba cokoliv vyhodnocovat a tedy ani
        ověřovat."""
        pass

    def configure(self):
        """Tato funkce není v případě této implementace potřeba."""
        pass


class Visited(EvaluationFunction):
    """Tato vyhodnocovací funkce má za cíl umožnit zaznamenávat, zda bylo
    políčko s danými souřadnicemi navštíveno či nikoliv.

    K tomu z titulu dědění z 'EventHandler' protokolu přijímá v rámci
    parametrů metody 'update(EventEmitter, Event)' událost, ke které
    došlo. Jde-li o událost přesunu robota na jiné políčko, je ověřeno,
    zda souřadnice neodpovídají těm, které jsou stanoveny ke sledování.
    """

    def __init__(self, x: int, y: int):
        """Initor, který přijímá souřadnice políčka, které se má sledovat.
        """

        # Volání předka
        EvaluationFunction.__init__(self, f"Visited ({x}, {y})")

        # Uložení souřadnic
        self._x = x
        self._y = y

        # Defaultní nastavení, zda políčko bylo či nebylo navštíveno
        self._visited = False

    @property
    def x(self) -> int:
        """Vlastnost vrací souřadnici x, která odpovídá sledovanému políčku.
        """
        return self._x

    @property
    def y(self) -> int:
        """Vlastnost vrací souřadnici y, která odpovídá sledovanému políčku.
        """
        return self._y

    @property
    def xy(self) -> "tuple[int, int]":
        """Vlastnost vrací sledované souřadnice v ntici."""
        return self._x, self._y,

    def eval(self) -> bool:
        """Funkce vyhodnocuje, zda-li políčko bylo či nebylo navštíveno.
        Pokud ano, vrací True, pokud ne, vrací False."""
        return self._visited

    def update(self, emitter: "EventEmitter", event: "Event"):
        """Funkce naslouchání událostem. Naplnění této evaluační funkce je
        stanoveno hned v několika možných situacích:

            - Když se robot přesune na sledované políčko
            - Když je na dané políčko robot zasazen
        """
        if (isinstance(event, world_events.FieldChangeEvent) or
                isinstance(event, world_events.SpawnRobotEvent)):

            if (event.x == self.x) and (event.y == self.y):
                self._visited = True
                emitter.unregister_event_handler(self)

    def configure(self):
        """Tato funkce není v případě této implementace potřeba."""
        pass


class VisitAllEvaluationFunction(Conjunction):
    """Evaluační funkce tohoto typu je odpovědná za naslouchání navštívení
    všech navštivitelných políček v dodaném světě.

    Tedy jde o konjunkci evaluačních funkcí, které čekají na událost
    navštívení jimi sledovaného políčka."""

    def __init__(self):
        """Jednoduchý bezparametrický initor, který pouze iniciuje předka."""
        Conjunction.__init__(self, "VisitAllEvaluationFunction")

    def configure(self):
        """Funkce se pokusí napojit pro každé navštivitelné políčko svoji
        evaluační funkci očekávající navštívění.

        Celý proces probíhá tak, že si funkce vyžádá z instance světa všechny
        cesty (políčka, které lze navštívit) a pro souřadnice každé této cesty
        si vytvoří jednu evaluační funkci čekající na událost značící návštěvu
        tohoto políčka.

        Poté tato funkce zaregistruje každou tuto evaluační funkci k
        příslušným emitorům událostí - tam, kde vznikají změny v kontextu
        změny pozice, tedy především stav robotů."""

        # Získání reference na svět, který má být sledován
        world = self.task.target.world

        # Pro každou cestu připoj jednu evaluační funkci
        for path in world.all_paths:
            ef = Visited(path.x, path.y)
            self.add_eval_func(ef)

            # Registrace dané evaluační funkce u všech důležitých
            # emitorů událostí
            world.world_interface.register_event_handler(ef)
            world.robot_state_manager.register_event_handler(ef)


class VisitSpecificFieldEvaluationFunction(Conjunction):
    """Evaluační funkce tohoto typu je konjunkcí evaluačních funkcí, které
    čekají na navštívení políčka na konkrétních souřadnicích."""

    def __init__(self, to_visit: "Iterable[Iterable[int, int]]"):
        """Initor, který přijímá iterovatelnou množinu souřadnic políček,
        ke kterým má být nasloucháno co do navštívení. robotem.

        Tato množina má požadovaný tvar Iterable[Iterable[int, int]]. Pokud
        nebude tento dodržen, je vyhozena výjimka.
        """
        # Volání předka
        Conjunction.__init__(self, "VisitSpecificFieldEvaluationFunction")

        # Pokud není Iterable
        if not isinstance(to_visit, Iterable):
            raise EvaluationFunctionError(
                f"Dodaná množina políček není v definovaném formátu", self)

        # Pokud je Iterable[Iterable]
        elif all(isinstance(subtuple, Iterable) for subtuple in to_visit):
            self._to_visit: "tuple[tuple[int, int]]" = tuple(
                map(lambda subtuple: tuple(subtuple), to_visit))

        # Je Iterable, ale není Iterable[Iterable]
        else:
            raise EvaluationFunctionError(
                f"Dodaná políčka nejsou v požadovaném formátu", self)

    @property
    def to_visit(self) -> "tuple[tuple[int, int]]":
        """Vlastnost vrací ntici dvojic souřadnic uspořádaných do ntice."""
        return self._to_visit

    def configure(self):
        """Funkce se stará o konfiguraci, tedy doplnění této instance o
        jednotlivé evaluační funkce odpovědné za kontrolu navštívění daného
        políčka."""

        # Získání reference na svět, který má být vrácen
        world = self.task.target.world

        # Pro každou dodanou kombinaci souřadnic
        for coords in self.to_visit:

            # Kontrola, že jsou dodané souřadnice ve správném formátu
            if len(coords) != 2:
                raise EvaluationFunctionError(
                    f"Dodané souřadnice nejsou platné: '{coords}'", self)

            # Kontrola, že políčko existuje
            elif not world.has_field(coords[0], coords[1]):
                raise EvaluationFunctionError(
                    f"Dodané souřadnice neukazují na "
                    f"platné políčko: {coords}", self)

            # Uložení existující políčka světa
            field = world.field(*coords)

            # Kontrola, že je políčko cestou (tedy navštivitelné políčko)
            if not field.is_path:
                raise EvaluationFunctionError(
                    f"Políčko na souřadnicích '{coords}' není cesta a nejde "
                    f"tedy navštívit", self)

            # Evidence nové evaluační funkce
            ef = Visited(*coords)
            self.add_eval_func(ef)

            # Registrace u možných instancí EventEmitter
            world.world_interface.register_event_handler(ef)
            world.robot_state_manager.register_event_handler(ef)


class UsedInteraction(EvaluationFunction):
    """Tato evaluační funkce čeká na události z kontextu aplikace interakcí.
    Evaluační funkce vrací svůj stav, tedy byla-li interakce zadaného názvu
    aplikována či nikoliv. Svůj stav pak mění v závislosti na událostech,
    které nastaly. Pokud """

    def __init__(self, interaction_name: str):
        """Initor třídy, který přijímá v parametru název interakce, na který
        má tato evaluační funkce reagovat.

        Pokud v tato funkce v rámci reakce na příslušnou událost (v metodě
        'update') rozpozná aplikaci interakce s tímto názvem, změní tato
        instance stav a bude na zavolání metody 'eval' vracet True.
        """
        # Volání předka
        EvaluationFunction.__init__(
            self, f"UsedInteraction '{interaction_name}'")

        # Uložení očekávaného názvu interakce
        self._interaction_name = interaction_name

        # Iniciace negativního stavu; potvrzení použití interakce se
        # ověřuje teprve v metodě 'update'
        self._used_interaction: bool = False

    @property
    def interaction_name(self) -> str:
        """Vlastnost vrací název interakce, na jejíž aplikaci se čeká."""
        return self._interaction_name

    def eval(self) -> bool:
        """Jednoduchá evaluace, zda bylo či nebylo evidováno použití interakce
        daného názvu."""
        return self._used_interaction

    def configure(self):
        """Konfigurace je v případě této evaluační funkce irelevantní."""
        pass

    def update(self, emitter: "EventEmitter", event: "Event"):
        """Tato funkce je odpovědná za kontrolu dodané události, zda-li je
        či není tou ze sledovaného kontextu. Pokud je, je dále zpracovávána.

        Pokud jde o událost pro tuto třídu relevantní (instanci typu
        'InteractionUsageEvent', je dále kontrolována interakce, zda svým
        názvem odpovídá té očekávané.
        """
        # Pokud jde o událost z tohoto kontextu
        if isinstance(event, robot_events.InteractionUsageEvent):

            # Pokud je název interakce tím očekávaným
            if event.interaction.name == self.interaction_name:

                # Změna stavu a odregistrování se; úkol je splněn
                self._used_interaction = True
                emitter.unregister_event_handler(self)


class UsedAllInteractions(Conjunction):
    """Tato evaluační funkce je konjunkčním agregátem, který přijímá názvy
    interakcí, přičemž cílem je zkontrolovat, že budou použity všechny. Tato
    třída (resp. její instance) pak mají schopnost toto kontrolovat.
    """

    def __init__(self, interaction_names: "Iterable[str]"):
        """Initor, který přijímá názvy interakcí, které mají být ověřeny co
        do jejich použití.

        Ty jsou přijaty v jakékoliv iterovatelné kolekci, typicky ntice.
        """

        # Iniciace předka
        Conjunction.__init__(self, "UsedAllInteractions")

        # Uložení všech požadovaných názvů
        self._names = interaction_names

    @property
    def interaction_names(self) -> "tuple[str]":
        """Vlastnost vrací množinu názvů interakcí, které mají být
        kontrolovány co do jejich použití."""
        return tuple(self._names)

    def configure(self):
        """Konfigurační metoda, která je odpovědná za připravení svých
        sub-evaluačních funkcí; pro každý dodaný název jedna.
        """

        # Získání reference na svět
        world = self.task.target.world

        # Pro každý název interakce
        for inter_name in self.interaction_names:

            # Vytvoření evaluační funkce a přidání do evidence
            ef = UsedInteraction(inter_name)
            self.add_eval_func(ef)

            # Registrace evaluační funkce u rozhraní světa
            world.world_interface.register_event_handler(ef)


class IsRobotMountedWith(EvaluationFunction):
    """Tato evaluační funkce je odpovědná za ověření, že je robot osazen
    jednotkou daného názvu.

    Pokud ano, je metodou 'eval' vrácena hodnota True, jinak False.
    """

    def __init__(self, unit_name: str, robot: "robot_module.Robot"):
        """Initor třídy, který přijímá v parametrech název jednotky, který
        je sledován co do osazení, a instanci robota, který má být co do
        osazení sledován.
        """

        # Volání initoru předka
        EvaluationFunction.__init__(
            self, f"IsMountedWith '{unit_name}'")

        # Uložení dodaných parametrů
        self._unit_name = unit_name
        self._robot: "robot_module.Robot" = robot

    def eval(self) -> bool:
        """Evaluační funkce, která má za cíl vyhodnotit, zda-li je stanovený
        robot osazen příslušnou jednotkou."""
        return self._unit_name in self._robot.unit_names

    def configure(self):
        """Konfigurační metoda zde nemá smysl."""
        pass

    def update(self, emitter: "EventEmitter", event: "Event"):
        """Metoda změny stavu zde nemá smysl."""
        pass


class IsRobotMountedWithAll(Conjunction):
    """"""

    def __init__(self, unit_names: "Iterable[str]"):
        """"""
        Conjunction.__init__(self, "IsRobotMountedWithAll")
        self._unit_names = tuple(unit_names)

    @property
    def unit_names(self) -> "tuple[str]":
        """"""
        return self._unit_names

    def configure(self):
        """"""

        # Získání reference na instanci světa
        world = self.task.target.world

        # Pro každý stav robota
        for robot_state in world.robot_state_manager.robot_states:

            # Pro každý název jednotky
            for unit_name in self._unit_names:

                # Přidání nové evaluační funkce
                self.add_eval_func(IsRobotMountedWith(
                    unit_name, robot_state.robot))












