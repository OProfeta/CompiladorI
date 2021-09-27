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
        return f"{op};{arg1};{arg2};{result}\n"

    def analisar(self):
        self.obtemSimbolo()
        codigoPrograma = self.programa()
        if self.simbolo == None:
            # print("Cadeia analisada com sucesso!")
            self.codigo = codigoPrograma
            self.codigoArrumado = []
            
            # fazendo patch up do codigo intermediario
            for nLinha, linha in enumerate(self.codigo.split('\n')):
                underlineIndex = linha.find("_")
                if underlineIndex == -1:
                    self.codigoArrumado.append(linha)
                    continue
                pontovirgulaIndex = linha.find(";", underlineIndex)
                tamanho = int(linha[underlineIndex+1:pontovirgulaIndex])
                novaLinha = linha[:underlineIndex] + str(tamanho+nLinha) + linha[pontovirgulaIndex+len(str(tamanho))-1:]
                self.codigoArrumado.append(novaLinha)
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

                corpoCodigo = self.corpo()

                if self.verificaSimbolo("."):
                    codigoGerado = corpoCodigo
                    codigoGerado += self.code("PARA", "", "", "")
                    self.obtemSimbolo()
                    return codigoGerado
                else:
                    raise RuntimeError(f"Erro sintático, esperado '.', encontrado: {self.simbolo.termo}")
            else:
                raise RuntimeError(f"Erro sintático, esperado '{TokenType.IDENTIFICADOR.name}', encontrado: '{self.simbolo.termo}'")
        else:
            raise RuntimeError(f"Erro sintático, esperado 'program', encontrado: {self.simbolo.termo}")
        
    # <corpo> -> <dc> begin <comandos> end
    def corpo(self):
        
        dcCodigo = self.dc()

        if self.verificaSimbolo("begin"):
            self.obtemSimbolo()

            comandosCodigo = self.comandos(dcCodigo)
            
            if self.verificaSimbolo("end"):
                self.obtemSimbolo()
                return comandosCodigo
            else:
                raise RuntimeError(f"Erro sintático, esperado 'end', encontrado: {self.simbolo.termo}")
        else:
            raise RuntimeError(f"Erro sintático, esperado 'begin', encontrado: {self.simbolo.termo}")

    # <dc> -> <dc_v> <mais_dc>  | λ
    def dc(self):
        if self.verificaSimbolo("real") or self.verificaSimbolo("integer"):
            dc_vCodigo = self.dc_v()

            mais_dcCodigo = self.mais_dc()

            return dc_vCodigo + mais_dcCodigo
        else:
            return ""
        
    # <mais_dc> -> ; <dc> | λ
    def mais_dc(self):
        if self.verificaSimbolo(";"):
            self.obtemSimbolo()

            dcCodigo = self.dc()
            return dcCodigo
        else:
            # Retorno vazio
            return ""

    # <dc_v> ->  <tipo_var> : <variaveis>
    def dc_v(self):
        tipos_varDir = self.tipo_var()

        if self.verificaSimbolo(":"):
            self.obtemSimbolo()

            variaveisCodigo = self.variaveis(tipos_varDir)
            return variaveisCodigo
        else:
            raise RuntimeError(f"Erro sintático, esperado ':', encontrado: {self.simbolo.termo}")

    # <tipo_var> -> real | integer
    def tipo_var(self):
        if self.verificaSimbolo("real"):
            self.obtemSimbolo()
            return TokenType.NUMERO_REAL
        elif self.verificaSimbolo("integer"):
            self.obtemSimbolo()
            return TokenType.NUMERO_INTEIRO
        else:
            raise RuntimeError(f"Erro sintático, esperado 'real' ou 'integer', encontrado: {self.simbolo.termo}")

    # <variaveis> -> ident <mais_var>
    def variaveis(self, variaveisEsq):
        
        if self.simbolo.tipo == TokenType.IDENTIFICADOR and (not self.simbolo.termo in self.palavrasReservadas):
            if self.simbolo.termo in self.tabelaSimbolo:
                raise RuntimeError(f"Erro semântico, variável {self.simbolo.termo} já declarada.")
            else:
                self.tabelaSimbolo[self.simbolo.termo] = Simbolo(variaveisEsq, self.simbolo.termo)
                if variaveisEsq == TokenType.NUMERO_INTEIRO:
                    codigoGerado = self.code("ALME", "0", "", self.simbolo.termo)
                else:
                    codigoGerado = self.code("ALME", "0.0", "", self.simbolo.termo)

            self.obtemSimbolo()

            mais_varCodigo = self.mais_var(variaveisEsq)
            return codigoGerado + mais_varCodigo
        else:
            raise RuntimeError(f"Erro sintático, esperado '{TokenType.IDENTIFICADOR.name}', encontrado: '{self.simbolo.termo}'")

    # <mais_var> -> , <variaveis> | λ
    def mais_var(self, mais_varEsq):
        if self.verificaSimbolo(","):
            self.obtemSimbolo()

            variaveisCodigo = self.variaveis(mais_varEsq)
            return variaveisCodigo
        else:
            # Retorno vazio
            return ""

    # <comandos> -> <comando> <mais_comandos>
    def comandos(self, codigoGerado):
        comandoCodigo = self.comando(codigoGerado)

        mais_comandosCodigo = self.mais_comandos(comandoCodigo)

        return mais_comandosCodigo

    # <mais_comandos> -> ; <comandos> | λ
    def mais_comandos(self, codigoGerado):
        if self.verificaSimbolo(";"):
            self.obtemSimbolo()

            comandosCodigo = self.comandos(codigoGerado)
            codigoGerado = comandosCodigo
            return codigoGerado
        else:
            # Retorno vazio
            return codigoGerado

    # <comando> -> read (ident) |
	#			   write (ident) |
	#			   ident := <expressao> |
	#			   if <condicao> then <comandos> <pfalsa> $
    def comando(self, codigoGerado):
        if self.verificaSimbolo("read"):
            self.obtemSimbolo()

            if self.verificaSimbolo("("):
                self.obtemSimbolo()

                
                if self.simbolo.tipo == TokenType.IDENTIFICADOR and (not self.simbolo.termo in self.palavrasReservadas):
                    if not self.simbolo.termo in self.tabelaSimbolo:
                        raise RuntimeError(f"Erro semântico: variável '{self.simbolo.termo}' não foi declarada.")
                    codigoGerado += self.code("read", "", "", self.simbolo.termo)
                    self.obtemSimbolo()

                    if self.verificaSimbolo(")"):
                        self.obtemSimbolo()
                        return codigoGerado
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
                    if not self.simbolo.termo in self.tabelaSimbolo:
                        raise RuntimeError(f"Erro semântico: variável '{self.simbolo.termo}' não foi declarada.")
                    codigoGerado += self.code("write", self.simbolo.termo, "", "")
                    self.obtemSimbolo()

                    if self.verificaSimbolo(")"):
                        self.obtemSimbolo()
                        return codigoGerado
                    else:
                        raise RuntimeError(f"Erro sintático, esperado ')', encontrado: {self.simbolo.termo}")
                else:
                    raise RuntimeError(f"Erro sintático, esperado '{TokenType.IDENTIFICADOR.name}', encontrado: '{self.simbolo.termo}'")
            else:
                raise RuntimeError(f"Erro sintático, esperado '(', encontrado: {self.simbolo.termo}")

        elif self.verificaSimbolo("if"):
            self.obtemSimbolo()

            condicaoCodigo, condicaoDir = self.condicao()
            
            if self.verificaSimbolo("then"):
                self.obtemSimbolo()

                codigoGerado += condicaoCodigo
                codigoGerado += self.code("JF", condicaoDir, "__", "")

                comandosCodigo = self.comandos(codigoGerado)

                comandosSomente = comandosCodigo.replace(codigoGerado, "")
                tamanhoThen = comandosSomente.count('\n')
                index = codigoGerado.rfind("__")
                codigoGerado = codigoGerado[:index] + f"_{tamanhoThen+2}" + codigoGerado[index+2:]

                codigoGerado += comandosSomente

                codigoGerado += self.code("goto", "__", "", "")
                pfalsaCodigo = self.pfalsa(codigoGerado)

                pfalsaSomente = pfalsaCodigo.replace(codigoGerado, "")
                tamanhoElse = pfalsaSomente.count('\n')
                index = codigoGerado.rfind("__")
                codigoGerado = codigoGerado[:index] + f"_{tamanhoElse+1}" + codigoGerado[index+2:]
                
                codigoGerado += pfalsaSomente

                if self.verificaSimbolo("$"):
                    self.obtemSimbolo()
                    return codigoGerado
                else:
                    raise RuntimeError(f"Erro sintático, esperado '$', encontrado: {self.simbolo.termo}")
            else:
                raise RuntimeError(f"Erro sintático, esperado 'then', encontrado: {self.simbolo.termo}")
        
        elif self.simbolo.tipo == TokenType.IDENTIFICADOR and (not self.simbolo.termo in self.palavrasReservadas):
            if not self.simbolo.termo in self.tabelaSimbolo:
                raise RuntimeError(f"Erro semântico: variável '{self.simbolo.termo}' não foi declarada.")
            id = self.simbolo.termo
            self.obtemSimbolo()
            if self.verificaSimbolo(":="):
                self.obtemSimbolo()

                expressaoCodigo, expressaoDir = self.expressao()
                codigoGerado += expressaoCodigo
                codigoGerado += self.code(":=", expressaoDir, "", id)
                return codigoGerado
            else:
                raise RuntimeError(f"Erro sintático, esperado ':=', encontrado: {self.simbolo.termo}")
        else:
            raise RuntimeError(f"Erro sintático, esperado 'read' ou 'write' ou 'if' ou '{TokenType.IDENTIFICADOR}', encontrado: '{self.simbolo.termo}' - tipo {self.simbolo.tipo.name}")

    # <condicao> -> <expressao> <relacao> <expressao>
    def condicao(self):
        expressaoCodigo, expressaoDir = self.expressao()
        relacaoDir = self.relacao()
        expressaoLinhaCodigo, expressaoLinhaDir = self.expressao()
        t = self.geratemp()
        codigoGerado = expressaoCodigo + expressaoLinhaCodigo
        codigoGerado += self.code(relacaoDir, expressaoDir, expressaoLinhaDir, t)
        return codigoGerado, t

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
        termoCodigo, termoDir = self.termo()
        outros_termosCodigo, expressaoDir = self.outros_termos(termoDir)
        codigoGerado = termoCodigo + outros_termosCodigo
        return codigoGerado, expressaoDir

    # <termo> -> <op_un> <fator> <mais_fatores>
    def termo(self):
        op_unDir = self.op_un()
        fatorCodigo, fatorDir = self.fator(op_unDir)
        mais_fatoresCodigo, termoDir = self.mais_fatores(fatorDir)
        return fatorCodigo + mais_fatoresCodigo, termoDir

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
            if not self.simbolo.termo in self.tabelaSimbolo:
                raise RuntimeError(f"Erro semântico: variável '{self.simbolo.termo}' não foi declarada.")
            if fatorEsq == "-":
                t = self.geratemp()
                codigoGerado = self.code("uminus", self.simbolo.termo, "", t)
                fatorDir = t
            else:
                fatorDir = self.simbolo.termo
                codigoGerado = ""
            self.obtemSimbolo()
            return codigoGerado, fatorDir
        elif self.simbolo.tipo == TokenType.NUMERO_INTEIRO:
            if fatorEsq == "-":
                t = self.geratemp()
                codigoGerado = self.code("uminus", self.simbolo.termo, "", t)
                fatorDir = t
            else:
                fatorDir = self.simbolo.termo
                codigoGerado = ""
            self.obtemSimbolo()
            return codigoGerado, fatorDir
        elif self.simbolo.tipo == TokenType.NUMERO_REAL:
            if fatorEsq == "-":
                t = self.geratemp()
                codigoGerado = self.code("uminus", self.simbolo.termo, "", t)
                fatorDir = t
            else:
                fatorDir = self.simbolo.termo
                codigoGerado = ""
            self.obtemSimbolo()
            return codigoGerado, fatorDir
        elif self.verificaSimbolo("("):
            self.obtemSimbolo()

            expressaoCodigo, expressaoDir = self.expressao()
            codigoGerado = expressaoCodigo

            if fatorEsq == "-":
                t = self.geratemp()
                codigoGerado += self.code("uminus", expressaoDir, "", t)
                fatorDir = t
            else:
                fatorDir = expressaoDir
            if self.verificaSimbolo(")"):
                self.obtemSimbolo()
                return codigoGerado, fatorDir
            else:
                raise RuntimeError(f"Erro sintático, esperado ')', encontrado: {self.simbolo.termo}")
        else:
            raise RuntimeError(f"Erro sintático, esperado '{TokenType.IDENTIFICADOR}', '{TokenType.NUMERO_INTEIRO}', '{TokenType.NUMERO_REAL}' ou '(', encontrado: '{self.simbolo.termo}' - tipo {self.simbolo.tipo.name}")

    # <outros_termos> -> <op_ad> <termo> <outros_termos> | λ
    def outros_termos(self, outros_termosEsq):
        if self.verificaSimbolo("+") or self.verificaSimbolo("-"):
            op_adDir = self.op_ad()
            termoCodigo, termoDir = self.termo()
            t = self.geratemp()
            codigoGerado = termoCodigo
            codigoGerado += self.code(op_adDir, outros_termosEsq, termoDir, t)
            outros_termosCodigo, outros_termosDir = self.outros_termos(t)
            codigoGerado += outros_termosCodigo
            return codigoGerado, outros_termosDir
        else:
            # Retorno vazio
            return "", outros_termosEsq

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
            fatorCodigo, fatorDir = self.fator(None)
            t = self.geratemp()
            codigoGerado = fatorCodigo
            codigoGerado += self.code(op_mulDir, mais_fatoresEsq, fatorDir, t)
            mais_fatoresCodigo, mais_fatoresDir = self.mais_fatores(t)
            codigoGerado += mais_fatoresCodigo
            return codigoGerado, mais_fatoresDir
        else:
            # Retorno vazio
            return "", mais_fatoresEsq

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
    def pfalsa(self, codigoGerado):
        if self.verificaSimbolo("else"):
            self.obtemSimbolo()

            codigoComandos = self.comandos(codigoGerado)
            codigoGerado = codigoComandos
            return codigoGerado
        else:
            # Retorno vazio
            return codigoGerado
