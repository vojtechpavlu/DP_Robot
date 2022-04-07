"""V tomto modulu jsou obsaženy definice značkování políček."""



class Mark:
    """"""

    def __init__(self, text: str):
        """"""
        self._text = text

    @property
    def text(self) -> str:
        """"""
        return self._text

    @text.setter
    def text(self, text: str):
        """"""
        self._text = str(text)




