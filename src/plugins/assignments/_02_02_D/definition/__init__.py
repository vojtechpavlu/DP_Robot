"""Smyslem této úlohy je ilustrovat, jak lze provádět cykly. Cyklus je ve své
podstatě konstrukce, která umožňuje opakovat specifikovaný kód.


Naším úkolem nyní bude ujít přesně 5 kroků v již demonstrované chodbě. Robot
k tomu bude osazen opět jednotkou 'ForwardMover'. Problém je však ve samotné
specifikaci těch 5 kroků.

Nyní si připomeňme, jak lze použít cyklus for. Na následující ukázce lze vidět
dva ze způsobů jeho použití:


    for item in list_of_items:
        ... [kód, který se provede pro každou položku z dodaného seznamu] ...

nebo:

    for i in range(5):
        ... [kód, který se provede pro i = 0, 1, 2, 3, 4, tedy celkem 5x] ...


V obecnějším pojetí lze mluvit o následujícím použití:

    for [identifikátor položky] in [množina hodnot k iterování]:
        ... [kód, který může použít danou položku] ...


V rámci těla cyklu je pochopitelně možné přistupovat k té jedné položce z
mnoha, pro kterou tato iterace cyklus běží a lze s ní pracovat.

Klíčová je v druhém případě funkce 'range()', což je built-in funkce pro
generování aritmetické posloupnosti. Více se lze dočíst v dokumentaci:

FOR cyklus: https://docs.python.org/3/tutorial/controlflow.html#for-statements
range(): https://docs.python.org/3/tutorial/controlflow.html#the-range-function
"""



