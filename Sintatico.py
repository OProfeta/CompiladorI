from io import SEEK_CUR
from Simbolo import Simbolo
from Token import Token, TokenType
from Scanner import Scanner

class Sintatico():

    lexico: Scanner
    simbolo: Token
    tipo: TokenType
    # tabelaSimbolo = {"nomeDoSimbolo": Simbolo}
    tabelaSimbolo = {}
    codigo = "operador;arg1;arg2;result\n"
    temp = 1

    palavrasReservadas = [
        "program",
        "begin",
        "end",
        "real",
        "integer",
        "read",
        "write",
        "if",
        "then",
        "else"
    ]

    listaIfs = []
    posListaIfs = -1
    tlmode = False
    flmode = False

    def __init__(self, arq) -> None:
        self.lexico = Scanner(arq)

    def geratemp(self):
        t = "t" + str(self.temp)
        self.temp += 1
        return t

    def code(self, op, arg1, arg2, result):
        codigoGerado = f"{op};{arg1};{arg2};{result}\n"
        if not self.tlmode and not self.flmode:
            self.codigo += codigoGerado
        elif self.tlmode:
            self.listaIfs[self.posListaIfs][0] += codigoGerado
        elif self.flmode:
            self.listaIfs[self.posListaIfs][1] += codigoGerado

    def geraLista(self):
        self.posListaIfs += 1
        self.listaIfs.append(["",""])

    def deletaLista(self):
        del self.listaIfs[self.posListaIfs]
        self.posListaIfs -= 1

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

    # <programa> -> program ident <corpo> .
    def programa(self):
        if self.verificaSimbolo("program"):
            self.obtemSimbolo()
            
            if self.simbolo.tipo == TokenType.IDENTIFICADOR and (not self.simbolo.termo in self.palavrasReservadas):
                self.obtemSimbolo()

                self.corpo()

                if self.verificaSimbolo("."):
                    self.code("PARA", "", "", "")
                    self.obtemSimbolo()
                else:
                    raise RuntimeError(f"Erro sintático, esperado '.', encontrado: {self.simbolo.termo}")
            else:
                raise RuntimeError(f"Erro sintático, esperado '{TokenType.IDENTIFICADOR.name}', encontrado: '{self.simbolo.termo}'")
        else:
            raise RuntimeError(f"Erro sintático, esperado 'program', encontrado: {self.simbolo.termo}")
        
    # <corpo> -> <dc> begin <comandos> end
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

    # <dc> -> <dc_v> <mais_dc>  | λ
    def dc(self):
        if self.verificaSimbolo("real") or self.verificaSimbolo("integer"):
            self.dc_v()

            self.mais_dc()
        else:
            # Retorno vazio
            pass
        
    # <mais_dc> -> ; <dc> | λ
    def mais_dc(self):
        if self.verificaSimbolo(";"):
            self.obtemSimbolo()

            self.dc()
        else:
            # Retorno vazio
            pass

    # <dc_v> ->  <tipo_var> : <variaveis>
    def dc_v(self):
        self.tipo_var()

        if self.verificaSimbolo(":"):
            self.obtemSimbolo()

            self.variaveis()
        else:
            raise RuntimeError(f"Erro sintático, esperado ':', encontrado: {self.simbolo.termo}")

    # <tipo_var> -> real | integer
    def tipo_var(self):
        if self.verificaSimbolo("real"):
            self.tipo = TokenType.NUMERO_REAL
            self.obtemSimbolo()
        elif self.verificaSimbolo("integer"):
            self.tipo = TokenType.NUMERO_INTEIRO
            self.obtemSimbolo()
        else:
            raise RuntimeError(f"Erro sintático, esperado 'real' ou 'integer', encontrado: {self.simbolo.termo}")

    # <variaveis> -> ident <mais_var>
    def variaveis(self):
        
        if self.simbolo.tipo == TokenType.IDENTIFICADOR and (not self.simbolo.termo in self.palavrasReservadas):
            if self.simbolo.termo in self.tabelaSimbolo:
                raise RuntimeError(f"Erro semântico, variável {self.simbolo.termo} já declarada.")
            else:
                self.tabelaSimbolo[self.simbolo.termo] = Simbolo(self.tipo, self.simbolo.termo)
                if self.tipo == TokenType.NUMERO_INTEIRO:
                    self.code("ALME", "0", "", self.simbolo.termo)
                else:
                    self.code("ALME", "0.0", "", self.simbolo.termo)

            self.obtemSimbolo()

            self.mais_var()
        else:
            raise RuntimeError(f"Erro sintático, esperado '{TokenType.IDENTIFICADOR.name}', encontrado: '{self.simbolo.termo}'")

    # <mais_var> -> , <variaveis> | λ
    def mais_var(self):
        if self.verificaSimbolo(","):
            self.obtemSimbolo()

            self.variaveis()
        else:
            # Retorno vazio
            pass

    # <comandos> -> <comando> <mais_comandos>
    def comandos(self):
        self.comando()
        self.mais_comandos()

    # <mais_comandos> -> ; <comandos> | λ
    def mais_comandos(self):
        if self.verificaSimbolo(";"):
            self.obtemSimbolo()

            self.comandos()
        else:
            # Retorno vazio
            pass

    # <comando> -> read (ident) |
	#			   write (ident) |
	#			   ident := <expressao> |
	#			   if <condicao> then <comandos> <pfalsa> $
    def comando(self):
        if self.verificaSimbolo("read"):
            self.obtemSimbolo()

            if self.verificaSimbolo("("):
                self.obtemSimbolo()

                
                if self.simbolo.tipo == TokenType.IDENTIFICADOR and (not self.simbolo.termo in self.palavrasReservadas):
                    self.code("read", "", "", self.simbolo.termo)
                    self.obtemSimbolo()

                    if self.verificaSimbolo(")"):
                        self.obtemSimbolo()
                        
                    else:
                        raise RuntimeError(f"Erro sintático, esperado ')', encontrado: {self.simbolo.termo}")
                else:
                    raise RuntimeError(f"Erro sintático, esperado '{TokenType.IDENTIFICADOR.name}', encontrado: '{self.simbolo.termo}'")
            else:
                raise RuntimeError(f"Erro sintático, esperado '(', encontrado: {self.simbolo.termo}")

        elif self.verificaSimbolo("write"):
            self.obtemSimbolo()

            if self.verificaSimbolo("("):
                self.obtemSimbolo()

                
                if self.simbolo.tipo == TokenType.IDENTIFICADOR and (not self.simbolo.termo in self.palavrasReservadas):
                    self.code("write", self.simbolo.termo, "", "")
                    self.obtemSimbolo()

                    if self.verificaSimbolo(")"):
                        self.obtemSimbolo()
                    else:
                        raise RuntimeError(f"Erro sintático, esperado ')', encontrado: {self.simbolo.termo}")
                else:
                    raise RuntimeError(f"Erro sintático, esperado '{TokenType.IDENTIFICADOR.name}', encontrado: '{self.simbolo.termo}'")
            else:
                raise RuntimeError(f"Erro sintático, esperado '(', encontrado: {self.simbolo.termo}")

        elif self.verificaSimbolo("if"):
            self.geraLista()
            self.obtemSimbolo()

            condicaoDir = self.condicao()
            
            if self.verificaSimbolo("then"):
                self.obtemSimbolo()

                self.tlmode = True
                self.flmode = False
                self.comandos()

                self.tlmode = False
                self.flmode = True
                self.pfalsa()
                
                if self.verificaSimbolo("$"):
                    self.tlmode = False
                    self.flmode = False
                    # gerar o codigo do if-else de verdade

                    linhaJF = self.codigo.count('\n')
                    quantInstThen = self.listaIfs[self.posListaIfs][0].count('\n')
                    quantInstElse = self.listaIfs[self.posListaIfs][1].count('\n')

                    self.code("JF", condicaoDir, linhaJF+quantInstThen+1, "")
                    self.codigo += self.listaIfs[self.posListaIfs][0]
                    self.code("goto", linhaJF+quantInstThen+quantInstElse+1, "", "")
                    self.codigo += self.listaIfs[self.posListaIfs][1]

                    self.deletaLista()
                    self.obtemSimbolo()
                else:
                    raise RuntimeError(f"Erro sintático, esperado '$', encontrado: {self.simbolo.termo}")
            else:
                raise RuntimeError(f"Erro sintático, esperado 'then', encontrado: {self.simbolo.termo}")
        
        elif self.simbolo.tipo == TokenType.IDENTIFICADOR and (not self.simbolo.termo in self.palavrasReservadas):
            id = self.simbolo.termo
            self.obtemSimbolo()
            if self.verificaSimbolo(":="):
                self.obtemSimbolo()

                expressaoDir = self.expressao()
                self.code(":=", expressaoDir, "", id)
            else:
                raise RuntimeError(f"Erro sintático, esperado ':=', encontrado: {self.simbolo.termo}")
        else:
            raise RuntimeError(f"Erro sintático, esperado 'read' ou 'write' ou 'if' ou '{TokenType.IDENTIFICADOR}', encontrado: '{self.simbolo.termo}' - tipo {self.simbolo.tipo.name}")

    # <condicao> -> <expressao> <relacao> <expressao>
    def condicao(self):
        expressaoDir = self.expressao()
        relacaoDir = self.relacao()
        expressaoLinhaDir = self.expressao()
        t = self.geratemp()
        self.code(relacaoDir, expressaoDir, expressaoLinhaDir, t)
        return t

    # <relacao> -> = | <> | >= | <= | > | <
    def relacao(self):
        if self.verificaSimbolo("="):
            self.obtemSimbolo()
            return "="
        elif self.verificaSimbolo("<>"):
            self.obtemSimbolo()
            return "<>"
        elif self.verificaSimbolo(">="):
            self.obtemSimbolo()
            return ">="
        elif self.verificaSimbolo("<="):
            self.obtemSimbolo()
            return "<="
        elif self.verificaSimbolo(">"):
            self.obtemSimbolo()
            return ">"
        elif self.verificaSimbolo("<"):
            self.obtemSimbolo()
            return "<"
        else:
            raise RuntimeError(f"Erro sintático, esperado '=', '<>', '>=', '<=', '>' ou '<', encontrado: {self.simbolo.termo}")

    # <expressao> -> <termo> <outros_termos>
    def expressao(self):
        outros_termosEsq = self.termo()
        expressaoDir = self.outros_termos(outros_termosEsq)
        return expressaoDir

    # <termo> -> <op_un> <fator> <mais_fatores>
    def termo(self):
        op_unDir = self.op_un()
        fatorDir = self.fator(op_unDir)
        termoDir = self.mais_fatores(fatorDir)
        return termoDir

    # <op_un> -> - | λ
    def op_un(self):
        if self.verificaSimbolo("-"):
            self.obtemSimbolo()
            return "-"
        else:
            # Retorno vazio
            return None

    # <fator> -> ident | numero_int | numero_real | (<expressao>)
    def fator(self, fatorEsq):
        
        if self.simbolo.tipo == TokenType.IDENTIFICADOR and (not self.simbolo.termo in self.palavrasReservadas):
            if fatorEsq == "-":
                t = self.geratemp()
                self.code("uminus", self.simbolo.termo, "", t)
                fatorDir = t
            else:
                fatorDir = self.simbolo.termo
            self.obtemSimbolo()
            return fatorDir
        elif self.simbolo.tipo == TokenType.NUMERO_INTEIRO:
            if fatorEsq == "-":
                t = self.geratemp()
                self.code("uminus", self.simbolo.termo, "", t)
                fatorDir = t
            else:
                fatorDir = self.simbolo.termo
            self.obtemSimbolo()
            return fatorDir
        elif self.simbolo.tipo == TokenType.NUMERO_REAL:
            if fatorEsq == "-":
                t = self.geratemp()
                self.code("uminus", self.simbolo.termo, "", t)
                fatorDir = t
            else:
                fatorDir = self.simbolo.termo
            self.obtemSimbolo()
            return fatorDir
        elif self.verificaSimbolo("("):
            self.obtemSimbolo()

            expressaoDir = self.expressao()
            if fatorEsq == "-":
                t = self.geratemp()
                self.code("uminus", expressaoDir, "", t)
                fatorDir = t
            else:
                fatorDir = expressaoDir
            
            if self.verificaSimbolo(")"):
                self.obtemSimbolo()
                return fatorDir
            else:
                raise RuntimeError(f"Erro sintático, esperado ')', encontrado: {self.simbolo.termo}")
        else:
            raise RuntimeError(f"Erro sintático, esperado '{TokenType.IDENTIFICADOR}', '{TokenType.NUMERO_INTEIRO}', '{TokenType.NUMERO_REAL}' ou '(', encontrado: '{self.simbolo.termo}' - tipo {self.simbolo.tipo.name}")

    # <outros_termos> -> <op_ad> <termo> <outros_termos> | λ
    def outros_termos(self, outros_termosEsq):
        if self.verificaSimbolo("+") or self.verificaSimbolo("-"):
            op_adDir = self.op_ad()
            termoDir = self.termo()
            t = self.geratemp()
            self.code(op_adDir, outros_termosEsq, termoDir, t)
            outros_termosDir = self.outros_termos(t)
            return outros_termosDir
        else:
            # Retorno vazio
            return outros_termosEsq

    # <op_ad> -> + | -
    def op_ad(self):
        if self.verificaSimbolo("+"):
            self.obtemSimbolo()
            return "+"
        elif self.verificaSimbolo("-"):
            self.obtemSimbolo()
            return "-"
        else:
            raise RuntimeError(f"Erro sintático, esperado '+' ou '-', encontrado: {self.simbolo.termo}")

    # <mais_fatores> -> <op_mul> <fator> <mais_fatores> | λ
    def mais_fatores(self, mais_fatoresEsq):
        if self.verificaSimbolo("*") or self.verificaSimbolo("/"):
            op_mulDir = self.op_mul()
            fatorDir = self.fator(None)
            t = self.geratemp()
            self.code(op_mulDir, mais_fatoresEsq, fatorDir, t)
            mais_fatoresDir = self.mais_fatores(t)
            return mais_fatoresDir
        else:
            # Retorno vazio
            return mais_fatoresEsq

    # <op_mul> -> * | /
    def op_mul(self):
        if self.verificaSimbolo("*"):
            self.obtemSimbolo()
            return "*"
        elif self.verificaSimbolo("/"):
            self.obtemSimbolo()
            return "/"
        else:
            raise RuntimeError(f"Erro sintático, esperado '*' ou '/', encontrado: {self.simbolo.termo}")

    # <pfalsa> -> else <comandos> | λ
    def pfalsa(self):
        if self.verificaSimbolo("else"):
            self.obtemSimbolo()

            self.comandos()
        else:
            # Retorno vazio
            pass
        

