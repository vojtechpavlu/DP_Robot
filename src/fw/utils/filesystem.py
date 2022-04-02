"""Modul sdružující funkcionalitu související s manipulací se souborovým
systémem.
"""

# Import standardních knihoven
import os
import re

# Import lokálních knihoven
from .error import PlatformError

# Defaultní názvy významných adresářů projektu
_SOURCE_FOLDER_NAME = "src"
_PLUGIN_FOLDER_NAME = "plugins"
_ASSIGNMENT_FOLDER_NAME = "assignments"


def exists(path: "str") -> "bool":
    """Funkce vrací informaci o tom, zda-li je adresa platná pro existující
    soubor, resp. adresář.
    """
    return os.path.exists(path)


def is_directory(path: "str") -> "bool":
    """Funkce vrací informaci o tom, zda-li je na zadané cestě adresář či
    nikoliv.

    Pokud zadaná adresa neexistuje, je vyhozena výjimka.
    """
    if exists(path):
        return os.path.isdir(path)
    raise FileSystemError(
        f"Zadaná adresa není platná: soubor '{path}' neexistuje", [path])


def is_file(path: "str") -> "bool":
    """Funkce vrací informaci o tom, zda-li je na zadané cestě soubor. Pokud
    jde o soubor, vrací True, pokud o adresář, vrací False.

    Pokud na zadaná adresa neexistuje, je vyhozena výjimka.
    """
    if exists(path):
        return os.path.isfile(path)
    raise FileSystemError(
        f"Zadaná adresa není platná: soubor '{path}' neexistuje", [path])


def root_directory_path() -> "str":
    """Funkce vrací absolutní cestu ke kořenové složce projektu.
    """
    return os.path.abspath(os.path.join(__file__, "..", "..", "..", ".."))


def plugin_path() -> "str":
    """Funkce vrací absolutní cestu k defaultnímu adresáři s pluginy."""
    return join_paths(root_directory_path(),
                      join_paths(_SOURCE_FOLDER_NAME,
                                 _PLUGIN_FOLDER_NAME))


def assignments_path() -> "str":
    """Funkce vrací absolutní cestu k adresáři, který má defaultně obsahovat
    pluginy v kontextu zadání úloh a programů k nim.

    Vychází zde z předpokladu, že daná zadání jsou uložena v podadresáři s
    názvem uloženým v proměnné '_ASSIGNMENT_FOLDER_NAME', který je v rámci
    adresáře pluginů."""
    return join_paths(plugin_path(), _ASSIGNMENT_FOLDER_NAME)


def assignment(assignment_name: str) -> str:
    """Funkce se pokusí vrátit cestu k adresáři, který obsahuje všechny
    požadované pluginy v kontextu zadání reprezentujících zadání daného
    názvu.

    Vychází zde z předpokladu, že je platný kontrakt funkce tohoto modulu
    'assignments_path()'."""

    # Pokud je délka názvu zadání kratší, než jeden znak
    if len(assignment_name) < 1:
        raise FileSystemError(f"Nelze najít zadání s prázdným názvem "
                              f"'{assignment_name}'", [])

    # Vytvoření cesty
    potential_path = join_paths(assignments_path(), assignment_name)

    # Pokud taková cesta neexistuje
    if not exists(potential_path):
        raise FileSystemError(f"Zadání s dodaným názvem neexistuje",
                              [potential_path])

    # Pokud dané zadání není reprezentováno adresářem
    elif not is_directory(potential_path):
        raise FileSystemError(f"Zadání musí být reprezentováno adresářem",
                              [potential_path])
    return potential_path


def list_assignments() -> "tuple[str]":
    """Funkce vrací seznam zadání v podobě ntice. Tato výstupní zadání jsou
    reprezentována jako ntice názvů zadání.

    Vychází zde z předpokladu, že je platný kontrakt funkce 'assignments_path'.
    """
    return tuple(map(lambda path: str(file_basename(path)), list_directories(
        assignments_path())))


def separator() -> str:
    """Funkce vrací znak, kterým je defaultně značen pohyb ve struktuře
    souborového systému.

    Zjednodušeně řečeno, MS Windows jde o tzv. zpětné lomítko (backslash) '\',
    u systému nad Unix se používá dopředné lomítko '/'.
    """
    return os.path.sep


def file_basename(path: "str", include_extension: bool = True) -> "str":
    """Funkce vrací název souboru dle zadané cesty. Název může volitelně
    obsahuje i příponu. To lze ovládat pomocí parametru 'include_extension'.
    """
    basename = os.path.basename(path)
    return basename if include_extension else os.path.splitext(basename)[0]


def list_files(path: "str", include_directories: bool = True) -> "list[str]":
    """Funkce vrací absolutní cesty ke všem potomkům obsaženým ve složce.

    Funkce umožňuje obsáhnout či ignorovat adresáře, v závislosti na parametru
    'include_directories'.
    """
    result = []
    if is_directory(path):
        for file in os.listdir(path):
            file = os.path.join(path, file)
            if is_file(file):
                result.append(file)
            elif is_directory(file) and include_directories:
                result.append(file)
        return result
    raise FileSystemError(
        f"Zadaná adresa není platná: soubor '{path}' není adresář", [path])


def list_directories(path: str) -> "list[str]":
    """Funkce vrátí seznam absolutních cest k podadresářům, které jsou v rámci
    dodaného adresáře reprezentovaného dodanou absolutní cestou.

    Funkce vyhazuje výjimku, není-li na dané cestě existující adresář.
    """
    return list(filter(lambda file: is_directory(file),
                       list_files(path, True)))


def list_files_with_extension(path: "str", ext: "str") -> "list[str]":
    """Funkce vrací seznam souborů, které mají zadanou koncovku.
    Koncovku lze v parametru dodat s úvodní tečkou či bez ní.
    Pokud na zadané cestě není adresář, je vyhozena výjimka.
    """
    ext = ext if ext and ext[0] == "." else f".{ext}"
    return list(filter(
        lambda file: os.path.splitext(file)[1] == ext, list_files(path)))


def deep_list_files(path: "str",
                    include_directories: bool = True) -> "list[str]":
    """Funkce prochází rekurzivně dodaný adresář do hloubky a vrací seznam
    souborů v něm.
    Pokud na dodané cestě není adresář, je vyhozena výjimka.
    """
    result = []
    if is_directory(path):
        for file in list_files(path):
            if is_file(file):
                result.append(file)
            elif is_directory(file):
                if include_directories:
                    result.append(file)
                result.extend(deep_list_files(file, include_directories))
        return result
    raise FileSystemError(
        f"Zadaná adresa není platná: soubor '{path}' není adresář", [path])


def deep_list_files_with_extension(path: "str", ext: "str") -> "list[str]":
    """Funkce rekurzivně prochází dodaný adresář do hloubky a vrací seznam
    souborů v něm. Ty jsou filtrovány podle koncovky.
    Koncovku lze zadat s úvodní tečkou i bez ní.
    Pokud na dodané cestě není adresář, je vyhozena výjimka.
    """
    ext = ext if ext and ext[0] == "." else f".{ext}"
    splitext = os.path.splitext
    return list(filter(
        lambda file: splitext(file)[1] == ext, deep_list_files(path, False)))


def contains_file(path: "str", filename: "str",
                  ignore_extension: bool = False) -> "bool":
    """Funkce vrací informaci o tom, zda-li adresář na zadané adrese obsahuje
    soubor, resp. složku s dodaným názvem.

    Pokud je nastaven modifikátor 'ignore_extension' na hodnotu True, pak

    Pokud na zadané cestě není adresář, je vyhozena výjimka.
    """
    if is_directory(path):
        basename = os.path.basename  # Zkrácení syntaxe
        splitext = os.path.splitext  # Zkrácení syntaxe
        for file in list_files(path):
            if basename(file) == filename:
                return True
            elif ignore_extension and basename(splitext(file)[0]) == filename:
                return True
        return False
    raise FileSystemError(
        f"Zadaná adresa není platná: soubot '{path}' není adresář", [path])


def deep_contains_file(path: "str", filename: "str",
                       ignore_extension: "bool" = False) -> "bool":
    """Funkce prochází do hloubky všechny adresáře od toho definovaného
    dodanou cestou. Pokud objeví soubor, resp. adresář s takovým názvem, je
    vrácena hodnota True, jinak False.

    Pokud je nastaven parametr 'ignore_extension' na hodnotu True, jsou
    ignorovány koncovky souborů.

    Pokud na zadané cestě není adresář, pak je vyhozena výjimka.
    """
    if is_directory(path):
        basename = os.path.basename
        splitext = os.path.splitext
        for file in list_files(path):
            if basename(file) == filename:
                return True
            elif ignore_extension and basename(splitext(file)[0]) == filename:
                return True
            elif is_directory(file) and deep_contains_file(
                    path=file, filename=filename,
                    ignore_extension=ignore_extension):
                return True
        return False
    raise FileSystemError(
        f"Zadaná adresa není platná: soubor '{path}' není adresář", [path])


def filesize(path: "str") -> "int":
    """Funkce vrací velikost dodaného souboru v bytech.
    Funkce počítá velikost pro jednotlivé soubory, stejně jako pro složky,
    které prochází do hloubky.

    Pokud na zadané cestě není žádný soubor, je vyhozena výjimka.
    """
    if exists(path):
        if is_file(path):
            return os.stat(path).st_size
        elif is_directory(path):
            size = 0
            for file in deep_list_files(path, False):
                size += filesize(file)
            return size
    raise FileSystemError(
        f"Zadaná adresa není platná: soubor '{path}' nenalezen", [path])


def count_files(path: "str", files_only: bool = False) -> "int":
    """Funkce spočítá všechny soubory v dodané složce.
    Funkce umožňuje ignorovat adresáře a zaměřit se pouze na soubory; vyloučit
    adresáře. To lze ovlivnit parametrem 'files_only'.

    Pokud na zadané adrese není adresář, je vyhozena výjimka.
    """
    if files_only:
        return len(list(filter(lambda file: is_file(file), list_files(path))))
    else:
        return len(list_files(path))


def deep_count_files(path: "str", files_only: bool = False) -> "int":
    """Funkce spočátá všechny soubory v dodané složce při hloubkovém průchodu.
    Funkce umí ignorovat adresáře a zaměřit se pouze na soubory. To lze
    definovat parametrem 'files_only'.
    """

    return len(list(filter(lambda file: is_file(file),
                           deep_list_files(path, not files_only))))


def create_file(parent_dir: "str", filename: "str", content: "str"):
    """Funkce vytvoří soubor v dodaném rodičovském adresáři a zapíše do něj
    dodaný obsah.
    Pokud na dodané absolutní cestě k rodičovské složce není adresář, bude
    vyhozena výjimka. Stejně tak v případě, že již existuje soubor daného
    názvu.
    """
    if is_directory(parent_dir):
        absolute = os.path.join(parent_dir, filename)
        if not exists(absolute):
            new_file = open(absolute, "x")
            new_file.write(content)
            new_file.close()
        else:
            raise FileSystemError(
                f"Soubor '{os.path.join(parent_dir, filename)}' již existuje",
                [os.path.join(parent_dir, filename)]
            )
    else:
        raise FileSystemError(f"Zadaná adresa není platná: adresář "
                              f"'{parent_dir}' nenalezen", [parent_dir])


def create_file_from_lines(parent_dir: "str", filename: "str",
                           lines: "list[str]", final_empty_line: bool = False):
    """Funkce vytvoří soubor v dodaném rodičovském adresáři a zapíše do něj
    obsah zpracovaný z dodaného seznamu řádků. Automaticky lze dodat prázdný
    řádek na konec. To lze upravit parametrem 'final_empty_line'.
    Pokud na dodané absolutní cestě k rodičovské složce není adresář, bude
    vyhozena výjimka. Stejně tak v případě, že již existuje soubor daného
    názvu."""
    content = ""
    for line in lines:
        content = f"{content}\n{line}" if content else line
    if final_empty_line:
        content = f"{content}\n"
    create_file(parent_dir, filename, content)


def read_file(path: "str") -> "str":
    """Funkce ze zadané cesty přečte soubor a vrátí jeho obsah v podobě
    textového řetězce.
    Pokud na zadané cestě není soubor, ze kterého by šlo číst, je vyhozena
    výjimka.
    """
    if not exists(path):
        raise FileSystemError(
            f"Zadaná adresa není platná: zadaný soubor s cestou "
            f"'{path}' neexistuje", [path])
    try:
        file = open(path, "r")
        content = file.read()
        file.close()
        return content
    except Exception as e:
        raise FileSystemError(
            f"Chyba souboru: ze souboru {path} se nepovedlo číst; "
            f"{type(e).__name__}: {str(e)}", [path])


def read_file_by_lines(path: "str") -> "list[str]":
    """Funkce čte soubor po řádcích, které také v podobě seznamu textových
    řetězců vrací.
    Pokud na zadané cestě není soubor, ze kterého by šlo číst, je vyhozena
    výjimka.
    """
    if not exists(path):
        raise FileSystemError(
            f"Zadaná adresa není platná: zadaný soubor s cestou"
            f"'{path}' neexistuje", [path])
    try:
        lines = []
        file = open(path, "r")
        for line in file:
            lines.append(line)
        file.close()
        return lines
    except Exception as e:
        raise FileSystemError(
            f"Chyba souboru: ze souboru {path} se nepovedlo číst; "
            f"{type(e).__name__}: {str(e)}", [path])


def read_file_head(path: "str", n_lines: "int", strip: "bool" = False
                   ) -> "list[str]":
    """Funkce přečte jen zadaných několik řádků, které vrítá v podobě
    seznamu textových řetězců. Defaultní parametr 'strip' určuje, zda-li bílé
    znaky na konci a na začátku řádků mají být obsaženy. Defaultně zůstávají
    součástí jednotlivých řádků.
    Pokud soubor obsahuje více řádků, ty za stanovenou hranicí budou
    ignorovány. Pokud méně, budou vráceny všechny nalezené.
    Pokud bude zadáno záporné číslo řádků k přečtení, bude vyhozena výjimka,
    stejně jako když na zadané cestě není nalezen soubor ke čtení.
    """
    if n_lines < 0:
        raise FileSystemError(
            f"Nelze číst záporné číslo řádků: {n_lines}", [path])
    elif not exists(path):
        raise FileSystemError(
            f"Zadaná adresa není platná: zadaný soubor s cestou"
            f"'{path}' neexistuje", [path])
    else:
        try:
            with open(path, "r") as file:
                lines = []
                for line_index in range(n_lines):
                    lines.append(next(file).strip() if strip else next(file))
                return list(lines)
        except StopIteration as si:
            raise FileSystemError(f"Počet řádků k přečtení je vyšší, než "
                                  f"skutečný počet řádků v souboru.", [path])
        except Exception as e:
            raise FileSystemError(
                f"Chyba souboru: ze souboru {path} se nepovedlo "
                f"číst; {type(e).__name__}: '{str(e)}'", [path])


def deep_search_by_regex(path: "str", regex: "str",
                         include_directories: "bool" = True) -> "list[str]":
    """Funkce se pokusí hloubkově vyhledat všechny soubory dle definovaného
    regulárního výrazu. Seznam jejich absolutních cest, který je navrácen,
    reprezentuje nalezené adepty. Podle parametru 'include_directories' je
    možné zahrnout či vyloučit z výsledků adresáře.
    Příkladem regulárního výrazu pro získání seznamu všech Python skriptů je
    '^.*\.py$'. Tím budou získány i soubory '__init__.py'
    Pokud na zadané cestě 'path' není nalezen adresář, je vyhozena výjimka.
    """
    if is_directory(path):
        regex = re.compile(regex)
        all_files = deep_list_files(path, include_directories)
        return list(filter(lambda file: re.search(regex, file_basename(file)),
                           all_files))


def search_by_regex(path: str, regex: str,
                    include_directories: bool = True) -> "list[str]":
    """Funkce vrací seznam souborů, které odpovídají svým názvem dodanému
    regulárnímu výrazu. Navrácen je seznam absolutních cest.
    Pokud na zadané cestě 'path' není nalezen adresář, je vyhozena výjimka.
    """
    if is_directory(path):
        regex = re.compile(regex)
        files = list_files(path, False)
        return list(filter(lambda file: re.search(regex, file_basename(file)),
                           files))


def has_regex_name(path: str, regex: str, include_ext: bool = True) -> bool:
    """Funkce vrací boolean hodnotu vyjadřující to, zda-li soubor na dodané
    cestě odpovídá názvem regulárnímu výrazu. Funkce kromě toho umí rozlišovat,
    jestli má být do názvu zahrnuta i koncovka.

    Vstupem může být soubor nebo adresář, stejně jako neexistující objekt.
    """
    return re.search(re.compile(regex),
                     file_basename(path, include_ext)) is not None


def join_paths(path1: str, path2: str) -> str:
    """Funkce spojuje cesty do jedné. Typickým případem užití je spojení
    absolutní cesty (parametr 'path1') a relativní (parametr 'path2').
    """
    return os.path.join(path1, path2)


def join_path_in_project(relative_path: str) -> str:
    """Funkce spojuje absolutní cestu ke kořeni projektu s relativní cestou
    v rámci tohoto projektu.
    """
    return join_paths(root_directory_path(), relative_path)


def abs_to_relative(abs_path: str, rel_root: str) -> str:
    """Funkce převede absolutní cestu na relativní vůči dodanému bodu.
    Relativní cesta musí být adresářem, který obsahuje absolutní cestou
    odkazovaný objekt. Je-li tedy například absolutní cestou popsán soubor,
    musí dodaná absolutní cesta ukazovat na adresář, který přímo nebo v
    některém ze svých podadresářů daný soubor obsahuje. Funkce pracuje pouze
    s přímými cestami; výhradně vztah 'rodič-potomek', žádní sourozenci.
    Pokud dodaný relativní bod (kořen, od kterého se má dále cesta popisovat)
    není počátkem absolutní cesty, je vyhozena výjimka.
    Jsou rozlišována malá a velká písmena. Počáteční a koncové mezery jsou
    ořezány.
    """
    abs_path = abs_path.strip()
    rel_root = rel_root.strip()
    if not abs_path.startswith(rel_root):
        raise FileSystemError(f"Relativní kořenový adresář neobsahuje "
                              f"absolutní cestu", [rel_root, abs_path])
    else:
        return abs_path[len(rel_root) + 1:]


def absolute_to_project_rel(abs_path: str) -> str:
    """Funkce převede absolutní cestu k souborovému objektu na relativní cestu
    vůči kořeni projektu.
    Pokud cesta není (byť hypoteticky; cílový objekt nemusí existovat)
    obsažena v projektu, je vyhozena výjimka.
    """
    return abs_to_relative(abs_path, root_directory_path())


def module_path_from_abs(abs_path: str) -> str:
    """Funkce se pokusí převést absolutní cestu ke zdrojovému souboru na
    absolutní cestu v kontextu balíčků projektu.
    Konkrétně funkce převede absolutní cestu k souboru na relativní vůči
    projektu, nahradí v něm defaultní separátory pohybu v souborovém systému
    (typicky zpětná a dopředná lomítka) na tečky a odstraní koncovku souboru.
    Této funkce lze použít pro dynamické importování modulů z absolutních cest
    prohledaného adresáře uvnitř projektu.
    """
    return file_basename(
        absolute_to_project_rel(abs_path).replace(separator(), "."), False)


class FileSystemError(PlatformError):
    """FileSystemError je výjimka sloužící k specifičtější symbolizaci
    vzniklého problému v rámci souborového systému, který by narušil
    konzistentní chod systému.
    """

    def __init__(self, message: str, paths: "list[str]"):
        PlatformError.__init__(self, message)
        self._paths = paths

    @property
    def paths(self) -> "tuple[str]":
        """Vlastnost vracející cestu související se vznikem problému.
        """
        return tuple(self._paths)
