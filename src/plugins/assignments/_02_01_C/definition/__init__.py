"""Smyslem této úlohy je ilustrovat, jak lze provádět cykly. Cyklus je ve své
podstatě konstrukce, která umožňuje opakovat specifikovaný kód.

Nyní si ukážeme, jak funguje cyklus while. Tento cyklus opakuje provádění
kódu specifikovaného ve svém těle, dokud je splněna podmínka.

Na následující ukázce je tento cyklus demonstrován:

    while [podmínka]:
        ... [kód, který bude opakován, dokud podmínka platí] ...

Nyní je však cílem navštívit všechna políčka. Svět je zjednodušen na
obdélníkovou podobu. Doporučeným postupem je navštívit všechna políčka
pomocí střídavých průchodů linií a postupným posouváním na další (ať už
horizontálně či vertikálně).

Toho lze dosáhnout například vnořením cyklu:

    while [podmínka1]:

        # dokud je splněna [podmínka1]
        ... [kód] ...

        while [podmínka2]:

            # dokud je splněna [podmínka2]
            ... [kód] ...

        # Když už [podmínka2] neplatí
        ... [kód] ...
"""



