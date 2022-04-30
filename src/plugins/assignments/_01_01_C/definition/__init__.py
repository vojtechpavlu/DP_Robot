"""V této úloze je požadováno, aby program posunul robota kupředu, nestojí-li
před stěnou. Pokud-že před stěnou stojí, posunout se naopak nesmí, protože by
naboural a rozbil se.

Proto je robot osazen jednotkami IsWallSensor, ForwardMover a LeftTurner.

Kromě toho je dobré, aby program sám rozpoznal, že úkol splnil, a samostatně
se ukončil. Toho lze docílit hned několika způsoby. Zde jsou zmíněny dva:


    def run(robot, log, terminate):
        ... [kód, který se provádí] ...
        return


respektive:


    def run(robot, log, terminate):
        ... [kód, který se provádí] ...
        terminate("Úspěšně jsem splnil svůj úkol", SUCCESS)
"""



