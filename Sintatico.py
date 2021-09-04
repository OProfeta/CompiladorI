from os import SEEK_HOLE
from Token import Token, TokenType
from Scanner import Scanner

class Sintatico():

    def __init__(self, arq) -> None:
        self.lexico = Scanner(arq)

    def analisar(self):
        self.obtemSimbolo()
        self.programa()
        if self.simbolo == None:
            print("Cadeia analisada com sucesso!")
        else:
            raise RuntimeError(f"Erro sintático, esperado fim de cadeia, encontrado: {self.simbolo.termo}")

    def obtemSimbolo(self):
        self.simbolo = self.lexico.nextToken()

    def verificaSimbolo(self, termo):
        return self.simbolo != None and self.simbolo.termo == termo

    def programa(self):
        if self.verificaSimbolo("program"):
            self.obtemSimbolo()
            # TODO: Mudar para nao passar palavras reservadas
            if self.simbolo.tipo == TokenType.IDENTIFICADOR:
                self.obtemSimbolo()

                self.corpo()

                if self.verificaSimbolo("."):
                    self.obtemSimbolo()
                else:
                    raise RuntimeError(f"Erro sintático, esperado '.', encontrado: {self.simbolo.termo}")
            else:
                raise RuntimeError(f"Erro sintático, esperado '{TokenType.IDENTIFICADOR.name}', encontrado: {self.simbolo.tipo.name}")
        else:
            raise RuntimeError(f"Erro sintático, esperado 'program', encontrado: {self.simbolo.termo}")
        
    def corpo(self):
        self.dc()

        if self.verificaSimbolo("begin"):
            self.obtemSimbolo()

            self.comandos()
            
            if self.verificaSimbolo("end"):
                self.obtemSimbolo()
            else:
                raise RuntimeError(f"Erro sintático, esperado 'end', encontrado: {self.simbolo.termo}")
        else:
            raise RuntimeError(f"Erro sintático, esperado 'begin', encontrado: {self.simbolo.termo}")

    def dc(self):
        if self.verificaSimbolo("real") or self.verificaSimbolo("integer"):
            self.dc_v()

            self.mais_dc()
        else:
            # Retorno vazio
            pass
        
    def mais_dc(self):
        if self.verificaSimbolo(";"):
            self.obtemSimbolo()

            self.dc()
        else:
            # Retorno vazio
            pass

    def dc_v(self):
        self.tipo_var()

        if self.verificaSimbolo(":"):
            self.obtemSimbolo()

            self.variaveis()
        else:
            raise RuntimeError(f"Erro sintático, esperado ':', encontrado: {self.simbolo.termo}")

    def tipo_var(self):
        if self.verificaSimbolo("real"):
            self.obtemSimbolo()
        elif self.verificaSimbolo("integer"):
            self.obtemSimbolo()
        else:
            raise RuntimeError(f"Erro sintático, esperado 'real' ou 'integer', encontrado: {self.simbolo.termo}")

    def variaveis(self):
        # TODO: Mudar para nao passar palavras reservadas
        if self.simbolo.tipo == TokenType.IDENTIFICADOR:
            self.obtemSimbolo()

            self.mais_var()
        else:
            raise RuntimeError(f"Erro sintático, esperado '{TokenType.IDENTIFICADOR.name}', encontrado: {self.simbolo.tipo.name}")

    def mais_var(self):
        if self.verificaSimbolo(","):
            self.obtemSimbolo()

            self.variaveis()
        else:
            # Retorno vazio
            pass

    def comandos(self):
        self.comando()
        self.mais_comandos()

    def mais_comandos(self):
        if self.verificaSimbolo(";"):
            self.obtemSimbolo()

            self.comandos()
        else:
            # Retorno vazio
            pass

    def comando(self):
        if self.verificaSimbolo("read"):
            self.obtemSimbolo()

            if self.verificaSimbolo("("):
                self.obtemSimbolo()

                # TODO: Mudar para nao passar palavras reservadas
                if self.simbolo.tipo == TokenType.IDENTIFICADOR:
                    self.obtemSimbolo()

                    if self.verificaSimbolo(")"):
                        self.obtemSimbolo()
                        
                    else:
                        raise RuntimeError(f"Erro sintático, esperado ')', encontrado: {self.simbolo.termo}")
                else:
                    raise RuntimeError(f"Erro sintático, esperado '{TokenType.IDENTIFICADOR.name}', encontrado: {self.simbolo.tipo.name}")
            else:
                raise RuntimeError(f"Erro sintático, esperado '(', encontrado: {self.simbolo.termo}")

        elif self.verificaSimbolo("write"):
            self.obtemSimbolo()

            if self.verificaSimbolo("("):
                self.obtemSimbolo()

                # TODO: Mudar para nao passar palavras reservadas
                if self.simbolo.tipo == TokenType.IDENTIFICADOR:
                    self.obtemSimbolo()

                    if self.verificaSimbolo(")"):
                        self.obtemSimbolo()
                    else:
                        raise RuntimeError(f"Erro sintático, esperado ')', encontrado: {self.simbolo.termo}")
                else:
                    raise RuntimeError(f"Erro sintático, esperado '{TokenType.IDENTIFICADOR.name}', encontrado: {self.simbolo.tipo.name}")
            else:
                raise RuntimeError(f"Erro sintático, esperado '(', encontrado: {self.simbolo.termo}")

        elif self.verificaSimbolo("if"):
            self.obtemSimbolo()

            self.condicao()
            
            if self.verificaSimbolo("then"):
                self.obtemSimbolo()

                self.comandos()
                self.pfalsa()
                
                if self.verificaSimbolo("$"):
                    self.obtemSimbolo()
                else:
                    raise RuntimeError(f"Erro sintático, esperado '$', encontrado: {self.simbolo.termo}")
            else:
                raise RuntimeError(f"Erro sintático, esperado 'then', encontrado: {self.simbolo.termo}")
        # TODO: Mudar para nao passar palavras reservadas
        elif self.simbolo.tipo == TokenType.IDENTIFICADOR:
            self.obtemSimbolo()
            if self.verificaSimbolo(":="):
                self.obtemSimbolo()

                self.expressao()
            else:
                raise RuntimeError(f"Erro sintático, esperado ':=', encontrado: {self.simbolo.termo}")
        else:
            raise RuntimeError(f"Erro sintático, esperado 'read' ou 'write' ou 'if' ou '{TokenType.IDENTIFICADOR}', encontrado: {self.simbolo.termo} - tipo {self.simbolo.tipo.name}")

    def condicao(self):
        self.expressao()
        self.relacao()
        self.expressao()

    def relacao(self):
        if self.verificaSimbolo("="):
            self.obtemSimbolo()
        elif self.verificaSimbolo("<>"):
            self.obtemSimbolo()
        elif self.verificaSimbolo(">="):
            self.obtemSimbolo()
        elif self.verificaSimbolo("<="):
            self.obtemSimbolo()
        elif self.verificaSimbolo(">"):
            self.obtemSimbolo()
        elif self.verificaSimbolo("<"):
            self.obtemSimbolo()
        else:
            raise RuntimeError(f"Erro sintático, esperado '=', '<>', '>=', '<=', '>' ou '<', encontrado: {self.simbolo.termo}")

    def expressao(self):
        self.termo()
        self.outros_termos()

    def termo(self):
        self.op_un()
        self.fator()
        self.mais_fatores()

    def op_un(self):
        if self.verificaSimbolo("-"):
            self.obtemSimbolo()
        else:
            # Retorno vazio
            pass

    def fator(self):
        # TODO: Mudar para nao passar palavras reservadas
        if self.simbolo.tipo == TokenType.IDENTIFICADOR:
            self.obtemSimbolo()
        elif self.simbolo.tipo == TokenType.NUMERO_INTEIRO:
            self.obtemSimbolo()
        elif self.simbolo.tipo == TokenType.NUMERO_REAL:
            self.obtemSimbolo()
        elif self.verificaSimbolo("("):
            self.obtemSimbolo()

            self.expressao()
            
            if self.verificaSimbolo(")"):
                self.obtemSimbolo()
            else:
                raise RuntimeError(f"Erro sintático, esperado ')', encontrado: {self.simbolo.termo}")
        else:
            raise RuntimeError(f"Erro sintático, esperado '{TokenType.IDENTIFICADOR}', '{TokenType.NUMERO_INTEIRO}', '{TokenType.NUMERO_REAL}' ou '(', encontrado: {self.simbolo.termo} - tipo {self.simbolo.tipo.name}")

    def outros_termos(self):
        if self.verificaSimbolo("+") or self.verificaSimbolo("-"):
            self.op_ad()
            self.termo()
            self.outros_termos()
        else:
            # Retorno vazio
            pass

    def op_ad(self):
        if self.verificaSimbolo("+"):
            self.obtemSimbolo()
        elif self.verificaSimbolo("-"):
            self.obtemSimbolo()
        else:
            raise RuntimeError(f"Erro sintático, esperado '+' ou '-', encontrado: {self.simbolo.termo}")

    def mais_fatores(self):
        if self.verificaSimbolo("*") or self.verificaSimbolo("/"):
            self.op_mul()
            self.fator()
            self.mais_fatores()
        else:
            # Retorno vazio
            pass

    def op_mul(self):
        if self.verificaSimbolo("*"):
            self.obtemSimbolo()
        elif self.verificaSimbolo("/"):
            self.obtemSimbolo()
        else:
            raise RuntimeError(f"Erro sintático, esperado '*' ou '/', encontrado: {self.simbolo.termo}")

    def pfalsa(self):
        if self.verificaSimbolo("else"):
            self.obtemSimbolo()

            self.comandos()
        else:
            # Retorno vazio
            pass
        

