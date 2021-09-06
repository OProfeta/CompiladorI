from Token import TokenType

class Simbolo():

    tipo: TokenType
    nome: str

    def __init__(self, tipo, nome):
        self.tipo = tipo
        self.nome = nome

    def __repr__(self) -> str:
        return f"{self.nome} = {self.tipo.name}"