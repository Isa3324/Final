import json
import os


def lerArvoreJson(caminho="output/arvore_sintatica.json"):
    with open(caminho, "r", encoding="utf-8") as arquivo:
        return json.load(arquivo)


def salvarTabelaSimbolosJson(tabela, erros, caminho="output/tabela_simbolos.json"):
    os.makedirs(os.path.dirname(caminho), exist_ok=True)

    dados = {
        "tabela_simbolos": tabela,
        "erros_semanticos": erros
    }

    with open(caminho, "w", encoding="utf-8") as arquivo:
        json.dump(dados, arquivo, indent=4, ensure_ascii=False)


def tokensDoNo(no):
    """
    Retorna todos os tokens folha de um nó da árvore.
    Converte listas vindas do JSON novamente para tuplas.
    """

    tokens = []

    if no.get("token") is not None:
        tokens.append(tuple(no["token"]))

    for filho in no.get("filhos", []):
        tokens.extend(tokensDoNo(filho))

    return tokens


def coletarComandosPrincipais(arvore):
    """
    Coleta apenas os comandos diretamente presentes na lista de comandos
    do programa, preservando a ordem das linhas.
    """

    comandos = []

    def percorrerLista(no):
        for filho in no.get("filhos", []):
            if filho["simbolo"] == "comando":
                comandos.append(filho)

            elif filho["simbolo"] == "lista_comandos":
                percorrerLista(filho)

    for filho in arvore.get("filhos", []):
        if filho["simbolo"] == "lista_comandos":
            percorrerLista(filho)

    return comandos

def separarElementos(tokens_comando):
    """
    Recebe os tokens completos de um comando, por exemplo:
    EPAR MEM MEM DPAR

    Retorna apenas os elementos internos, agrupando comandos aninhados.
    """

    internos = tokens_comando[1:-1]
    elementos = []
    i = 0

    while i < len(internos):
        token = internos[i]

        if token[0] == "EPAR":
            profundidade = 1
            inicio = i
            i += 1

            while i < len(internos) and profundidade > 0:
                if internos[i][0] == "EPAR":
                    profundidade += 1

                elif internos[i][0] == "DPAR":
                    profundidade -= 1

                i += 1

            elementos.append(internos[inicio:i])

        else:
            elementos.append(token)
            i += 1

    return elementos


def linhaDoToken(token, linha_padrao="?"):
    if len(token) >= 4:
        return token[3]

    return linha_padrao


def elementoEhToken(elemento, tipo):
    return isinstance(elemento, tuple) and elemento[0] == tipo


def elementoEhComandoAninhado(elemento):
    return isinstance(elemento, list)


def registrarDefinicao(
    tabela,
    nome_variavel,
    linha,
    erros=None,
    contexto_controle=None
):
    """
    Registra a primeira definição ou uma reatribuição de variável.

    Regras:
    - Toda variável MEM possui tipo real.
    - Variável nova não pode ser criada pela primeira vez dentro de se/enquanto.
    - Variável já existente pode ser reatribuída dentro de se/enquanto.
    """

    # Primeira definição da variável
    if nome_variavel not in tabela:
        if contexto_controle is not None:
            if erros is not None:
                erros.append(
                    f"Erro semântico na linha {linha}: "
                    f"a variável {nome_variavel} não pode ser definida pela primeira vez "
                    f"dentro de {contexto_controle}. "
                    f"Defina a variável antes da estrutura de controle."
                )

            return False

        tabela[nome_variavel] = {
            "identificador": nome_variavel,
            "tipo": "real",
            "linha_definicao": linha,
            "linhas_atribuicao": [linha],
            "linha_ultima_atribuicao": linha,
            "linhas_uso": [],
            "linha_ultimo_uso": None
        }

        return True

    # Reatribuição de variável já existente
    tabela[nome_variavel]["linhas_atribuicao"].append(linha)
    tabela[nome_variavel]["linha_ultima_atribuicao"] = linha

    return True


def registrarUso(tabela, erros, token_variavel, linha):
    nome_variavel = token_variavel[1]

    if nome_variavel not in tabela:
        erros.append(
            f"Erro semântico na linha {linha}: "
            f"variável {nome_variavel} utilizada antes de sua definição."
        )
        return False

    tabela[nome_variavel]["linhas_uso"].append(linha)
    tabela[nome_variavel]["linha_ultimo_uso"] = linha

    return True

def analisarUsosEmElemento(
    elemento,
    tabela,
    erros,
    linha,
    contexto_controle=None
):
    """
    Analisa um elemento usado dentro de um comando.

    contexto_controle pode ser:
    - None: fora de se/enquanto;
    - "se": dentro de uma decisão;
    - "enquanto": dentro de um laço.
    """

    # Um número literal não altera a tabela de símbolos.
    if elementoEhToken(elemento, "NUM"):
        return

        # Tokens especiais que não usam variável MEM diretamente.
    if (
        elementoEhToken(elemento, "PALA")
        or elementoEhToken(elemento, "LED")
        or elementoEhToken(elemento, "LIGAR")
        or elementoEhToken(elemento, "DESLIGAR")
        or elementoEhToken(elemento, "DELAY")
        or elementoEhToken(elemento, "BLOCO")
    ):
        return
    
    # Uma variável isolada neste ponto está sendo usada.
    if elementoEhToken(elemento, "MEM"):
        registrarUso(tabela, erros, elemento, linha)
        return

    # Se o elemento é outro comando, analisa recursivamente,
    # mantendo a informação de estar ou não dentro de controle.
    if elementoEhComandoAninhado(elemento):
        elementos_internos = separarElementos(elemento)

        analisarComandoInterno(
            elementos_internos,
            tabela,
            erros,
            linha,
            contexto_controle
        )


def analisarComandoInterno(
    elementos,
    tabela,
    erros,
    linha,
    contexto_controle=None
):
    """
    Analisa comandos aninhados para a tabela de símbolos.

    Esta função verifica:
    - uso de variáveis;
    - definições e reatribuições;
    - proibição de criar variável nova dentro de se/enquanto;
    - atribuição inválida de expressão para variável.

    Ela não verifica tipos de operadores.
    """
    # Caso: (bloco comando1 comando2 ...)
    # O bloco não cria variável por si só, mas seus comandos internos podem criar/usar MEM.
    if len(elementos) >= 1 and elementoEhToken(elementos[0], "BLOCO"):
        comandos_do_bloco = elementos[1:]

        for comando in comandos_do_bloco:
            if elementoEhComandoAninhado(comando):
                elementos_internos = separarElementos(comando)

                analisarComandoInterno(
                    elementos_internos,
                    tabela,
                    erros,
                    linha,
                    contexto_controle
                )

        return
    # Caso: (A)
    # Uso isolado de variável.
    if len(elementos) == 1:
        if elementoEhToken(elementos[0], "MEM"):
            registrarUso(tabela, erros, elementos[0], linha)

        return

    # Casos com dois elementos:
    # (1 A)
    # (A B)
    # (N RES)
    # ((expressao) A)
    if len(elementos) == 2:
        primeiro = elementos[0]
        segundo = elementos[1]
        
        # Caso: (N RES)
        # RES não define nem usa variável MEM.
        if elementoEhToken(segundo, "RES"):
            return
        
        # Caso: ([texto] morse)
        # Morse não define nem usa variável MEM.
        if elementoEhToken(primeiro, "PALA") and elementoEhToken(segundo, "MOR"):
            return
        
        # Caso: (N delay)
        # Delay não define nem usa variável MEM.
        if elementoEhToken(primeiro, "NUM") and elementoEhToken(segundo, "DELAY"):
            return
        
        # Caso: (1 A) ou (1.0 A)
        # Define A fora de controle ou reatribui A dentro de controle.
        if elementoEhToken(primeiro, "NUM") and elementoEhToken(segundo, "MEM"):
            registrarDefinicao(
                tabela,
                segundo[1],
                linha,
                erros=erros,
                contexto_controle=contexto_controle
            )
            return

        # Caso: (A B)
        # A é usada como origem.
        # B é definida ou reatribuída.
        if elementoEhToken(primeiro, "MEM") and elementoEhToken(segundo, "MEM"):
            origem_valida = registrarUso(tabela, erros, primeiro, linha)

            if origem_valida:
                registrarDefinicao(
                    tabela,
                    segundo[1],
                    linha,
                    erros=erros,
                    contexto_controle=contexto_controle
                )

            return

        # Caso: ((3 4 +) A) ou ((3 4 <=) A)
        # Continua proibido pela regra atual da linguagem.
        if elementoEhComandoAninhado(primeiro) and elementoEhToken(segundo, "MEM"):
            erros.append(
                f"Erro semântico na linha {linha}: "
                f"não é permitido atribuir o resultado de uma expressão "
                f"à variável {segundo[1]}. "
                f"Uma atribuição deve usar NUM ou uma variável já definida."
            )

            # Mesmo inválida, verifica possíveis usos dentro da expressão.
            analisarUsosEmElemento(
                primeiro,
                tabela,
                erros,
                linha,
                contexto_controle
            )
            return

    # Casos com três elementos:
    # (A B +)
    # (A B >=)
    # ((A B >=) D se)
    # ((D S <=) D enquanto)
    if len(elementos) == 3:
        primeiro = elementos[0]
        segundo = elementos[1]
        operador = elementos[2]

        # Caso: (led N ligar) ou (led N desligar)
        # LED não define nem usa variável MEM.
        if (
            elementoEhToken(primeiro, "LED")
            and elementoEhToken(segundo, "NUM")
            and (
                elementoEhToken(operador, "LIGAR")
                or elementoEhToken(operador, "DESLIGAR")
            )
        ):
            return
        
        # Caso: (condicao acao se)
        if elementoEhToken(operador, "SE"):
            analisarUsosEmElemento(
                primeiro,
                tabela,
                erros,
                linha,
                contexto_controle="se"
            )

            analisarUsosEmElemento(
                segundo,
                tabela,
                erros,
                linha,
                contexto_controle="se"
            )

            return

        # Caso: (condicao acao enquanto)
        if elementoEhToken(operador, "ENQUANTO"):
            analisarUsosEmElemento(
                primeiro,
                tabela,
                erros,
                linha,
                contexto_controle="enquanto"
            )

            analisarUsosEmElemento(
                segundo,
                tabela,
                erros,
                linha,
                contexto_controle="enquanto"
            )

            return

        # Operações aritméticas ou relacionais.
        # Apenas registra os usos das variáveis nos operandos.
        analisarUsosEmElemento(
            primeiro,
            tabela,
            erros,
            linha,
            contexto_controle
        )

        analisarUsosEmElemento(
            segundo,
            tabela,
            erros,
            linha,
            contexto_controle
        )

        return
        
def construirTabelaSimbolos(arvore):
    """
    Constrói a tabela de símbolos percorrendo todos os comandos principais.

    Regras tratadas aqui:
    - toda variável MEM armazenada possui tipo real;
    - variável deve ser definida antes do uso;
    - variável nova não pode ser criada dentro de se/enquanto;
    - variável previamente definida pode ser reatribuída dentro de se/enquanto;
    - atribuição direta de resultado de expressão para MEM continua proibida.
    """

    tabela = {}
    erros = []

    comandos = coletarComandosPrincipais(arvore)

    for numero_comando, comando in enumerate(comandos, start=1):
        tokens = tokensDoNo(comando)

        if not tokens:
            continue

        linha = linhaDoToken(tokens[0], numero_comando)
        elementos = separarElementos(tokens)

        analisarComandoInterno(
            elementos,
            tabela,
            erros,
            linha,
            contexto_controle=None
        )

    salvarTabelaSimbolosJson(tabela, erros)

    return {
        "tabela_simbolos": tabela,
        "erros_semanticos": erros
    }