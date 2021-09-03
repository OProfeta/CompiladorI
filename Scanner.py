from Token import Token, TokenType

class Scanner():

    def __init__(self, input):
        with open(input) as arq:
            self.conteudo = arq.read()
            self.pos = 0

    def nextToken(self):
        if self.isEOF():
            return None

        estado = 0
        termo = ""
        token = None

        while True:
            c = self.nextChar()
            if c == 0:
                return None
            # print(f"pos: {self.pos} estado {estado}, c = {c}")
            if estado == 0:
                if self.isEspaco(c):
                    estado = 0
                elif self.isDigito(c):
                    estado = 1
                    termo += c
                elif self.isLetra(c):
                    estado = 3
                    termo += c
                elif c == '<' or c == '>' or c == ':':
                    termo += c
                    estado = 4
                else:
                    if c == 0:
                        return None
                    termo += c
                    token = Token()
                    token.tipo = TokenType.SIMBOLO
                    token.termo = termo
                    return token
            elif estado == 1:
                if self.isDigito(c):
                    estado = 1
                    termo += c
                elif c == '.':
                    estado = 2
                    termo += c
                else:
                    token = Token()
                    token.tipo = TokenType.NUMERO_INTEIRO
                    token.termo = termo
                    self.back()
                    return token
            elif estado == 2:
                if self.isDigito(c):
                    estado = 2
                    termo += c
                else:
                    token = Token()
                    token.tipo = TokenType.NUMERO_REAL
                    token.termo = termo
                    self.back()
                    return token
            elif estado == 3:
                if self.isLetra(c) or self.isDigito(c):
                    estado = 3
                    termo += c
                else:
                    token = Token()
                    token.tipo = TokenType.IDENTIFICADOR
                    token.termo = termo
                    self.back()
                    return token
            elif estado == 4:
                if (not self.isDigito(c)) and (not self.isLetra(c)) and (not self.isEspaco(c)):
                    estado = 4
                    termo += c
                else:
                    token = Token()
                    token.tipo = TokenType.SIMBOLO
                    token.termo = termo
                    self.back()
                    return token

    def isLetra(self, c):
        return (c >= 'a' and c <= 'z') or (c >= 'A' and c <= 'Z')

    def isEspaco(self, c):
        return c == ' ' or c == '\n' or c == '\t'

    def isDigito(self, c):
        return c >= '0' and c <= '9'

    def isEOF(self):
        return self.pos == len(self.conteudo)

    def nextChar(self):
        if self.isEOF():
            return 0
        tmp = self.pos
        self.pos += 1
        return self.conteudo[tmp]

    def back(self):
        if not self.isEOF():
            self.pos -= 1