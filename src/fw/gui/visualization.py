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

"""Definice barvy, kterou je políčko ohraničeno."""
_OUTLINE_COLOUR = "gold"

"""Definice barvy, kterou má robot"""
_ROBOT_COLOUR = "red"

"""Definice velikosti políčka"""
_FIELD_W = 25
_FIELD_H = 25

"""Text značící nedostupnost (Not Available; defaultně 'N/A')."""
_NOT_AVAILABLE = "N/A"


def east_robot_polygon(x_indent, y_indent):
    """"""
    return (
        x_indent + _FIELD_W, y_indent + (_FIELD_H * 0.5),
        x_indent + 0, y_indent + _FIELD_H,
        x_indent + (_FIELD_W * 0.25), y_indent + (_FIELD_H * 0.5),
        x_indent + 0, y_indent + 0
    )


def north_robot_polygon(x_indent, y_indent):
    """"""
    return (
        x_indent + (_FIELD_W * 0.5), y_indent + 0,
        x_indent + _FIELD_W, y_indent + _FIELD_H,
        x_indent + (_FIELD_W * 0.5), y_indent + (_FIELD_H * 0.75),
        x_indent + 0, y_indent + _FIELD_H
    )


def west_robot_polygon(x_indent, y_indent):
    """"""
    return (
        x_indent + 0, y_indent + (_FIELD_H * 0.5),
        x_indent + _FIELD_W, y_indent + 0,
        x_indent + (_FIELD_W * 0.75), y_indent + (_FIELD_H * 0.5),
        x_indent + _FIELD_W, y_indent + _FIELD_H
    )


def south_robot_polygon(x_indent, y_indent):
    """"""
    return (
        x_indent + (_FIELD_W * 0.5), y_indent + _FIELD_H,
        x_indent + 0, y_indent + 0,
        x_indent + (_FIELD_W * 0.5), y_indent + (_FIELD_H * 0.25),
        x_indent + _FIELD_W, y_indent + 0
    )


def resovle_robot_polygon(rs, x_indent, y_indent):
    """"""

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
        self._frame = tk.LabelFrame(global_frame, text="Aktuální svět",
                                    padx=5, pady=5)
        self._frame.grid(row=0, column=1)

        # Nastavení plátna
        self._canvas = tk.Canvas(self.frame, width=100, height=100,
                                 bg=_BACKGROUND_COLOUR)
        self._canvas.pack()

        self._robot_vis = []

    @property
    def frame(self) -> tk.LabelFrame:
        """"""
        return self._frame

    @property
    def canvas(self) -> tk.Canvas:
        """"""
        return self._canvas

    def redraw(self):
        """"""
        # Odstranění plátna
        self.canvas.delete("all")
        self.canvas.destroy()

        # Pomocné přístupové proměnné
        runtime = self.gui.platform.current_runtime
        world = runtime.world
        width = world.width
        height = world.height

        self._canvas = tk.Canvas(self.frame, width=width*_FIELD_W,
                                 height=height*_FIELD_H, bg=_BACKGROUND_COLOUR)
        self._canvas.pack()

        min_x = min(world.fields, key=lambda f: f.x).x
        min_y = min(world.fields, key=lambda f: f.y).y

        for field in world.fields:
            colour = _PATH_COLOUR if field.is_path else _WALL_COLOUR
            self._draw_field(field.x - min_x, field.y - min_y, colour, height)

        self.redraw_robots()

    def _draw_field(self, x: int, y: int, colour: str, height: int):
        """"""
        w = _FIELD_W
        h = _FIELD_H
        self.canvas.create_rectangle(
            x * w,  # Stanovení šířky horního levého rohu
            (height - y - 1) * h,  # Stanovení výšky horního levého rohu
            (x * w) + w,  # Stanovení šířky dolního pravého rohu
            ((height - y - 1) * h) + h,  # Stanovení výšky dolního pravého rohu
            fill=colour,  # Stanovení barvy výplně políčka
            outline=_OUTLINE_COLOUR  # Stanovení barvy ohraničení políčka
        )

    def redraw_robots(self):

        if len(self._robot_vis) > 0:
            for robot in self._robot_vis:
                self.canvas.delete(robot)
        self._robot_vis = []

        world = self.gui.platform.current_runtime.world
        rs_m = world.robot_state_manager

        min_x = min(world.fields, key=lambda f: f.x).x
        min_y = min(world.fields, key=lambda f: f.y).y
        max_y = max(world.fields, key=lambda f: f.y).y

        for rs in rs_m.robot_states:
            x_indent = (rs.field.x - min_x) * _FIELD_W
            y_indent = (max_y - rs.field.y - min_y) * _FIELD_H
            self._robot_vis.append(self.canvas.create_polygon(
                resovle_robot_polygon(rs, x_indent, y_indent),
                fill=_ROBOT_COLOUR, outline="black"))


class RuntimeVisualization(Component):
    """"""

    def __init__(self, gui: "GraphicalInterface", global_frame: tk.LabelFrame):
        Component.__init__(self, gui, global_frame)
        self._frame = tk.LabelFrame(
            global_frame, text="Status", padx=5, pady=5)
        self._frame.grid(row=0, column=0, sticky="N")

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
        "world_change": "<<world_change>>",
        "robot_change": "<<robot_change>>",
    }

    def __init__(self, platform: "platform_module.Platform"):
        """"""
        self._master = tk.Tk()
        self._platform = platform

        self._master.title(platform.assignment_name)

        self._global_frame = tk.LabelFrame(self._master, text="Průběh testů",
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
        self._master.bind(
            GraphicalInterface._EVENT_SIGNATURES["world_change"],
            lambda e: self._update_world()
        )
        self._master.bind(
            GraphicalInterface._EVENT_SIGNATURES["robot_change"],
            lambda e: self._update_robot()
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

    def _update_world(self):
        self._world_c.redraw()

    def _update_robot(self):
        self._world_c.redraw_robots()

    def notify_runtime_change(self):
        self._update(GraphicalInterface._EVENT_SIGNATURES["runtime_change"])

    def notify_world_change(self):
        self._update(GraphicalInterface._EVENT_SIGNATURES["world_change"])

    def notify_robot_change(self):
        self._update(GraphicalInterface._EVENT_SIGNATURES["robot_change"])

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


def update_runtime():
    _GI.notify_runtime_change()


def update_world():
    _GI.notify_world_change()

def update_robot():
    _GI.notify_robot_change()


def window_close():
    _GI.close()



