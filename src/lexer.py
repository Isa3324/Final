token_EPar = "EPAR"       # "("
token_DPar = "DPAR"       # ")"
token_Num = "NUM"         # números reais
token_OP = "OP"           # "+", "-", "*", "/", "|", "//", "%" e "^"
token_Mem = "MEM"         # identificador de memória
token_Res = "RES"         # RES
token_Invalido = "INVALIDO"

token_Start = "START"     # (START)
token_End = "END"         # (END)
token_OP_REL = "OPREL"    # "==", "!=", ">", "<", ">=", "<="
token_Se = "SE"           # comando se
token_Enquanto = "ENQUANTO"  # comando enquanto

token_Mor = "MOR"         # comando morse
token_Pala = "PALA"       # palavra/frase entre colchetes

def estadoStartEnd(linha, posicao):
    if linha.startswith("(START)", posicao):
        return posicao + len("(START)"), (token_Start, "(START)", posicao)

    if linha.startswith("(END)", posicao):
        return posicao + len("(END)"), (token_End, "(END)", posicao)

    return None


def estadoOperadorRelacional(linha, posicao):
    inicio = posicao

    operadores_duplos = ["==", "!=", ">=", "<="]

    for op in operadores_duplos:
        if linha.startswith(op, posicao):
            return posicao + len(op), (token_OP_REL, op, inicio)

    if linha[posicao] in [">", "<"]:
        return posicao + 1, (token_OP_REL, linha[posicao], inicio)

    return posicao + 1, (token_Invalido, linha[posicao], inicio)


def estadoOperador(linha, posicao):
    inicio = posicao

    if linha[posicao] == "/":
        if posicao + 1 < len(linha) and linha[posicao + 1] == "/":
            return posicao + 2, (token_OP, "//", inicio)

        return posicao + 1, (token_OP, "/", inicio)

    return posicao + 1, (token_OP, linha[posicao], inicio)


def estadoNumero(linha, posicao):
    inicio = posicao
    ponto = False

    while posicao < len(linha):
        if linha[posicao].isdigit():
            posicao += 1

        elif linha[posicao] == ".":
            if ponto:
                while posicao < len(linha) and (linha[posicao].isdigit() or linha[posicao] == "."):
                    posicao += 1

                return posicao, (token_Invalido, linha[inicio:posicao], inicio)

            ponto = True
            posicao += 1

            if posicao >= len(linha) or not linha[posicao].isdigit():
                return posicao, (token_Invalido, linha[inicio:posicao], inicio)

        else:
            break

    numero = linha[inicio:posicao]
    return posicao, (token_Num, numero, inicio)


def estadoParenteses(linha, posicao):
    if linha[posicao] == "(":
        return posicao + 1, (token_EPar, "(", posicao)

    if linha[posicao] == ")":
        return posicao + 1, (token_DPar, ")", posicao)

    return posicao + 1, (token_Invalido, linha[posicao], posicao)

def estadoPalavraColchetes(linha, posicao):
    inicio = posicao
    posicao += 1  # pula o "["

    conteudo = []

    while posicao < len(linha) and linha[posicao] != "]":
        conteudo.append(linha[posicao])
        posicao += 1

    # Se chegou ao fim da linha sem achar "]", é erro léxico.
    if posicao >= len(linha):
        return posicao, (token_Invalido, linha[inicio:posicao], inicio)

    # Pula o "]"
    posicao += 1

    texto = "".join(conteudo)

    if texto.strip() == "":
        return posicao, (token_Invalido, linha[inicio:posicao], inicio)

    return posicao, (token_Pala, texto, inicio)

def estadoIdentificadorMaiusculo(linha, posicao):
    inicio = posicao

    while posicao < len(linha) and linha[posicao].isalpha() and linha[posicao].isupper():
        posicao += 1

    letras = linha[inicio:posicao]

    if letras == "RES":
        return posicao, (token_Res, letras, inicio)

    # START e END só são válidos como (START) e (END).
    # Sozinhos, devem ser inválidos.
    if letras in ["START", "END"]:
        return posicao, (token_Invalido, letras, inicio)

    return posicao, (token_Mem, letras, inicio)


def estadoComandoMinusculo(linha, posicao):
    inicio = posicao

    while posicao < len(linha) and linha[posicao].isalpha() and linha[posicao].islower():
        posicao += 1

    palavra = linha[inicio:posicao]

    if palavra == "se":
        return posicao, (token_Se, palavra, inicio)

    if palavra == "enquanto":
        return posicao, (token_Enquanto, palavra, inicio)

    if palavra == "morse":
        return posicao, (token_Mor, palavra, inicio)

    return posicao, (token_Invalido, palavra, inicio)


def parserExpressao(linha, tokens=None):
    if tokens is None:
        tokens = []

    posicao = 0

    while posicao < len(linha):
        caractere = linha[posicao]

        if caractere.isspace():
            posicao += 1
            continue

        resultado_start_end = estadoStartEnd(linha, posicao)
        if resultado_start_end is not None:
            posicao, token = resultado_start_end
            tokens.append(token)
            continue

        if caractere == "[":
            posicao, token = estadoPalavraColchetes(linha, posicao)
            tokens.append(token)
            continue

        if caractere == "(" or caractere == ")":
            posicao, token = estadoParenteses(linha, posicao)
            tokens.append(token)

        elif caractere.isdigit():
            posicao, token = estadoNumero(linha, posicao)
            tokens.append(token)

        elif caractere in ["=", "!", ">", "<"]:
            posicao, token = estadoOperadorRelacional(linha, posicao)
            tokens.append(token)

        elif caractere in ["+", "-", "*", "/", "%", "^", "|"]:
            posicao, token = estadoOperador(linha, posicao)
            tokens.append(token)

        elif caractere.isalpha() and caractere.isupper():
            posicao, token = estadoIdentificadorMaiusculo(linha, posicao)
            tokens.append(token)

        elif caractere.isalpha() and caractere.islower():
            posicao, token = estadoComandoMinusculo(linha, posicao)
            tokens.append(token)

        else:
            tokens.append((token_Invalido, caractere, posicao))
            posicao += 1

    return tokens

def removerComentarios(codigo):
    resultado = []
    posicao = 0
    dentro_comentario = False
    inicio_comentario = None

    while posicao < len(codigo):
        atual = codigo[posicao]

        if not dentro_comentario:
            if atual == "*" and posicao + 1 < len(codigo) and codigo[posicao + 1] == "{":
                dentro_comentario = True
                inicio_comentario = posicao
                posicao += 2
            else:
                resultado.append(atual)
                posicao += 1

        else:
            if atual == "}" and posicao + 1 < len(codigo) and codigo[posicao + 1] == "*":
                dentro_comentario = False
                posicao += 2
            else:
                # O conteúdo do comentário é descartado,
                # mas a quebra de linha precisa permanecer.
                # Assim os tokens seguintes continuam com
                # o mesmo número de linha do arquivo original.
                if atual == "\n":
                    resultado.append("\n")
                posicao += 1

    if dentro_comentario:
        raise SyntaxError(f"Comentário iniciado na posição {inicio_comentario} não foi fechado com }}*.")

    return "".join(resultado)
