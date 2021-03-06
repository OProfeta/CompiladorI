# CompiladorI
Compilador para o trabalho da matéria de Compiladores I.

Comando no terminal para rodar o compilador: ```python3 Compilador.py programaEntrada.txt```

Sendo o 'programaEntrada.txt' podendo ser qualquer arquivo .txt.

Autômato utilizado no compilador:


![alt text](https://github.com/OProfeta/CompiladorI/blob/master/Automato.jpg)

Gramática:

```
<programa> -> program ident <corpo> .
<corpo> -> <dc> begin <comandos> end
<dc> -> <dc_v> <mais_dc>  | λ
<mais_dc> -> ; <dc> | λ
<dc_v> ->  <tipo_var> : <variaveis>
<tipo_var> -> real | integer
<variaveis> -> ident <mais_var>
<mais_var> -> , <variaveis> | λ
<comandos> -> <comando> <mais_comandos>
<mais_comandos> -> ; <comandos> | λ

<comando> -> read (ident) |
             write (ident) |
             ident := <expressao> |
             if <condicao> then <comandos> <pfalsa> $
							
<condicao> -> <expressao> <relacao> <expressao>
<relacao> -> = | <> | >= | <= | > | <
<expressao> -> <termo> <outros_termos>
<termo> -> <op_un> <fator> <mais_fatores>
<op_un> -> - | λ
<fator> -> ident | numero_int | numero_real | (<expressao>)
<outros_termos> -> <op_ad> <termo> <outros_termos> | λ
<op_ad> -> + | -
<mais_fatores> -> <op_mul> <fator> <mais_fatores> | λ
<op_mul> -> * | /
<pfalsa> -> else <comandos> | λ

```

Gramática com regras semânticas:

```
<programa> -> program ident <corpo> {programa.codigo = corpo.codigo, programa.codigo += code("PARA","","","")} .

<corpo> -> <dc> begin {comandos.codigo = dc.codigo} <comandos> end {corpo.codigo = comandos.codigo}

<dc> -> <dc_v> <mais_dc> {dc.codigo = dc_v.codigo + mais_dc.codigo}
<dc> -> λ {dc.codigo = ""}

<mais_dc> -> ; <dc> {mais_dc.codigo = dc.codigo}
<mais_dc> -> λ {mais_dc.codigo = ""}

<dc_v> ->  <tipo_var> {variaves.esq = tipo_var.dir} : <variaveis> {dc_v.codigo = variaveis.codigo}

<tipo_var> -> real {tipo_var.dir = real}
<tipo_var> -> integer {tipo_var.dir = integer}

<variaveis> -> ident {ident.tipo = variaveis.esq} {addTabela(ident)} {variaveis.codigo = code("ALME", 0 ou 0.0, "", ident)} {mais_var.esq = variaveis.esq} <mais_var> {variaveis.codigo += mais_var.codigo}

<mais_var> -> , {variaveis.esq = mais_var.esq} <variaveis> {mais_var.codigo = variaveis.codigo}
<mais_var> -> λ {mais_var.codigo = ""}

<comandos> -> {comando.codigo = comandos.codigo} <comando> {mais_comandos.codigo = comando.codigo} {mais_comandos.codigo = comandos.codigo} <mais_comandos> {comandos.codigo = mais_comandos.codigo}

<mais_comandos> -> ; {comandos.codigo = mais_comandos.codigo} <comandos> {mais_comandos.codigo = comandos.codigo}
<mais_comandos> -> λ {mais_comandos.codigo = mais_comandos.codigo}

<comando> -> read (ident) {comando.codigo += code("read", "", "", ident)}
<comando> -> write (ident) {comando.codigo += code("write", "", "", ident)}
<comando> -> ident := <expressao> {comando.codigo += code(":=", expressao.dir, "", ident)}
<comando> -> if <condicao> then {comando.codigo += condicao.codigo + code("JF", condicao.dir, "__", ""), comandos.codigo = comando.codigo} <comandos> {comando.codigo = comandos.codigo, comando.codigo += code("goto", "__", "", ""), pfalsa.codigo = comando.codigo} <pfalsa> {comando.codigo = pfalsa.codigo} $
							
<condicao> -> <expressao> <relacao> <expressao> {t = geraTemp(), condicao.codigo = code(relacao.dir, expressao.dir, expressaoLinha.dir, t), condicao.dir = t}

<relacao> -> = {relacao.dir = "="}
<relacao> -> <> {relacao.dir = "<>"}
<relacao> -> >= {relacao.dir = ">="}
<relacao> -> <= {relacao.dir = "<="}
<relacao> -> > {relacao.dir = ">"}
<relacao> -> < {relacao.dir = "<"}

<expressao> -> <termo> {outros_termos.esq = termo.dir} <outros_termos> {expressao.codigo = outros_termos.codigo, expressao.dir = outros_termos.dir}

<termo> -> <op_un> {fator.esq = op_un.dir} <fator> {mais_fatores.esq = fator.dir} <mais_fatores> {termo.codigo = fator.codigo + mais_fatores.codigo, termo.dir = mais_fatores.dir}

<op_un> -> - {op_un.dir = "-"}
<op_un> -> λ {op_un.dir = ""}

<fator> -> ident {
    if fator.esq == "-"
        t = geraTemp()
        fator.dir = t
        fator.codigo = code("uminus", ident, "", t)
    else
        fator.dir = ident
    }
<fator> -> numero_int {
    if fator.esq == "-"
        t = geraTemp()
        fator.dir = t
        fator.codigo = code("uminus", numero_int, "", t)
    else
        fator.dir = numero_int
        fator.codigo = ""
    }
<fator> -> numero_real {
    if fator.esq == "-"
        t = geraTemp()
        fator.dir = t
        fatorr.codigo = code("uminus, numero_real, "", temp)
    else
        fator.dir = numero_real
        fator.codigo = ""
    }
<fator> -> ( <expressao> ) {
    fator.codigo = expressao.codigo
    if fator.esq == "-"
        t = geratemp()
        fator.dir = temp
        fator.codigo += code("uminus", expressao.dir, "", t)
    else
        fator.dir = expressao.dir
    }

<outros_termos> -> <op_ad> <termo> {outros_termos.codigo = termo.codigo, t = geraTemp(), outros_termos.codigo += code(op_ad.dir, outros_termos.esq, termo.dir, t), outros_termosLinha.esq = t} <outros_termos> {outros_termos.codigo += outros_termosLinha.codigo, outros_termos.dir = outros_termosLinha.dir}
<outros_termos> -> λ {outros_termos.codigo = "", outros_termos.dir = outros_termos.esq}

<op_ad> -> + {op_ad.dir = "+"}
<op_ad> -> - {op_ad.dir = "-"}

<mais_fatores> -> <op_mul> {fator.esq = ""} <fator> {t = geraTemp(), mais_fatores.codigo = fator.codigo + Code(op_mul.dir, mais_fatores.esq, fator.dir, t), mais_fatoresLinha.esq = t} <mais_fatores> {mais_fatores.codigo = mais_fatoresLinha.codigo, mais_fatores.dir = mais_fatoresLinha.dir}
<mais_fatores> -> λ {mais_fatores.codigo = "", mais_fatores.dir = mais_fatores.esq}

<op_mul> -> * {op_mul.dir = "*"}
<op_mul> -> / {op_mul.dir = "/"}

<pfalsa> -> else {comandos.codigo = pfalsa.codigo} <comandos> {pfalsa.codigo = comandos.codigo}
<pfalsa> -> λ {pfalsa.codigo = pfalsa.codigo}
```
