""""""



# Import standardních knihoven
from abc import ABC, abstractmethod
import datetime

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
        result = (
            f"""
            <!DOCTYPE html>
            <html>
                <head>
                    <title>Výsledky Platformy</title>
                    <link href='../bootstrap.min.css' rel='stylesheet'>
                </head>
                <body>
                    <div style="margin: auto; width: 95%">
                        <h1>Výsledky Platformy</h1>
                        <p>Výstup vytvořen: {datetime.datetime.now()}<p>
                        <hr />
                        {self._summary_table()}
                        <hr />
                        {self._plugin_loading()}
                        <hr />
                    <div>
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

        for runtime in self.runtimes:
            HTMLRuntimeBuilder(runtime, self.dir_name).build()

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
        head = ("<thead>"
                    "<th>ID autora</th>"
                    "<th>Jméno autora</th>"
                    "<th>Plugin</th>")
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
            tbody = (f"{tbody}"
                     "<tr>"
                     f"<th>{program.author_id}</th>" 
                     f"<th>{program.author_name}</th>"
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
            return (
                f"<a href='runtimes/{runtime.hex_id}.html' target='_blank'>"
                f"⭐ ({int(val + 0.5)} %)</a>")
        if val > 70:
            return (
                f"<a href='runtimes/{runtime.hex_id}.html' target='_blank'>"
                f"✅ ({int(val + 0.5)} %)</a>")
        elif val > 20:
            return (
                f"<a href='runtimes/{runtime.hex_id}.html' target='_blank'>"
                f"⛔ ({int(val + 0.5)} %)</a>")
        else:
            return (
                f"<a href='runtimes/{runtime.hex_id}.html' target='_blank'>"
                f"🔥 ({int(val + 0.5)} %)</a>")

    def _plugin_loading(self) -> str:
        """"""
        return (
            f"""
            <br />
            <h2 class='mt-3'>Načítání pluginů</h2>
            <p class="lead">
            V tomto bloku je uveden proces načítání pluginů. Konkrétně
            načítání <strong>továren jednotek</strong>, 
            <strong>továren běhových prostředí</strong> a 
            <strong>programů robotů</strong>.</p>
            <br />
            {self._uf_plugins_loading()}\n
            <br />
            {self._rt_plugins_loading()}\n
            <br />
            {self._p_plugins_loading()}\n
            <br />
            {self._invalid_plugins()}\n
            <br />
            {self._not_identified_plugins()}\n
            <br />
            """)

    def _uf_plugins_loading(self) -> str:
        """"""
        return (f"""<h4 class='mt-3'>Načítání továren jednotek</h4>
        <p class='lead'>Celkem bylo načteno {len(self.unit_factories)} 
        pluginů továrních jednotek, kterými bylo možné robota osadit. 
        Validní pluginy byly tyto:</p>
        {self._valid_loader_analysis(self.unit_factories_loaders)}
        <br/ >
        <p class='lead'>Pokud zde není uveden plugin, který očekáváte, zkuste
        se podívat do nevalidních a neidentifikovanách pluginů.</p>
        """)

    def _rt_plugins_loading(self) -> str:
        """"""
        return (f"""<h4 class='mt-3'>Načítání továren běhových prostředí</h4>
        <p class='lead'>Celkem bylo načteno 
        {len(self.runtime_factory_loader.runtime_factories)} továren běhových
        prostředí, ve kterých byla ověřována správnost programů robotů.
        {self._valid_loader_analysis(tuple([self.runtime_factory_loader]))}
        <br/ >
        <p class='lead'>Pokud zde není uveden plugin, který očekáváte, zkuste
        se podívat do nevalidních a neidentifikovanách pluginů.</p>""")

    def _p_plugins_loading(self) -> str:
        """"""
        return (f"""<h4 class='mt-3'>Načítání programů</h4>
        <p class='lead'>Celkem bylo načteno {sum(tuple(map(
            lambda pl: len(pl.programs), self.program_loaders)))} pluginů 
        programů. Validní pluginy programů byly tyto:</p>
        {self._valid_loader_analysis(self.program_loaders)}
        <br/ >
        <p class='lead'>Pokud zde není uveden plugin, který očekáváte, zkuste
        se podívat do nevalidních a neidentifikovanách pluginů.</p>""")

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
                    "<li class='list-group-item list-group-item-warning mt-1'>"
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

class HTMLRuntimeBuilder(RuntimeResultBuilder):

    def __init__(self, runtime: runtime_module.AbstractRuntime,
                 dirname: str):
        RuntimeResultBuilder.__init__(self, runtime)

        self._dirname = dirname

    @property
    def dirname(self) -> str:
        """"""
        return self._dirname

    def build(self):
        result = (
            f"""
            <!DOCTYPE html>
            <html>
                <head>
                    <title>Výsledky programu {self.runtime_id}</title>
                    <link href='../../bootstrap.min.css' rel='stylesheet'>
                </head>
                <body>
                    <div style="margin: auto; width: 95%">
                        <h1>Výsledky běhového prostředí</h1>
                        <i>Výstup vytvořen: {datetime.datetime.now()}</i>
                        <hr />
                        <br />
                        {self.about_program()}
                        <br />
                        <hr />
                        <br />
                        {self.about_runtime()}
                        <br />
                        <hr />
                        <br />
                        {self.target_fulfillment()}
                        <br />
                        <hr />
                        <br />
                        {self.logs()}
                    <div>
                </body>
                <script></script>
            </html>"""
        )

        folder = fs.join_paths(self.dirname, "runtimes")
        rt_file = fs.join_paths(folder, f"{self.runtime_id}.html")

        if not fs.exists(folder):
            import os
            os.makedirs(fs.join_paths(self.dirname, "runtimes"))

        with open(rt_file, "w", encoding="utf-8") as f:
            f.write(result.replace("   ", "").replace("  ", ""))

    def about_program(self):

        program = self.runtime.program

        return (

            f"""
            <div class="card bg-light text-dark mb-3">
              <div class="card-header">
                O programu
              </div>
              <div class="card-body">
                <h3 class="card-title">
                <b>{self.program.author_id} - {self.author_name}</b></h3>
                <p class="card-text">
                    <strong>Umístění pluginu: </strong>
                    <samp>{program.path}</samp>
                    <br />
                    <strong>Jméno robota: </strong> 
                    <samp>{self.robots[0].name}</samp>
                </p>
                <div class='card-footer'>
                    <small class="text-muted">Úspěšnost 
                    {(int(self.runtime.target.evaluate * 100 + 0.5))} %.\t 
                    <a href="#target-results">Více</a></small>
                </div>
              </div>
            </div>
            """)

    def about_runtime(self):
        return (
            f"""
            <h2>O běhovém prostředí <i>{self.runtime.target.name}</i></h2>
            <i>ID běhového prostředí: {self.runtime_id}</i>
            <hr />
            <p class='lead'>{self.runtime.target.description}</p>
            <br />
            <h3>Dostupné jednotky</h3>
            {self.available_units()}
            """)

    def available_units(self):
        units = self.runtime.units
        result = (
            f"<p class='lead'>Zde jsou uvedeny jednotky, kterými bylo možné "
            f"robota osadit.</p>"
            f"<br />"
            f"<div class='row'>")
        for unit in units:
            result = f"{result}\n{self.describe_unit(unit)}"
        return f"{result}</div>"

    def describe_unit(self, unit):

        was_mounted = unit.name in self.runtime.robots[0].unit_names

        was_mounted_text = ""

        if was_mounted:
            was_mounted_text = "<i>Robot byl touto jednotkou osazen</i>"
        else:
            was_mounted_text = "<i>Robot byl touto jednotkou osazen nebyl</i>"

        return (
            f"""
            <div class='col-md-4'>
                <div class="card bg-light mb-3">
                  <div class="card-header">
                    {'Aktuátor' if unit.is_actuator else 'Senzor'}
                  </div>
                  <div class="card-body">
                    <h4 class="card-title">{unit.name}</h5>
                    <p class="card-text lean">{unit.description}</p>
                    <p class="card-text">
                        <small class="text-muted">{was_mounted_text}</small>
                    </p>
                  </div>
                </div>
            </div>
            """)

    def target_fulfillment(self):
        """"""
        target = self.runtime.target

        result = (
            f"<h2 id='target-results'>Úloha '<samp>{target.name}</samp>' "
            f"a její výsledky</h2>\n<i>{target.description}</i>"
            f"<br />"
            f"<ul>")

        for task in target.tasks:
            task_result = (
                f"<li>{'✅' if task.eval() else '❌'} <b>{task.name}</b> "
                f"<i>({task.description})</i><ul>")
            for ef in task.evaluation_functions:
                task_result = (
                    f"{task_result}<li>{'✅' if ef.eval() else '❌'} {ef.name}"
                    f"</li>")
            result = f"{result}\n{task_result}</ul><br />"
        return f"{result}</ul>"

    def logs(self):

        result = (
            "<h2>Záznamy</h2>"
            "<p class='lead'>Zde jsou uvedené záznamy spjaté s tímto během</p>"
            "<br />"
            "<samp><ul style='list-style-type: none'>")

        for o in self.logger.outputs:
            if o.has_memo and o.takes_all:
                for log in o.remember:
                    result = (
                        f"{result}<li>[{log.time[0:8]}]"
                        f"[{log.context}]: {log.message}</li>")
                break

        return f"{result}</ul><samp>"

