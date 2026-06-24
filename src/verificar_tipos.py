import json
import os
from decimal import Decimal, InvalidOperation

from tabela_simbolos import (
    coletarComandosPrincipais,
    tokensDoNo,
    separarElementos,
    linhaDoToken,
    elementoEhToken,
    elementoEhComandoAninhado
)


TIPO_INTEIRO = "inteiro"
TIPO_REAL = "real"
TIPO_LOGICO = "logico"
TIPO_COMANDO = "comando"
TIPO_ERRO = "erro"

OPERADORES_NUMERICOS = {"+", "-", "*"}
OPERADORES_INTEIROS = {"/", "//", "%"}
OPERADOR_DIVISAO_REAL = "|"
OPERADOR_POTENCIA = "^"
OPERADORES_RELACIONAIS = {"==", "!=", ">", "<", ">=", "<="}

def salvarRelatorioTiposJson(resultado, caminho="output/tipos_inferidos.json"):
    os.makedirs(os.path.dirname(caminho), exist_ok=True)

    with open(caminho, "w", encoding="utf-8") as arquivo:
        json.dump(resultado, arquivo, indent=4, ensure_ascii=False)


def adicionarErro(erros, mensagem):
    if mensagem not in erros:
        erros.append(mensagem)


def tipoLiteralNumerico(valor):
    """
    O literal 1 é inteiro.
    O literal 1.0 é real.
    """

    if "." in str(valor):
        return TIPO_REAL

    return TIPO_INTEIRO


def literalEhInteiroNaoNegativo(valor):
    """
    Verifica se um literal numérico representa um inteiro não negativo.

    Exemplos:
    - "3"    -> True
    - "3.00" -> True
    - "0"    -> True
    - "0.00" -> True
    - "3.50" -> False
    - "-1"   -> False
    """

    try:
        numero = Decimal(str(valor))
    except InvalidOperation:
        return False

    return numero >= 0 and numero == numero.to_integral_value()

def ehNumerico(tipo):
    return tipo in {TIPO_INTEIRO, TIPO_REAL}


def tipoOperacaoNumerica(tipo_esquerda, tipo_direita):
    """
    Regra de promoção:
    inteiro com inteiro -> inteiro
    se houver real -> real
    """

    if tipo_esquerda == TIPO_REAL or tipo_direita == TIPO_REAL:
        return TIPO_REAL

    return TIPO_INTEIRO


def textoDoElemento(elemento):
    if elementoEhToken(elemento, "NUM") or elementoEhToken(elemento, "MEM"):
        return elemento[1]

    if elementoEhComandoAninhado(elemento):
        valores = [token[1] for token in elemento]
        return " ".join(valores)

    return "?"

def resultadoPodeSerNull(elemento):
    """
    Verifica se o resultado direto de um elemento pode ser NULL.

    Na linguagem atual:
    - se pode retornar NULL;
    - enquanto pode retornar NULL;
    - RES não precisa ser tratado aqui, pois RES só pode aparecer
      como comando principal isolado.
    """

    if not elementoEhComandoAninhado(elemento):
        return False

    elementos_internos = separarElementos(elemento)

    if len(elementos_internos) != 3:
        return False

    operador = elementos_internos[2]

    if elementoEhToken(operador, "SE"):
        return True

    if elementoEhToken(operador, "ENQUANTO"):
        return True

    return False

def inferirTipoElemento(
    elemento,
    tabela_simbolos,
    resultados_anteriores,
    anotacoes,
    erros,
    linha,
    oprel_permitido=False
):
    """
    Infere o tipo de um elemento.

    oprel_permitido:
    - False: comparações não podem aparecer neste ponto;
    - True: uma comparação pode aparecer porque este elemento
      está sendo analisado como condição direta de se/enquanto.
    """

    if elementoEhToken(elemento, "NUM"):
        return tipoLiteralNumerico(elemento[1])

    if elementoEhToken(elemento, "MEM"):
        nome = elemento[1]

        if nome not in tabela_simbolos:
            adicionarErro(
                erros,
                f"Erro semântico na linha {linha}: "
                f"variável {nome} utilizada antes de sua definição."
            )
            return TIPO_ERRO

        return tabela_simbolos[nome]["tipo"]

    if elementoEhComandoAninhado(elemento):
        return inferirTipoComando(
            elemento,
            tabela_simbolos,
            resultados_anteriores,
            anotacoes,
            erros,
            linha,
            oprel_permitido=oprel_permitido,
            res_permitido=False
        )

    adicionarErro(
        erros,
        f"Erro semântico na linha {linha}: elemento inválido na expressão."
    )

    return TIPO_ERRO

def validarOperacaoAritmetica(operador, tipo_esq, tipo_dir, linha, erros):
    if tipo_esq == TIPO_ERRO or tipo_dir == TIPO_ERRO:
        return TIPO_ERRO

    if operador in OPERADORES_INTEIROS:
        if tipo_esq != TIPO_INTEIRO or tipo_dir != TIPO_INTEIRO:
            adicionarErro(
                erros,
                f"Erro semântico na linha {linha}: "
                f"o operador {operador} exige dois operandos inteiros, "
                f"mas recebeu {tipo_esq} e {tipo_dir}."
            )
            return TIPO_ERRO

        return TIPO_INTEIRO

    if operador == OPERADOR_DIVISAO_REAL:
        if not ehNumerico(tipo_esq) or not ehNumerico(tipo_dir):
            adicionarErro(
                erros,
                f"Erro semântico na linha {linha}: "
                f"o operador {operador} exige operandos numéricos."
            )
            return TIPO_ERRO

        return TIPO_REAL

    if operador in OPERADORES_NUMERICOS:
        if not ehNumerico(tipo_esq) or not ehNumerico(tipo_dir):
            adicionarErro(
                erros,
                f"Erro semântico na linha {linha}: "
                f"o operador {operador} exige operandos numéricos, "
                f"mas recebeu {tipo_esq} e {tipo_dir}."
            )
            return TIPO_ERRO

        return tipoOperacaoNumerica(tipo_esq, tipo_dir)

    adicionarErro(
        erros,
        f"Erro semântico na linha {linha}: operador aritmético {operador} desconhecido."
    )

    return TIPO_ERRO


def validarPotenciacao(
    elemento_expoente,
    tipo_base,
    tipo_expoente,
    linha,
    erros
):
    """
    Valida a operação de potenciação.

    Regras:
    - a base deve ser numérica;
    - o expoente deve ser um literal NUM;
    - o valor do expoente deve ser inteiro e não negativo;
    - 0, 0.00, 3 e 3.00 são aceitos;
    - 3.50 é rejeitado.
    """

    if tipo_base == TIPO_ERRO or tipo_expoente == TIPO_ERRO:
        return TIPO_ERRO

    if not ehNumerico(tipo_base):
        adicionarErro(
            erros,
            f"Erro semântico na linha {linha}: "
            f"a base do operador ^ deve ser numérica, "
            f"mas recebeu {tipo_base}."
        )
        return TIPO_ERRO

    if not elementoEhToken(elemento_expoente, "NUM"):
        adicionarErro(
            erros,
            f"Erro semântico na linha {linha}: "
            f"o expoente de ^ deve ser um literal inteiro não negativo, "
            f"como 0, 3 ou 3.00."
        )
        return TIPO_ERRO

    valor_expoente = elemento_expoente[1]

    if not literalEhInteiroNaoNegativo(valor_expoente):
        adicionarErro(
            erros,
            f"Erro semântico na linha {linha}: "
            f"o expoente de ^ deve ser um literal inteiro não negativo, "
            f"mas recebeu {valor_expoente}."
        )
        return TIPO_ERRO

    return tipoOperacaoNumerica(tipo_base, tipo_expoente)

def validarOperacaoRelacional(operador, tipo_esq, tipo_dir, linha, erros):
    if tipo_esq == TIPO_ERRO or tipo_dir == TIPO_ERRO:
        return TIPO_ERRO

    if not ehNumerico(tipo_esq) or not ehNumerico(tipo_dir):
        adicionarErro(
            erros,
            f"Erro semântico na linha {linha}: "
            f"o operador relacional {operador} exige operandos numéricos, "
            f"mas recebeu {tipo_esq} e {tipo_dir}."
        )
        return TIPO_ERRO

    return TIPO_LOGICO

def validarRes(
    primeiro,
    resultados_anteriores,
    linha,
    anotacoes,
    erros
):
    """
    Valida o comando (N RES).

    Regras:
    - N deve ser um literal NUM escrito como inteiro;
    - N deve ser não negativo;
    - N representa uma posição nos resultados anteriores, começando em zero:
        0 -> resultado imediatamente anterior;
        1 -> segundo resultado anterior;
        2 -> terceiro resultado anterior;
    - RES retorna exatamente o tipo e a possibilidade de NULL
      do resultado referenciado.
    """

    if not elementoEhToken(primeiro, "NUM"):
        adicionarErro(
            erros,
            f"Erro semântico na linha {linha}: "
            f"RES exige um índice inteiro não negativo."
        )
        return TIPO_ERRO

    valor = primeiro[1]
    tipo_indice = tipoLiteralNumerico(valor)

    # Em RES, o índice deve ser escrito como inteiro.
    # Portanto, 0 e 1 são válidos; 0.00 e 1.00 não são.
    if tipo_indice != TIPO_INTEIRO:
        adicionarErro(
            erros,
            f"Erro semântico na linha {linha}: "
            f"RES exige índice inteiro não negativo, mas recebeu {valor}."
        )
        return TIPO_ERRO

    indice = int(valor)

    if indice < 0:
        adicionarErro(
            erros,
            f"Erro semântico na linha {linha}: "
            f"RES exige índice inteiro não negativo, mas recebeu {valor}."
        )
        return TIPO_ERRO

    # Como a contagem começa em zero:
    # com 1 resultado anterior disponível, somente o índice 0 existe.
    if indice >= len(resultados_anteriores):
        adicionarErro(
            erros,
            f"Erro semântico na linha {linha}: "
            f"RES solicitou a posição anterior {indice}, "
            f"mas existem apenas {len(resultados_anteriores)} "
            f"resultado(s) anterior(es) disponível(is)."
        )
        return TIPO_ERRO

    # Índice zero busca o último resultado anterior.
    # Índice um busca o penúltimo, e assim por diante.
    resultado_referenciado = resultados_anteriores[-(indice + 1)]

    tipo_referenciado = resultado_referenciado["tipo"]
    pode_ser_null = resultado_referenciado.get("pode_ser_null", False)

    anotacoes.append({
        "linha": linha,
        "categoria": "res",
        "indice": indice,
        "tipo": tipo_referenciado,
        "pode_ser_null": pode_ser_null
    })

    return tipo_referenciado

def inferirTipoComando(
    tokens_comando,
    tabela_simbolos,
    resultados_anteriores,
    anotacoes,
    erros,
    linha_padrao,
    oprel_permitido=False,
    res_permitido=False
):
    linha = linhaDoToken(tokens_comando[0], linha_padrao)
    elementos = separarElementos(tokens_comando)

    # Caso: (A)
    if len(elementos) == 1:
        tipo = inferirTipoElemento(
            elementos[0],
            tabela_simbolos,
            resultados_anteriores,
            anotacoes,
            erros,
            linha
        )

        anotacoes.append({
            "linha": linha,
            "categoria": "uso_variavel",
            "expressao": textoDoElemento(elementos[0]),
            "tipo": tipo
        })

        return tipo

    # Caso: (1 A), (A B), (N RES), ((expr) A)
    if len(elementos) == 2:
        primeiro = elementos[0]
        segundo = elementos[1]

        # Caso: (N RES)
        if elementoEhToken(segundo, "RES"):
            if not res_permitido:
                adicionarErro(
                    erros,
                    f"Erro semântico na linha {linha}: "
                    f"RES só pode ser usado como comando isolado no formato (N RES)."
                )
                return TIPO_ERRO

            return validarRes(
                primeiro,
                resultados_anteriores,
                linha,
                anotacoes,
                erros
            )

        # (1 A): definição válida; variável armazenada como real.
        if elementoEhToken(primeiro, "NUM") and elementoEhToken(segundo, "MEM"):
            tipo = TIPO_REAL

            anotacoes.append({
                "linha": linha,
                "categoria": "atribuicao_literal",
                "variavel": segundo[1],
                "tipo": tipo
            })

            return tipo

        # (A B): atribuição válida se A já tiver sido definida.
        if elementoEhToken(primeiro, "MEM") and elementoEhToken(segundo, "MEM"):
            tipo_origem = inferirTipoElemento(
                primeiro,
                tabela_simbolos,
                resultados_anteriores,
                anotacoes,
                erros,
                linha
            )

            if tipo_origem == TIPO_ERRO:
                return TIPO_ERRO

            anotacoes.append({
                "linha": linha,
                "categoria": "atribuicao_variavel",
                "origem": primeiro[1],
                "destino": segundo[1],
                "tipo": TIPO_REAL
            })

            return TIPO_REAL

        # ((3 4 +) A) ou ((3 4 <=) A)
        # Já deve ser rejeitado pela tabela de símbolos.
        if elementoEhComandoAninhado(primeiro) and elementoEhToken(segundo, "MEM"):
            return TIPO_ERRO

    # Casos:(A B +), (A B <), ((A B <) A se), ((A B <) A enquanto)
    if len(elementos) == 3:
        primeiro = elementos[0]
        segundo = elementos[1]
        operador = elementos[2]

        # -----------------------------------------
        # Comando SE
        # -----------------------------------------
        if elementoEhToken(operador, "SE"):
            tipo_condicao = inferirTipoElemento(
                primeiro,
                tabela_simbolos,
                resultados_anteriores,
                anotacoes,
                erros,
                linha,
                oprel_permitido=True
            )

            tipo_acao = inferirTipoElemento(
                segundo,
                tabela_simbolos,
                resultados_anteriores,
                anotacoes,
                erros,
                linha,
                oprel_permitido=False
            )

            if tipo_condicao == TIPO_ERRO or tipo_acao == TIPO_ERRO:
                return TIPO_ERRO

            if tipo_condicao != TIPO_LOGICO:
                adicionarErro(
                    erros,
                    f"Erro semântico na linha {linha}: "
                    f"o comando se exige uma comparação relacional direta "
                    f"como condição."
                )
                return TIPO_ERRO

            anotacoes.append({
                "linha": linha,
                "categoria": "decisao",
                "tipo_condicao": TIPO_LOGICO,
                "tipo": tipo_acao,
                "pode_ser_null": True
            })

            return tipo_acao

        # -----------------------------------------
        # Comando ENQUANTO
        # -----------------------------------------
        if elementoEhToken(operador, "ENQUANTO"):
            tipo_condicao = inferirTipoElemento(
                primeiro,
                tabela_simbolos,
                resultados_anteriores,
                anotacoes,
                erros,
                linha,
                oprel_permitido=True
            )

            tipo_acao = inferirTipoElemento(
                segundo,
                tabela_simbolos,
                resultados_anteriores,
                anotacoes,
                erros,
                linha,
                oprel_permitido=False
            )

            if tipo_condicao == TIPO_ERRO or tipo_acao == TIPO_ERRO:
                return TIPO_ERRO

            if tipo_condicao != TIPO_LOGICO:
                adicionarErro(
                    erros,
                    f"Erro semântico na linha {linha}: "
                    f"o comando enquanto exige uma comparação relacional direta "
                    f"como condição."
                )
                return TIPO_ERRO

            anotacoes.append({
                "linha": linha,
                "categoria": "repeticao",
                "tipo_condicao": TIPO_LOGICO,
                "tipo": tipo_acao,
                "pode_ser_null": True
            })

            return tipo_acao

        # -----------------------------------------
        # Para operações comuns, nenhum OPREL
        # interno recebe autorização especial.
        # -----------------------------------------
        tipo_esq = inferirTipoElemento(
            primeiro,
            tabela_simbolos,
            resultados_anteriores,
            anotacoes,
            erros,
            linha,
            oprel_permitido=False
        )

        tipo_dir = inferirTipoElemento(
            segundo,
            tabela_simbolos,
            resultados_anteriores,
            anotacoes,
            erros,
            linha,
            oprel_permitido=False
        )

        # -----------------------------------------
        # Operações aritméticas
        # -----------------------------------------
        if elementoEhToken(operador, "OP"):
            simbolo_operador = operador[1]

            if resultadoPodeSerNull(primeiro) or resultadoPodeSerNull(segundo):
                adicionarErro(
                    erros,
                    f"Erro semântico na linha {linha}: "
                    f"o operador {simbolo_operador} não pode utilizar "
                    f"um resultado que pode ser NULL."
                )
                return TIPO_ERRO

            if simbolo_operador == OPERADOR_POTENCIA:
                tipo_resultado = validarPotenciacao(
                    segundo,
                    tipo_esq,
                    tipo_dir,
                    linha,
                    erros
                )
            else:
                tipo_resultado = validarOperacaoAritmetica(
                    simbolo_operador,
                    tipo_esq,
                    tipo_dir,
                    linha,
                    erros
                )

            anotacoes.append({
                "linha": linha,
                "categoria": "operacao_aritmetica",
                "operador": simbolo_operador,
                "tipo": tipo_resultado
            })

            return tipo_resultado

        # -----------------------------------------
        # Operação relacional
        # -----------------------------------------
        if elementoEhToken(operador, "OPREL"):
            if not oprel_permitido:
                adicionarErro(
                    erros,
                    f"Erro semântico na linha {linha}: "
                    f"o operador relacional {operador[1]} só pode ser usado "
                    f"como condição direta de se ou enquanto."
                )
                return TIPO_ERRO

            if resultadoPodeSerNull(primeiro) or resultadoPodeSerNull(segundo):
                adicionarErro(
                    erros,
                    f"Erro semântico na linha {linha}: "
                    f"o operador relacional {operador[1]} não pode utilizar "
                    f"um resultado que pode ser NULL."
                )
                return TIPO_ERRO

            tipo_resultado = validarOperacaoRelacional(
                operador[1],
                tipo_esq,
                tipo_dir,
                linha,
                erros
            )

            if tipo_resultado == TIPO_ERRO:
                return TIPO_ERRO

            anotacoes.append({
                "linha": linha,
                "categoria": "operacao_relacional",
                "operador": operador[1],
                "tipo": TIPO_LOGICO
            })

            return TIPO_LOGICO

    adicionarErro(
        erros,
        f"Erro semântico na linha {linha}: não foi possível inferir o tipo do comando."
    )

    return TIPO_ERRO

def verificarTipos(arvore, tabela_simbolos):
    """
    Recebe a árvore sintática inicial e a tabela de símbolos.
    Retorna tipos inferidos para os comandos e erros semânticos de tipo.
    """

    anotacoes = []
    erros = []
    resultados_anteriores = []

    comandos = coletarComandosPrincipais(arvore)

    for numero_comando, comando in enumerate(comandos, start=1):
        tokens = tokensDoNo(comando)

        if not tokens:
            continue

        linha = linhaDoToken(tokens[0], numero_comando)

        tipo_resultado = inferirTipoComando(
            tokens,
            tabela_simbolos,
            resultados_anteriores,
            anotacoes,
            erros,
            linha,
            oprel_permitido=False,
            res_permitido=True
        )

        pode_ser_null = False

        if anotacoes:
            ultima_anotacao = anotacoes[-1]

            if ultima_anotacao.get("linha") == linha:
                pode_ser_null = ultima_anotacao.get("pode_ser_null", False)

        resultados_anteriores.append({
            "linha": linha,
            "tipo": tipo_resultado,
            "pode_ser_null": pode_ser_null
        })

    resultado = {
        "tipos_inferidos": anotacoes,
        "resultados_anteriores": resultados_anteriores,
        "erros_semanticos": erros
    }

    salvarRelatorioTiposJson(resultado)

    return resultado