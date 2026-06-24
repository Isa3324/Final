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

from morse_utils import normalizar_texto_morse

TIPO_INTEIRO = "inteiro"
TIPO_REAL = "real"
TIPO_LOGICO = "logico"
TIPO_COMANDO = "comando"


def salvarArvoreAtribuidaJson(
    arvore_atribuida,
    caminho="output/arvore_atribuida.json"
):
    os.makedirs(os.path.dirname(caminho), exist_ok=True)

    with open(caminho, "w", encoding="utf-8") as arquivo:
        json.dump(arvore_atribuida, arquivo, indent=4, ensure_ascii=False)


def tipoLiteral(valor):
    """
    Tipo do literal escrito no código.

    Atenção:
    - O literal 1 é inteiro.
    - O literal 1.0 é real.
    - Quando armazenado em MEM, a variável continua sendo real,
      conforme a regra definida para a linguagem.
    """

    if "." in str(valor):
        return TIPO_REAL

    return TIPO_INTEIRO

def obterInteiroLiteral(valor):
    """
    Converte um NUM para inteiro.
    Aceita:
    1
    1.0
    500
    Rejeita:
    1.5
    """
    try:
        numero = Decimal(str(valor))
    except InvalidOperation:
        return None

    if numero != numero.to_integral_value():
        return None

    return int(numero)

def tipoDaOperacao(operador, tipo_esquerda, tipo_direita):
    """
    Esta função apenas anota o tipo final de uma operação
    que já foi validada previamente por verificarTipos().
    """

    if operador in {"/", "//", "%"}:
        return TIPO_INTEIRO

    if operador == "|":
        return TIPO_REAL

    if tipo_esquerda == TIPO_REAL or tipo_direita == TIPO_REAL:
        return TIPO_REAL

    return TIPO_INTEIRO


def obterTipoResultado(no):
    """
    Obtém o tipo de um nó já convertido.
    """

    if "tipo_resultado" in no:
        return no["tipo_resultado"]

    return no.get("tipo")


def converterElemento(elemento, tabelaSimbolos, historico_resultados, linha):
    """
    Converte um elemento da árvore sintática inicial
    para um nó semanticamente anotado.
    """

    if elementoEhToken(elemento, "NUM"):
        return {
            "categoria": "literal",
            "valor": elemento[1],
            "tipo": tipoLiteral(elemento[1]),
            "linha": linha
        }

    if elementoEhToken(elemento, "MEM"):
        nome = elemento[1]
        simbolo = tabelaSimbolos[nome]

        return {
            "categoria": "variavel",
            "nome": nome,
            "tipo": simbolo["tipo"],
            "linha_definicao": simbolo["linha_definicao"],
            "linha": linha
        }

    if elementoEhComandoAninhado(elemento):
        return converterComando(
            elemento,
            tabelaSimbolos,
            historico_resultados,
            linha
        )

    raise ValueError(f"Elemento não reconhecido na árvore atribuída: {elemento}")


def converterComando(
    tokens_comando,
    tabelaSimbolos,
    historico_resultados,
    linha_padrao
):
    """
    Converte um comando da árvore inicial para um nó
    da árvore sintática atribuída.
    """

    linha = linhaDoToken(tokens_comando[0], linha_padrao)
    elementos = separarElementos(tokens_comando)

    # Caso: (bloco comando1 comando2 ...)
    if len(elementos) >= 1 and elementoEhToken(elementos[0], "BLOCO"):
        comandos_do_bloco = elementos[1:]

        comandos_atribuidos = []

        for comando in comandos_do_bloco:
            if not elementoEhComandoAninhado(comando):
                raise ValueError(
                    f"Não foi possível gerar árvore atribuída na linha {linha}: "
                    f"bloco só pode conter comandos entre parênteses."
                )

            comando_atribuido = converterComando(
                comando,
                tabelaSimbolos,
                historico_resultados,
                linha
            )

            comandos_atribuidos.append(comando_atribuido)

        if len(comandos_atribuidos) == 0:
            raise ValueError(
                f"Não foi possível gerar árvore atribuída na linha {linha}: "
                f"bloco não pode ser vazio."
            )

        ultimo = comandos_atribuidos[-1]

        return {
            "categoria": "bloco",
            "comandos": comandos_atribuidos,
            "tipo_resultado": ultimo.get("tipo_resultado", TIPO_COMANDO),
            "pode_ser_null": ultimo.get("pode_ser_null", False),
            "linha": linha
        }
    
    # Caso: (A)
    if len(elementos) == 1 and elementoEhToken(elementos[0], "MEM"):
        variavel = converterElemento(
            elementos[0],
            tabelaSimbolos,
            historico_resultados,
            linha
        )

        return {
            "categoria": "leitura_memoria",
            "variavel": variavel,
            "tipo_resultado": TIPO_REAL,
            "linha": linha
        }

    # Casos: (1 A), (A B), (N RES)
    if len(elementos) == 2:
        primeiro = elementos[0]
        segundo = elementos[1]

        # Caso: ([texto] morse)
        if elementoEhToken(primeiro, "PALA") and elementoEhToken(segundo, "MOR"):
            texto_original = primeiro[1]
            texto_normalizado = normalizar_texto_morse(texto_original)

            return {
                "categoria": "morse",
                "texto_original": texto_original,
                "texto_normalizado": texto_normalizado,
                "tipo_resultado": TIPO_COMANDO,
                "linha": linha
            }

        # Caso: (1 A) ou (1.0 A)
        if elementoEhToken(primeiro, "NUM") and elementoEhToken(segundo, "MEM"):
            return {
                "categoria": "atribuicao_literal",
                "destino": segundo[1],
                "valor": converterElemento(
                    primeiro,
                    tabelaSimbolos,
                    historico_resultados,
                    linha
                ),
                "tipo_resultado": TIPO_REAL,
                "linha": linha
            }

        # Caso: (A B)
        if elementoEhToken(primeiro, "MEM") and elementoEhToken(segundo, "MEM"):
            return {
                "categoria": "atribuicao_variavel",
                "origem": converterElemento(
                    primeiro,
                    tabelaSimbolos,
                    historico_resultados,
                    linha
                ),
                "destino": segundo[1],
                "tipo_resultado": TIPO_REAL,
                "linha": linha
            }

        # Caso: (N RES)
        # N indica uma posição entre os resultados anteriores,
        # contando a partir de zero:
        # 0 -> resultado imediatamente anterior
        # 1 -> segundo resultado anterior
        # 2 -> terceiro resultado anterior
        if elementoEhToken(primeiro, "NUM") and elementoEhToken(segundo, "RES"):
            indice = int(primeiro[1])

            if indice < 0 or indice >= len(historico_resultados):
                raise ValueError(
                    f"Não é possível gerar árvore atribuída na linha {linha}: "
                    f"RES solicitou a posição anterior {indice}, "
                    f"mas existem apenas {len(historico_resultados)} "
                    f"resultado(s) anterior(es) disponível(is)."
                )

            resultado_referenciado = historico_resultados[-(indice + 1)]

            return {
                "categoria": "res",
                "indice": indice,
                "posicao_historico": len(historico_resultados) - (indice + 1),
                "tipo_resultado": resultado_referenciado["tipo_resultado"],
                "pode_ser_null": resultado_referenciado.get("pode_ser_null", False),
                "linha_resultado_referenciado": resultado_referenciado["linha"],
                "linha": linha
            }

        # Caso: (N delay)
        if elementoEhToken(primeiro, "NUM") and elementoEhToken(segundo, "DELAY"):
            tempo_ms = obterInteiroLiteral(primeiro[1])

            if tempo_ms is None:
                raise ValueError(
                    f"Não foi possível gerar árvore atribuída na linha {linha}: "
                    f"delay exige número inteiro."
                )

            return {
                "categoria": "delay",
                "tempo_ms": tempo_ms,
                "tipo_resultado": TIPO_COMANDO,
                "linha": linha
            }
        
        # Não deveria chegar aqui, pois tabela_simbolos já rejeita.
        # Casos: ((3 4 +) A), ((3 4 <=) A)
        if elementoEhComandoAninhado(primeiro) and elementoEhToken(segundo, "MEM"):
            raise ValueError(
                f"Não é possível gerar árvore atribuída na linha {linha}: "
                f"atribuição de expressão para {segundo[1]} não é permitida."
            )

    # Casos:
    # (A B +)
    # (A B <)
    # ((A B <) A se)
    # ((A B <) (A 1 +) enquanto)
    if len(elementos) == 3:
        primeiro = elementos[0]
        segundo = elementos[1]
        operador = elementos[2]

        # Caso: (led N ligar) ou (led N desligar)
        if (
            elementoEhToken(primeiro, "LED")
            and elementoEhToken(segundo, "NUM")
            and (
                elementoEhToken(operador, "LIGAR")
                or elementoEhToken(operador, "DESLIGAR")
            )
        ):
            mascara = obterInteiroLiteral(segundo[1])

            if mascara is None:
                raise ValueError(
                    f"Não foi possível gerar árvore atribuída na linha {linha}: "
                    f"máscara do led precisa ser inteira."
                )

            acao = "ligar"

            if elementoEhToken(operador, "DESLIGAR"):
                acao = "desligar"

            return {
                "categoria": "led",
                "mascara": mascara,
                "acao": acao,
                "tipo_resultado": TIPO_COMANDO,
                "linha": linha
            }
        
        esquerda = converterElemento(
            primeiro,
            tabelaSimbolos,
            historico_resultados,
            linha
        )

        direita = converterElemento(
            segundo,
            tabelaSimbolos,
            historico_resultados,
            linha
        )

        if elementoEhToken(operador, "OP"):
            tipo_resultado = tipoDaOperacao(
                operador[1],
                obterTipoResultado(esquerda),
                obterTipoResultado(direita)
            )

            return {
                "categoria": "operacao_aritmetica",
                "operador": operador[1],
                "esquerda": esquerda,
                "direita": direita,
                "tipo_resultado": tipo_resultado,
                "linha": linha
            }

        if elementoEhToken(operador, "OPREL"):
            return {
                "categoria": "operacao_relacional",
                "operador": operador[1],
                "esquerda": esquerda,
                "direita": direita,
                "tipo_resultado": TIPO_LOGICO,
                "linha": linha
            }

        if elementoEhToken(operador, "SE"):
            return {
                "categoria": "decisao",
                "condicao": esquerda,
                "acao": direita,

                # A condição já foi validada anteriormente como relacional.
                "tipo_condicao": TIPO_LOGICO,

                # Se a ação produzir real, o se produz real quando executado.
                # Se a ação for outro se/enquanto, pega o tipo produzido por ele.
                "tipo_resultado": obterTipoResultado(direita),

                # Todo se pode retornar NULL, pois sua condição pode ser falsa.
                "pode_ser_null": True,

                # Informa se, mesmo quando a condição externa for verdadeira,
                # a própria ação ainda pode resultar em NULL.
                "acao_pode_ser_null": direita.get("pode_ser_null", False),

                "valor_sem_execucao": "NULL",
                "linha": linha
            }
            
        if elementoEhToken(operador, "ENQUANTO"):
            return {
                "categoria": "repeticao",
                "condicao": esquerda,
                "acao": direita,

                # A condição do enquanto deve ser lógica.
                "tipo_condicao": TIPO_LOGICO,

                # O resultado do laço, quando existir, é do mesmo tipo da ação.
                "tipo_resultado": obterTipoResultado(direita),

                # Todo enquanto pode resultar em NULL,
                # pois talvez não execute nenhuma vez.
                "pode_ser_null": True,

                # Se a ação for outro controle, ela também pode gerar NULL
                # mesmo durante uma iteração executada.
                "acao_pode_ser_null": direita.get("pode_ser_null", False),

                "valor_sem_execucao": "NULL",
                "resultado_quando_executa": "resultado_da_ultima_execucao",
                "linha": linha
            }

    raise ValueError(
        f"Não foi possível converter o comando da linha {linha} "
        f"para árvore sintática atribuída."
    )


def gerarArvoreAtribuida(arvore, tabelaSimbolos, tipos):
    """
    Recebe:
        - árvore sintática inicial;
        - tabela de símbolos;
        - resultado de verificarTipos().

    Retorna:
        - árvore sintática atribuída pronta para geração de Assembly.
    """

    if tipos.get("erros_semanticos"):
        raise ValueError(
            "Não é possível gerar árvore atribuída: existem erros semânticos de tipo."
        )

    comandos_atribuidos = []
    historico_resultados = []

    comandos_iniciais = coletarComandosPrincipais(arvore)

    for numero_comando, comando in enumerate(comandos_iniciais, start=1):
        tokens = tokensDoNo(comando)

        no_atribuido = converterComando(
            tokens,
            tabelaSimbolos,
            historico_resultados,
            numero_comando
        )

        no_atribuido["indice_resultado"] = len(historico_resultados) + 1

        comandos_atribuidos.append(no_atribuido)

        historico_resultados.append({
            "linha": no_atribuido["linha"],
            "tipo_resultado": no_atribuido["tipo_resultado"],
            "pode_ser_null": no_atribuido.get("pode_ser_null", False)
        })

    arvore_atribuida = {
        "categoria": "programa",
        "tipo": "programa",
        "inicio": "START",
        "fim": "END",
        "tabela_simbolos": tabelaSimbolos,
        "tipos_validados": tipos,
        "comandos": comandos_atribuidos
    }

    salvarArvoreAtribuidaJson(arvore_atribuida)

    return arvore_atribuida