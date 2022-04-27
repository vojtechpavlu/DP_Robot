""""""



# Import standardních knihoven
from abc import ABC, abstractmethod

# Import lokálních knihoven
from src.fw.target.results.result_builder import (
    PlatformResultBuilder, RuntimeResultBuilder, ResultBuilderError)

import src.fw.platform.platform as platform_module
import src.fw.platform.runtime as runtime_module
import src.fw.utils.filesystem as fs
from src.fw.utils.loading.plugin_loader import PluginLoader


def _naming_convention(dirname: str):
    """"""

    if len(dirname) > 0:
        return dirname

    import datetime
    from src.fw.utils.timeworks import time, date

    dt = datetime.datetime.now()
    output_name = str(date(dt))
    return f"{output_name}_{str(time(dt, False)).replace(':', '-')}"


class PlatformHTMLBuilder(PlatformResultBuilder):
    """"""

    def __init__(
            self, platform: "platform_module.Platform", dir_name: str = ""):

        PlatformResultBuilder.__init__(self, platform)

        self._dir_name = fs.join_paths(fs.output_path(),
                                       _naming_convention(dir_name))

        if fs.exists(self._dir_name):
            raise ResultBuilderError(
                f"Soubor s názvem '{self._dir_name}' již existuje", self)

    @property
    def dir_name(self) -> str:
        """Vlastnost vrací cestu k adresáři, ve kterém má být zbudován výstup.
        """
        return self._dir_name

    def build(self):
        """"""
        import datetime
        result = (
            f"""
            <!DOCTYPE html>
            <html>
                <head>
                    <title>Výsledky Platformy</title>
                    <link href='../bootstrap.min.css' rel='stylesheet'>
                </head>
                <body>
                    <h1>Výsledky Platformy</h1>
                    <p>Výstup vytvořen: {datetime.datetime.now()}<p>
                    <hr />
                    {self._summary_table()}
                    <hr />
                    {self._plugin_loading()}
                    <hr />
                </body>
                <script></script>
            </html>
            """
        )

        platform_file = fs.join_paths(self.dir_name, "platform.html")

        import os
        os.makedirs(self.dir_name)

        with open(platform_file, "w", encoding="utf-8") as f:
            f.write(result.replace("   ", "").replace("  ", ""))

        import webbrowser
        webbrowser.open(f"file://"
                        f"{fs.join_paths(self.dir_name, 'platform.html')}")

    def _summary_table(self) -> str:
        """"""
        return (
            f"""
            <h2>Souhrnná tabulka</h2>
            <p class="lead">
                V této tabulce je uveden kartézský součin mezi jednotlivými
                běhovými prostředími a jednotlivými programy robotů.
            </p>
            <table class="table">
                {self._table_head()}
                {self._table_content()}
            </table>
            """
        )

    def _table_head(self) -> str:
        """"""
        head = ("<thead>\n<th>Autor</th>\n<th>Plugin</th>")
        rf_paths = []
        for rt in self.runtimes:
            if rt.runtime_factory.absolute_path not in rf_paths:
                head = f"{head}\n<th>{rt.target.name}</th>"
                rf_paths.append(rt.runtime_factory.absolute_path)
        return f"{head}\n</thead>"

    def _table_content(self) -> str:
        """"""
        tbody = "<tbody>"

        for program in self.platform.programs:
            tbody = (f"{tbody}\n<tr>\n<th>{program.author_name}</th>"
                     f"<td><samp>{program.path}</samp></td>")
            for rt in self.runtimes:
                if rt.program.absolute_path == program.absolute_path:
                    tbody = f"{tbody}\n<td>{self.evaluate(rt)}</td>"
            tbody = f"{tbody}\n</tr>"
        return f"{tbody}\n</tbody>"

    @staticmethod
    def evaluate(runtime):
        """"""
        val = runtime.target.evaluate * 100

        if val > 90:
            return f"⭐ ({val} %)"
        if val > 70:
            return f"✅ ({val} %)"
        elif val > 20:
            return f"⛔ ({val} %)"
        else:
            return f"🔥 ({val} %)"

    def _plugin_loading(self) -> str:
        """"""
        return (
            f"""
            <h2 class='mt-3'>Načítání pluginů</h2>
            <p class="lead">
            V tomto bloku je uveden proces načítání pluginů. Konkrétně
            načítání <strong>továren jednotek</strong>, 
            <strong>továren běhových prostředí</strong> a 
            <strong>programů robotů</strong>.</p>
            {self._uf_plugins_loading()}\n
            {self._rt_plugins_loading()}\n
            {self._p_plugins_loading()}\n
            {self._invalid_plugins()}\n
            {self._not_identified_plugins()}\n
            """)

    def _uf_plugins_loading(self) -> str:
        """"""
        return (f"""<h4 class='mt-3'>Načítání továren jednotek</h4>
        <p class='lead'>Celkem bylo načteno {len(self.unit_factories)} 
        pluginů továrních jednotek, kterými bylo možné robota osadit. 
        Validní pluginy byly tyto:</p>
        {self._valid_loader_analysis(self.unit_factories_loaders)}""")

    def _rt_plugins_loading(self) -> str:
        """"""
        return (f"""<h4 class='mt-3'>Načítání továren běhových prostředí</h4>
        <p class='lead'>Celkem bylo načteno 
        {len(self.runtime_factory_loader.runtime_factories)} továren běhových
        prostředí, ve kterých byla ověřována správnost programů robotů.
        {self._valid_loader_analysis(tuple([self.runtime_factory_loader]))}""")

    def _p_plugins_loading(self) -> str:
        """"""
        return (f"""<h4 class='mt-3'>Načítání programů</h4>
        <p class='lead'>Celkem bylo načteno {sum(tuple(map(
            lambda pl: len(pl.programs), self.program_loaders)))} pluginů 
        programů. Validní pluginy programů byly tyto:</p>
        {self._valid_loader_analysis(self.program_loaders)}""")

    def _invalid_plugins(self) -> str:
        """"""
        all_loaders = [self.runtime_factory_loader]
        all_loaders.extend(self.program_loaders)
        all_loaders.extend(self.unit_factories_loaders)

        return (f"""<h4 class='mt-3'>Nevalidní pluginy</h4>
        <p class='lead'>V tomto bloku jsou uvedeny všechny pluginy, které
        prošly identifikací, ale nebyly shledány jako validní.</p>
        {self._invalid_loader_analysis(tuple(all_loaders))}""")

    def _not_identified_plugins(self) -> str:
        """"""
        all_loaders = [self.runtime_factory_loader]
        all_loaders.extend(self.program_loaders)
        all_loaders.extend(self.unit_factories_loaders)

        return (f"""<h4 class='mt-3'>Neidentifikované pluginy</h4>
        <p class='lead'>V tomto bloku jsou uvedené pluginy, které nebyly
        ani připuštěny k validaci, neboť nesplňovaly některá základní 
        stanovená pravidla. Pokud nebyl některý plugin správně načten,
        zkuste se podívat právě do této sekce, třeba ho příslušný loader
        odebral úmyslně.</p>
        {self._not_identified_analysis(tuple(all_loaders))}""")

    @staticmethod
    def _valid_loader_analysis(plugin_loaders: "tuple[PluginLoader]"):
        """"""

        plugin_results = []

        for plugin_loader in plugin_loaders:

            for plugin in plugin_loader.valid_plugins:
                plugin_results.append(
                    f"<li class='list-group-item list-group-item-success"
                    f" mt-1'><samp>{plugin.absolute_path}</samp></li>")

        result = "<div class='list-group'>"
        for pr in plugin_results:
            result = f"{result}\n{pr}"

        return f"{result}\n</div>"

    @staticmethod
    def _invalid_loader_analysis(plugin_loaders: "tuple[PluginLoader]"):
        """"""

        plugin_results = []

        for plugin_loader in plugin_loaders:

            for plugin in plugin_loader.not_valid_plugins:
                result = (
                    f"<li class='list-group-item list-group-item-danger mt-1'>"
                    f"<samp>{plugin.absolute_path}</samp>\n<ul>")
                for v_v in plugin.violated_validators:
                    result = result + (
                        f"\n<li><strong>{v_v.name}</strong>: <i>"
                        f"{v_v.description}</i></li>")
                plugin_results.append(result + "\n</ul>")

        result = "<div class='list-group'>"
        for pr in plugin_results:
            result = f"{result}\n{pr}"

        return f"{result}\n</div>"

    @staticmethod
    def _not_identified_analysis(plugin_loaders: "tuple[PluginLoader]"):
        """"""
        plugin_results = []

        for plugin_loader in plugin_loaders:
            for plugin in plugin_loader.not_identified_plugins:
                plugin_results.append(
                    f"<li class='list-group-item list-group-item-warning'>"
                    f"<strong>{type(plugin_loader).__name__}"
                    f"</strong>: <samp>{plugin}</samp>"
                    f"""{PlatformHTMLBuilder._reason_for_not_identification(
                        plugin_loader, plugin)}</li>""")

        result = "<div class='list-group'>"
        for pr in plugin_results:
            result = f"{result}\n{pr}"

        return f"{result}\n</div>"

    @staticmethod
    def _reason_for_not_identification(
            plugin_loader: "PluginLoader", abs_path) -> str:
        names = []
        for identifier in plugin_loader.violated_identifiers(abs_path):
            names.append(
                f"<li><strong>{identifier.name}</strong>: "
                f"<i>{identifier.description}</i></li>")

        result = "<ul>"
        for name in names:
            result = f"{result}\n{name}"
        return f"{result}</ul>"


