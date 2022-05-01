"""V této úloze je požadováno, aby program posunul robota kupředu, nestojí-li
před stěnou. Pokud-že před stěnou stojí, posunout se naopak nesmí, protože by
naboural a rozbil se.

Proto je robot osazen jednotkami IsWallSensor, ForwardMover a LeftTurner. Nyní
je úkol podobný, jako v _01_01_C, tedy aby se robot otočil jediným směrem,
ve kterém se může posunout dopředu a posunul se v něm.

K tomu lze použít podprogram, vytvořit si vlastní pomocnou funkci, do které
lze zapouzdřit část programu z toho hlavního. Ilustraci tohoto postupu lze
vidět na následující ukázce:


    def run(robot, log, terminate):
        ... [hlavní kód programu] ...
        pomocna_funkce(robot, log, terminate)
        ... [hlavní kód programu] ...


    def pomocna_funkce(robot, log, terminate)
        ... [pomocný kód programu] ...

Problém ovšem nastane, není-li jediná taková cesta možná. Tedy je-li robot
obklopen stěnami a nikam nemůže. V takovém případě je nutné, aby program
upozornil na neřešitelnou situaci.
"""



