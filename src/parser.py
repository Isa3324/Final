EPSILON = "ε"
ENDMARKER = "$"


class ErroSintatico(Exception):
    pass


def pegar_tipo_token(token):
    """
    Seu lexer retorna tokens assim:
    ("MEM", "A", 1)

    Para o parser LL(1), o que importa é o tipo:
    "MEM"
    """

    if isinstance(token, tuple):
        return token[0]

    return token


def descrever_token(token):
    if isinstance(token, tuple):
        tipo = token[0]
        valor = token[1] if len(token) > 1 else ""
        posicao = token[2] if len(token) > 2 else "?"
        linha = token[3] if len(token) > 3 and token[3] is not None else "?"

        return (
            f"{tipo} ('{valor}') "
            f"na linha {linha}, posição {posicao}"
        )

    return str(token)


def criar_no(simbolo):
    return {
        "simbolo": simbolo,
        "filhos": [],
        "token": None
    }


def parsear(tokens, tabela_ll1, simbolo_inicial="programa", recuperar_erros=False):
    """
    Parser LL(1) baseado em pilha.

    Entrada:
        tokens: lista de tokens vindos do lexer
        tabela_ll1: tabela gerada pela gramática
        simbolo_inicial: por padrão, "programa"

    Saída:
        dicionário com:
        - aceito
        - arvore
        - derivacao
        - erros
    """

    nao_terminais = set(tabela_ll1.keys())

    entrada = [pegar_tipo_token(token) for token in tokens]
    entrada.append(ENDMARKER)

    tokens_com_fim = list(tokens)
    tokens_com_fim.append((ENDMARKER, ENDMARKER, -1, "?"))
    raiz = criar_no(simbolo_inicial)

    pilha = [
        (ENDMARKER, None),
        (simbolo_inicial, raiz)
    ]

    posicao = 0
    derivacao = []
    erros = []

    while pilha:
        topo, no_atual = pilha.pop()
        token_atual = entrada[posicao]
        token_original = tokens_com_fim[posicao]

        if topo == EPSILON:
            continue

        if topo == ENDMARKER:
            if token_atual == ENDMARKER:
                return {
                    "aceito": len(erros) == 0,
                    "arvore": raiz,
                    "derivacao": derivacao,
                    "erros": erros
                }

            mensagem = (
                f"Erro sintático: esperado fim da entrada, "
                f"encontrado {descrever_token(token_original)}."
            )
            erros.append(mensagem)

            if not recuperar_erros:
                return {
                    "aceito": False,
                    "arvore": raiz,
                    "derivacao": derivacao,
                    "erros": erros
                }

        # Caso 1: topo da pilha é terminal
        if topo not in nao_terminais:
            if topo == token_atual:
                if no_atual is not None:
                    no_atual["token"] = token_original

                posicao += 1
            else:
                mensagem = (
                    f"Erro sintático: esperado {topo}, "
                    f"encontrado {descrever_token(token_original)}."
                )
                erros.append(mensagem)

                if not recuperar_erros:
                    return {
                        "aceito": False,
                        "arvore": raiz,
                        "derivacao": derivacao,
                        "erros": erros
                    }

                # Recuperação básica:
                # pula o token atual e tenta continuar
                if token_atual != ENDMARKER:
                    posicao += 1

            continue

        # Caso 2: topo da pilha é não-terminal
        if token_atual not in tabela_ll1.get(topo, {}):
            esperados = sorted(tabela_ll1.get(topo, {}).keys())

            mensagem = (
                f"Erro sintático em {topo}: encontrado "
                f"{descrever_token(token_original)}. "
                f"Esperado um destes tokens: {esperados}."
            )
            erros.append(mensagem)

            if not recuperar_erros:
                return {
                    "aceito": False,
                    "arvore": raiz,
                    "derivacao": derivacao,
                    "erros": erros
                }

            # Recuperação básica:
            # pula tokens até achar um token que sirva para esse não-terminal
            while token_atual != ENDMARKER and token_atual not in tabela_ll1.get(topo, {}):
                posicao += 1
                token_atual = entrada[posicao]
                token_original = tokens_com_fim[posicao]

            if token_atual == ENDMARKER:
                return {
                    "aceito": False,
                    "arvore": raiz,
                    "derivacao": derivacao,
                    "erros": erros
                }

        producao = tabela_ll1[topo][token_atual]

        derivacao.append({
            "nao_terminal": topo,
            "lookahead": token_atual,
            "producao": producao
        })

        filhos = []

        if producao == [EPSILON]:
            filho_epsilon = criar_no(EPSILON)
            no_atual["filhos"].append(filho_epsilon)
            continue

        for simbolo in producao:
            filho = criar_no(simbolo)
            filhos.append(filho)

        no_atual["filhos"].extend(filhos)

        for simbolo, filho in reversed(list(zip(producao, filhos))):
            if simbolo != EPSILON:
                pilha.append((simbolo, filho))

    return {
        "aceito": len(erros) == 0,
        "arvore": raiz,
        "derivacao": derivacao,
        "erros": erros
    }