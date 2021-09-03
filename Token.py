from enum import Enum

class TokenType(Enum):
    IDENTIFICADOR = 0
    NUMERO_INTEIRO = 1
    NUMERO_REAL = 2
    SIMBOLO = 3


class Token():

    tipo: TokenType
    termo: str

    def toString(self):
        return "Token [" + self.tipo.name + ", " + self.termo + "]"
