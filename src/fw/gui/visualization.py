"""Tento modul sdružuje funkcionalitu grafického rozhraní. A to na úrovni
vybudování GUI, tak na úrovni zpracování událostí z jiných vláken."""

# Import standardních knihoven
import tkinter as tk

# Import lokálních knihoven
import src.fw.platform.platform as platform_module


# Definice základních proměnných

"""Definice barvy, která bude na pozadí. Bude viditelná pouze tam, kde políčko
chybí a ve světě je díra."""
_BACKGROUND_COLOUR = "bisque"

"""Definice barvy, která bude reprezentovat políčko typu cesta."""
_PATH_COLOUR = "bisque"

"""Definice barvy, která bude reprezentovat políčko typu stěna."""
_WALL_COLOUR = "grey4"

"""Definice barvy, kterou je políčko ohraničeno."""
_OUTLINE_COLOUR = "gold"

"""Definice barvy, kterou má robot"""
_ROBOT_COLOUR = "red"

"""Definice barvy, kterou má mít značka"""
_MARK_COLOUR = "cyan"

"""Definice velikosti políčka"""
_FIELD_W = 25
_FIELD_H = 25

"""Text značící nedostupnost (Not Available; defaultně 'N/A')."""
_NOT_AVAILABLE = "N/A"


def east_robot_polygon(x_indent, y_indent):
    """Funkce pro vygenerování souřadnic polygonu, který reprezentuje
    robota otočeného na východ.

    Přijímá k tomu odsazení v ose x a v ose y. Tím je specifikován levý
    horní roh políčka."""
    return (
        x_indent + _FIELD_W, y_indent + (_FIELD_H * 0.5),
        x_indent + 0, y_indent + _FIELD_H,
        x_indent + (_FIELD_W * 0.25), y_indent + (_FIELD_H * 0.5),
        x_indent + 0, y_indent + 0
    )


def north_robot_polygon(x_indent, y_indent):
    """Funkce pro vygenerování souřadnic polygonu, který reprezentuje
    robota otočeného na sever.

    Přijímá k tomu odsazení v ose x a v ose y. Tím je specifikován levý
    horní roh políčka."""
    return (
        x_indent + (_FIELD_W * 0.5), y_indent + 0,
        x_indent + _FIELD_W, y_indent + _FIELD_H,
        x_indent + (_FIELD_W * 0.5), y_indent + (_FIELD_H * 0.75),
        x_indent + 0, y_indent + _FIELD_H
    )


def west_robot_polygon(x_indent, y_indent):
    """Funkce pro vygenerování souřadnic polygonu, který reprezentuje
    robota otočeného na západ.

    Přijímá k tomu odsazení v ose x a v ose y. Tím je specifikován levý
    horní roh políčka."""
    return (
        x_indent + 0, y_indent + (_FIELD_H * 0.5),
        x_indent + _FIELD_W, y_indent + 0,
        x_indent + (_FIELD_W * 0.75), y_indent + (_FIELD_H * 0.5),
        x_indent + _FIELD_W, y_indent + _FIELD_H
    )


def south_robot_polygon(x_indent, y_indent):
    """Funkce pro vygenerování souřadnic polygonu, který reprezentuje
    robota otočeného na jih.

    Přijímá k tomu odsazení v ose x a v ose y. Tím je specifikován levý
    horní roh políčka."""
    return (
        x_indent + (_FIELD_W * 0.5), y_indent + _FIELD_H,
        x_indent + 0, y_indent + 0,
        x_indent + (_FIELD_W * 0.5), y_indent + (_FIELD_H * 0.25),
        x_indent + _FIELD_W, y_indent + 0
    )


def resolve_robot_polygon(rs, x_indent, y_indent):
    """Funkce pro vybrání správného polygonu robota. K tomu potřebuje
    znát stav robota ('RobotState'), ze kterého zjistí směr natočení
    robota.
    Dále vyžaduje odsazení v ose x a v ose y, která reprezentují levý
    horní roh políčka, na kterém robot stojí."""

    dn = rs.direction.name
    if dn == "EAST":
        return east_robot_polygon(x_indent, y_indent)
    elif dn == "NORTH":
        return north_robot_polygon(x_indent, y_indent)
    elif dn == "WEST":
        return west_robot_polygon(x_indent, y_indent)
    elif dn == "SOUTH":
        return south_robot_polygon(x_indent, y_indent)


class Component:
    """Jednoduchý společný předek pro hlavní komponentové celky.
    Tento uchovává referenci na grafické rozhraní a na frame, ve kterém
    je komponenta vykreslena."""

    def __init__(self, gui: "GraphicalInterface", global_frame: tk.LabelFrame):
        """Initor, který přijímá referenci na grafické rozhraní, pro které
        má být komponenta vykreslena, a frame, do kterého je tato vykreslena.
        """
        self._global_frame = global_frame
        self._gui = gui

    @property
    def global_frame(self) -> tk.LabelFrame:
        """Vlastnost vrací Frame, v rámci kterého je tato komponenta
        vykreslena."""
        return self._global_frame

    @property
    def gui(self) -> "GraphicalInterface":
        """Vlastnost vrací referenci na nejvyšší úroveň GUI (root) obalenou
        v instanci třídy GraphicalInterface."""
        return self._gui


class WorldVisualization(Component):
    """Instance této třídy jsou vizualizací světa. Jejím cílem je řízení
    vykreslování aktuálního stavu světa na plátno."""

    def __init__(self, gui: "GraphicalInterface", global_frame: tk.LabelFrame):
        # Volání předka
        Component.__init__(self, gui, global_frame)

        # Nastavení hlavního frame
        self._frame = tk.LabelFrame(global_frame, text="Aktuální svět",
                                    padx=5, pady=5)
        self._frame.grid(row=0, column=1)

        # Nastavení plátna
        self._canvas = tk.Canvas(self.frame, width=_FIELD_W, height=_FIELD_H,
                                 bg=_BACKGROUND_COLOUR)
        self._canvas.pack()

        self._robot_vis = []
        self._marks = []

    @property
    def frame(self) -> tk.LabelFrame:
        """Vlastnost vrací rámec, který obsahuje plátno."""
        return self._frame

    @property
    def canvas(self) -> tk.Canvas:
        """Vlastnost vrací plátno, do kterého je obraz světa kreslen."""
        return self._canvas

    def redraw(self):
        """Funkce starající se o překreslení celého plátna."""
        # Odstranění plátna
        self.canvas.delete("all")
        self.canvas.destroy()

        # Pomocné přístupové proměnné
        runtime = self.gui.platform.current_runtime
        world = runtime.world
        width = world.width
        height = world.height

        # Inicializace nového plátna a jeho vykreslení do rámce
        self._canvas = tk.Canvas(self.frame, width=width*_FIELD_W,
                                 height=height*_FIELD_H, bg=_BACKGROUND_COLOUR)
        self._canvas.pack()

        # Získání minimálních hodnot políček, která definují odsazení
        min_x = min(world.fields, key=lambda f: f.x).x
        min_y = min(world.fields, key=lambda f: f.y).y

        # Pro každé políčko světa
        for field in world.fields:

            # Rozlišení barvy stěny a cesty
            colour = _PATH_COLOUR if field.is_path else _WALL_COLOUR

            # Vykreslení daného políčka
            self._draw_field(field.x - min_x, field.y - min_y, colour, height)

        # Překreslení značek a robotů
        self.redraw_marks()
        self.redraw_robots()

    def _draw_field(self, x: int, y: int, colour: str, height: int):
        """Funkce starající se o vykreslení daného políčka na plátno."""
        w = _FIELD_W
        h = _FIELD_H
        self.canvas.create_rectangle(
            x * w,                       # Stanovení šířky horního levého rohu
            (height - y - 1) * h,        # Stanovení výšky horního levého rohu
            (x * w) + w,                 # Stanovení šířky dolního pravého rohu
            ((height - y - 1) * h) + h,  # Stanovení výšky dolního pravého rohu
            fill=colour,                 # Stanovení barvy výplně políčka
            outline=_OUTLINE_COLOUR      # Stanovení barvy ohraničení políčka
        )

    def redraw_marks(self):
        """Funkce starající se o překreslení všech značek, které jsou na
        jednotlivých políčcích světa."""

        # Pokud jsou doposud nějaké vykreslené, smaž je
        if len(self._marks) > 0:
            for m in self._marks:
                self.canvas.delete(m)
        self._marks = []

        # Získání reference na aktuální svět
        world = self.gui.platform.current_runtime.world

        # Získání minimálních hodnot souřadnic políček
        min_x = min(world.fields, key=lambda f: f.x).x
        min_y = min(world.fields, key=lambda f: f.y).y

        # Pro všechna políčka světa
        for field in world.fields:

            # Pokud má značku, vykresli ji
            if field.has_mark:
                self._draw_mark(
                    (field.x - min_x)*_FIELD_W,
                    (world.height - (field.y - min_y + 1)) * _FIELD_H)

    def _draw_mark(self, x_indent: int, y_indent: int):
        """Funkce se stará o vykreslení značky v daném políčku.

        V parametru přijímá odsazení políčka v osách x a y. Tím je definován
        horní levý roh políčka v rámci vizualizace světa."""

        # Šířka a výška značky
        width = int(_FIELD_W * 0.25)
        height = int(_FIELD_H * 0.25)

        # Odsazení od okrajů políčka
        indent = int(_FIELD_W * 0.1)

        # Vykreslení značky
        self.canvas.create_rectangle(
            x_indent + _FIELD_W - (width + indent),
            y_indent + indent,
            x_indent + _FIELD_W - indent,
            y_indent + height + indent,
            fill=_MARK_COLOUR
        )

    def redraw_robots(self):
        """Funkce, která se stará o překreslení robotů světa."""

        # Pokud je počet evidovaných robotů ve světě > 0, vymaž vizualizace
        if len(self._robot_vis) > 0:
            for robot in self._robot_vis:
                self.canvas.delete(robot)
        self._robot_vis = []

        # Získání referencí na svět a správce stavů robota
        world = self.gui.platform.current_runtime.world
        rs_m = world.robot_state_manager

        # Získání minimálních a maximálních hodnot souřadnic políček
        min_x = min(world.fields, key=lambda f: f.x).x
        min_y = min(world.fields, key=lambda f: f.y).y
        max_y = max(world.fields, key=lambda f: f.y).y

        # Pro každý stav robota
        for rs in rs_m.robot_states:

            # Vytvoř si odsazení v ose x a y pro stanovení hroního levého rohu
            x_indent = (rs.field.x - min_x) * _FIELD_W
            y_indent = (max_y - rs.field.y - min_y) * _FIELD_H

            # Eviduj nově vytvořený obrazec reprezentující robota
            self._robot_vis.append(self.canvas.create_polygon(
                resolve_robot_polygon(rs, x_indent, y_indent),
                fill=_ROBOT_COLOUR, outline="black"))


class RuntimeVisualization(Component):
    """Třída reprezentující vizualizaci běhového prostředí."""

    def __init__(self, gui: "GraphicalInterface", global_frame: tk.LabelFrame):
        Component.__init__(self, gui, global_frame)
        self._frame = tk.LabelFrame(
            global_frame, text="Status", padx=5, pady=5)
        self._frame.grid(row=0, column=0, sticky="N")

        # Definice popisných labelů
        id_label = tk.Label(self.frame, text="ID autora:")
        name_label = tk.Label(self.frame, text="Jméno autora:")
        status_label = tk.Label(self.frame, text="Status:")
        program_label = tk.Label(self.frame, text="Program:")

        # Definice konkrétních hodnot
        self._current_id = tk.Label(self.frame, text=_NOT_AVAILABLE)
        self._a_name = tk.Label(self.frame, text=_NOT_AVAILABLE)
        self._a_status = tk.Label(self.frame, text=_NOT_AVAILABLE)
        self._a_program = tk.Label(self.frame, text=_NOT_AVAILABLE)

        # Přidání do tabulky
        id_label.grid(row=0, sticky="W")
        name_label.grid(row=1, sticky="W")
        status_label.grid(row=2, sticky="W")
        program_label.grid(row=3, sticky="W")
        self._current_id.grid(row=0, column=1, sticky="E")
        self._a_name.grid(row=1, column=1, sticky="E")
        self._a_status.grid(row=2, column=1, sticky="E")
        self._a_program.grid(row=3, column=1, sticky="E")

        # Celkový počet běhových prostředí, která mají být platformou spuštěna
        self._num_of_rts = 0

    @property
    def frame(self) -> tk.LabelFrame:
        """Vlastnost vrací rámec, ve kterém je vizualizace běhového prostředí
        zobrazena."""
        return self._frame

    def set_testing_runtimes(self, num_of_rts: int):
        """Funkce nastavuje celkový počet všech běhových prostředí, která
        mají být v rámci platformy spuštěna. Tato funkce umožňuje sledování
        průběhu v rámci hromadného testování."""
        self._num_of_rts = num_of_rts

    def set_author(self, author_id: str, author_name: str, index: int):
        """Funkce nastavuje popisné údaje nového autora."""
        self._current_id.configure(text=author_id)
        self._a_name.configure(text=author_name)
        self._a_status.configure(text=f"{index}/{self._num_of_rts}")
        self._a_program.configure(
            text=self.gui.platform.current_runtime.program.path)


class GraphicalInterface:
    """Hlavní třída celého grafického rozhraní, která má za cíl zobrazovat,
    řídit a reagovat na události v rámci celého uživatelského rozhraní."""

    # Definice událostí, na které grafické rozhraní reaguje
    _EVENT_SIGNATURES = {
        "runtime_change": "<<runtime_change>>",
        "world_change": "<<world_change>>",
        "robot_change": "<<robot_change>>",
        "marks_change": "<<marks_change>>"
    }

    def __init__(self, platform: "platform_module.Platform"):
        """Initor, který přijímá referenci na platformu, kterou má sledovat
        a pro kterou je grafické rozhraní budováno."""

        self._platform = platform

        # Vytvoření kořene GUI a nastavení popisku
        self._master = tk.Tk()
        self._master.title(platform.assignment_name)

        # Nastavení rámce, který obsahuje všechny komponenty
        self._global_frame = tk.LabelFrame(self._master, text="Průběh testů",
                                           padx=5, pady=5)
        self._global_frame.pack(padx=10, pady=10)

        # Vytvoření komponent pro svět a sledování postupu běhových prostředí
        self._runtime_c = RuntimeVisualization(self, self._global_frame)
        self._world_c = WorldVisualization(self, self._global_frame)

        # Konfigurace
        self._is_active = True
        self._master.protocol("WM_DELETE_WINDOW", self.close)

        """Připojení naslouchání na virtuální události"""
        # Událost změny běhového prostředí
        self._master.bind(
            self._EVENT_SIGNATURES["runtime_change"],
            lambda e: self._update_runtime())

        # Událost změny světa
        self._master.bind(
            self._EVENT_SIGNATURES["world_change"],
            lambda e: self._update_world())

        # Událost změny robota
        self._master.bind(
            self._EVENT_SIGNATURES["robot_change"],
            lambda e: self._update_robot())

        # Událost změny značky
        self._master.bind(
            self._EVENT_SIGNATURES["marks_change"],
            lambda e: self._update_marks())

    @property
    def platform(self) -> "platform_module.Platform":
        """Vlastnost vrací platformu, pro kterou bylo GUI vytvořeno"""
        return self._platform

    def _update(self, event_keyword: str):
        """Funkce odpovědná za odeslání specifické události na kořen GUI."""

        # Pokud nebyla stanovena platforma, nelze pokračovat
        if self._platform is None:
            raise Exception("PLATFORMA NEBYLA STANOVENA!")

        # Pokud je GUI aktivní, vytvoř si událost
        elif self._is_active:
            self._master.event_generate(event_keyword)

    def _update_runtime(self):
        """Funkce odpovědná za provedení změny v GUI na základě změny běhového
        prostředí."""

        # Získání reference na aktuální běhové prostředí
        runtime = self.platform.current_runtime

        # Zanesení změn
        self._runtime_c.set_testing_runtimes(
            len(self.platform.runtime_factories) * len(self.platform.programs))

        self._runtime_c.set_author(runtime.program.author_id,
                                   runtime.program.author_name,
                                   self.platform.current_runtime_index)

    def _update_world(self):
        """Funkce odpovědná za delegování odpovědnosti o překreslení obrazu
        světa."""
        self._world_c.redraw()

    def _update_robot(self):
        """Funkce odpovědná za delegování odpovědnosti o překreslení obrazu
        robota."""
        self._world_c.redraw_robots()

    def _update_marks(self):
        """Funkce odpovědná za delegování odpovědnosti o překreslení značek."""
        if self.platform.current_runtime.is_ready:
            self._world_c.redraw_marks()

    def notify_runtime_change(self):
        """Vnější upozornění na změnu v běhovém prostředí. K této funkci lze
        libovolně přistupovat z jiných vláken."""
        self._update(self._EVENT_SIGNATURES["runtime_change"])

    def notify_world_change(self):
        """Vnější upozornění na změnu ve světě. K této funkci lze
        libovolně přistupovat z jiných vláken."""
        self._update(self._EVENT_SIGNATURES["world_change"])

    def notify_robot_change(self):
        """Vnější upozornění na změnu ve stavu robota. K této funkci lze
        libovolně přistupovat z jiných vláken."""
        self._update(self._EVENT_SIGNATURES["robot_change"])

    def notify_marks_change(self):
        """Vnější upozornění na změnu v kontextu značek políček. K této funkci
        lze libovolně přistupovat z jiných vláken."""
        self._update(self._EVENT_SIGNATURES["marks_change"])

    def close(self):
        """Funkce reagující na událost ukončení okna. Ať už křížkem nebo
        z vnějšku GUI."""
        self._is_active = False
        self._master.destroy()

    def run(self):
        """Samotná funkce spuštění GUI. Po jejím zavolání se toto vlákno
        rezervuje pouze na mainloop okna."""
        self._master.mainloop()


_GI: GraphicalInterface = None


def build_graphical_interface(platform: "platform_module.Platform"):
    """Funkce, která se pokusí vytvořit grafické rozhraní a zobrazit ho."""

    global _GI

    # Pokud již jedno GUI bylo vytvořeno
    if _GI is not None:
        raise Exception("NELZE VYTVOŘIT VÍCE GRAFICKÝCH ROZHRANÍ")

    # Vytvoř a nakonfiguruj nové GUI
    _GI = GraphicalInterface(platform)

    # Spusť GUI
    _GI.run()


def update_runtime():
    """Přístupová funkce pro překreslení údajů v kontextu běhového prostředí.
    """
    if _GI is not None:
        _GI.notify_runtime_change()


def update_world():
    """Přístupová funkce pro překreslení údajů v kontextu světa.
    """
    if _GI is not None:
        _GI.notify_world_change()


def update_robot():
    """Přístupová funkce pro překreslení údajů v kontextu stavu robota.
    """
    if _GI is not None:
        _GI.notify_robot_change()


def update_marks():
    """Přístupová funkce pro překreslení údajů v kontextu značek na políčcích.
    """
    if _GI is not None:
        _GI.notify_marks_change()


def window_close():
    """Přístupová funkce pro bezpečné ukončení grafického rozhraní."""
    if _GI is not None:
        _GI.close()



