""""""

# Import standardních knihoven
import tkinter as tk

# Import lokálních knihoven
import src.fw.platform.platform as platform_module


# Definice základních proměnných

"""Definice barvy, která bude na pozadí. Bude viditelná pouze tam, kde políčko
chybí a ve světě je díra."""
_BACKGROUND_COLOUR = "red"

"""Definice barvy, která bude reprezentovat políčko typu cesta."""
_PATH_COLOUR = "bisque"

"""Definice barvy, která bude reprezentovat políčko typu stěna."""
_WALL_COLOUR = "grey4"

"""Definice velikosti políčka"""
_FIELD_DEFINITION = {"w": 20, "h": 20}

"""Text značící nedostupnost (Not Available; defaultně 'N/A')."""
_NOT_AVAILABLE = "N/A"


class FieldVisualization:
    """"""


class Component:
    """"""

    def __init__(self, gui: "GraphicalInterface", global_frame: tk.LabelFrame):
        self._global_frame = global_frame
        self._gui = gui

    @property
    def global_frame(self) -> tk.LabelFrame:
        """"""
        return self._global_frame

    @property
    def gui(self) -> "GraphicalInterface":
        """"""
        return self._gui


class WorldVisualization(Component):
    """"""

    def __init__(self, gui: "GraphicalInterface", global_frame: tk.LabelFrame):
        """"""

        # Volání předka
        Component.__init__(self, gui, global_frame)

        # Nastavení hlavního frame
        self._frame = tk.LabelFrame(global_frame, text="WORLD", padx=5, pady=5)
        self._frame.grid(row=0, column=1)

        # Nastavení plátna
        self._canvas = tk.Canvas(self.frame, width=100, height=100,
                                 bg=_BACKGROUND_COLOUR)
        self._canvas.pack()

    @property
    def frame(self) -> tk.LabelFrame:
        """"""
        return self._frame

    @property
    def canvas(self) -> tk.Canvas:
        """"""
        return self._canvas

    def redraw(self, platform: platform_module.Platform):
        """"""
        runtime = platform.current_runtime
        world = runtime.world



class RuntimeVisualization(Component):
    """"""

    def __init__(self, gui: "GraphicalInterface", global_frame: tk.LabelFrame):
        Component.__init__(self, gui, global_frame)
        self._frame = tk.LabelFrame(
            global_frame, text="RUNTIME", padx=5, pady=5)
        self._frame.grid(row=0, column=0)

        # Definice popisných labelů
        id_label = tk.Label(self.frame, text="ID autora:")
        name_label = tk.Label(self.frame, text="Jméno autora:")
        status_label = tk.Label(self.frame, text="Status:")

        # Definice konkrétních hodnot
        self._current_id = tk.Label(self.frame, text=_NOT_AVAILABLE)
        self._a_name = tk.Label(self.frame, text=_NOT_AVAILABLE)
        self._a_status = tk.Label(self.frame, text=_NOT_AVAILABLE)

        # Přidání do tabulky
        id_label.grid(row=0, sticky="W")
        name_label.grid(row=1, sticky="W")
        status_label.grid(row=2, sticky="W")
        self._current_id.grid(row=0, column=1, sticky="E")
        self._a_name.grid(row=1, column=1, sticky="E")
        self._a_status.grid(row=2, column=1, sticky="E")

        self._num_of_rts = 0

    @property
    def frame(self) -> tk.LabelFrame:
        return self._frame

    def set_testing_runtimes(self, num_of_rts: int):
        self._num_of_rts = num_of_rts

    def set_author(self, author_id: str, author_name: str, index: int):
        self._current_id.configure(text=author_id)
        self._a_name.configure(text=author_name)
        self._a_status.configure(text=f"{index}/{self._num_of_rts}")


class GraphicalInterface:
    """"""

    _EVENT_SIGNATURES = {
        "runtime_change": "<<runtime_change>>",
    }

    def __init__(self, platform: "platform_module.Platform"):
        """"""
        self._master = tk.Tk()
        self._platform = platform

        self._master.title("TEST TITLE")

        self._global_frame = tk.LabelFrame(self._master, text="GLOBAL FRAME",
                                           padx=5, pady=5)
        self._global_frame.pack(padx=10, pady=10)

        self._runtime_c = RuntimeVisualization(self, self._global_frame)
        self._world_c = WorldVisualization(self, self._global_frame)

        # Konfigurace
        self._is_active = True
        self._master.protocol("WM_DELETE_WINDOW", self.close)
        self._master.bind(
            GraphicalInterface._EVENT_SIGNATURES["runtime_change"],
            lambda e: self._update_runtime()
        )

    @property
    def platform(self) -> "platform_module.Platform":
        return self._platform

    def _update(self, event_keyword: str):
        if self._platform is None:
            raise Exception("PLATFORMA NEBYLA STANOVENA!")
        elif self._is_active:
            self._master.event_generate(event_keyword)

    def _update_runtime(self):
        runtime = self.platform.current_runtime
        self._runtime_c.set_testing_runtimes(
            len(self.platform.runtime_factories) * len(self.platform.programs))
        self._runtime_c.set_author(_NOT_AVAILABLE, runtime.program.author_name,
                                   self.platform.current_runtime_index)

    def notify_runtime_change(self):
        self._update(GraphicalInterface._EVENT_SIGNATURES["runtime_change"])

    def close(self):
        self._is_active = False
        self._master.destroy()

    def run(self):
        self._master.mainloop()


_GI: GraphicalInterface = None


def build_graphical_interface(platform: "platform_module.Platform"):
    global _GI
    if _GI is not None:
        raise Exception("NELZE VYTVOŘIT VÍCE GRAFICKÝCH ROZHRANÍ")
    _GI = GraphicalInterface(platform)
    _GI.run()


def update_world():
    pass


def update_runtime():
    _GI.notify_runtime_change()


def window_close():
    _GI.close()



