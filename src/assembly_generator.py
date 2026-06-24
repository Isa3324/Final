# assembly_generator.py
import os


class ErroGeracaoAssembly(Exception):
    pass


def inicializarEstado(arvore_atribuida):
    """
    Cria as informações necessárias para gerar o Assembly.

    A árvore atribuída já contém:
    - tabela de símbolos;
    - comandos semanticamente válidos;
    - tipos inferidos;
    - marcação de possíveis resultados NULL.
    """

    return {
        "constantes": {},
        "ordem_constantes": [],
        "contador_constantes": 0,
        "contador_labels": 0,
        "contador_lacos": 0,
        "temporarios_laco": [],
        "memorias": sorted(arvore_atribuida.get("tabela_simbolos", {}).keys()),
        "quantidade_resultados": len(arvore_atribuida.get("comandos", [])),
    }


def novoLabel(prefixo, estado):
    label = f"{prefixo}_{estado['contador_labels']}"
    estado["contador_labels"] += 1
    return label


def novoTemporarioLaco(estado):
    """
    Cada enquanto precisa guardar temporariamente:
    - resultado da última execução;
    - informação se o resultado ainda é NULL.
    """

    indice = estado["contador_lacos"]
    estado["contador_lacos"] += 1

    label_valor = f"temp_laco_valor_{indice}"
    label_null = f"temp_laco_null_{indice}"

    estado["temporarios_laco"].append((label_valor, label_null))

    return label_valor, label_null


def normalizarDouble(valor):
    """
    Todos os valores numéricos são armazenados no Assembly como double.

    Exemplos:
    1   -> 1.0
    2.5 -> 2.5
    """

    texto = str(valor)

    if "." not in texto:
        texto += ".0"

    return texto


def obterConstante(valor, estado):
    """
    Cria ou reutiliza constantes da seção .data.
    """

    texto = normalizarDouble(valor)

    if texto == "0.0":
        return "const_zero"

    if texto == "1.0":
        return "const_um"

    if texto in estado["constantes"]:
        return estado["constantes"][texto]

    label = f"const_{estado['contador_constantes']}"
    estado["contador_constantes"] += 1

    estado["constantes"][texto] = label
    estado["ordem_constantes"].append((label, texto))

    return label


def labelMemoria(nome):
    """
    Prefixo para evitar conflito entre nome de variável e labels internos.
    """

    return f"mem_{nome}"


def gerarCabecalho():
    """
    Convenção durante geração de expressões:

    d0 = valor resultante da expressão
    r7 = flag de NULL
         0 -> resultado válido
         1 -> resultado NULL
    """

    return (
        ".syntax unified\n"
        ".arch armv7-a\n"
        ".fpu vfpv3\n"
        ".global _start\n\n"
        ".text\n"
        "_start:\n"
        "    ldr r10, =pilha_expr       @ pilha temporaria para expressoes\n"
        "    ldr r11, =resultados       @ resultados dos comandos principais\n"
        "    ldr r12, =resultados_null  @ flag NULL: 0=valor, 1=NULL\n\n"
    )


def gerarRodape(estado):
    quantidade = max(1, estado["quantidade_resultados"])

    codigo = ""

    codigo += "\nfim:\n"
    codigo += "    b fim\n\n"

    codigo += "erro_null:\n"
    codigo += "    @ NULL usado onde era necessario um valor numerico\n"
    codigo += "    b erro_null\n\n"

    codigo += "erro_div_zero:\n"
    codigo += "    @ tentativa de divisao por zero\n"
    codigo += "    b erro_div_zero\n\n"

    codigo += "erro_expoente:\n"
    codigo += "    @ expoente deve ser inteiro nao negativo\n"
    codigo += "    b erro_expoente\n\n"

    codigo += ".data\n"
    codigo += "    .align 3\n"

    codigo += "const_zero: .double 0.0\n"
    codigo += "const_um:   .double 1.0\n"

    for label, valor in estado["ordem_constantes"]:
        codigo += f"{label}: .double {valor}\n"

    for nome in estado["memorias"]:
        codigo += f"{labelMemoria(nome)}: .double 0.0\n"

    for label_valor, label_null in estado["temporarios_laco"]:
        codigo += f"{label_valor}: .double 0.0\n"
        codigo += f"{label_null}: .word 1\n"

    codigo += "    .align 3\n"
    codigo += f"resultados:      .space {quantidade * 8}\n"
    codigo += f"resultados_null: .space {quantidade * 4}\n"
    codigo += "    .align 3\n"
    codigo += "pilha_expr:      .space 2048\n"

    return codigo


def carregarConstante(label, registrador="d0"):
    return (
        f"    ldr r0, ={label}\n"
        f"    vldr {registrador}, [r0]\n"
    )


def exigirNaoNull():
    """
    Impede que NULL seja usado como operando numérico.
    """

    return (
        "    cmp r7, #0\n"
        "    bne erro_null\n"
    )


def empilharD0():
    """
    Empilha temporariamente o valor de d0.
    """

    return (
        "    vstr d0, [r10]\n"
        "    add r10, r10, #8\n"
    )


def recuperarEsquerdaComDireitaEmD1():
    """
    Antes desta função:
        d0 = operando direito
        topo da pilha = operando esquerdo

    Depois:
        d0 = operando esquerdo
        d1 = operando direito
    """

    return (
        "    vmov.f64 d1, d0\n"
        "    sub r10, r10, #8\n"
        "    vldr d0, [r10]\n"
    )


def gerarLiteral(no, estado):
    label = obterConstante(no["valor"], estado)

    codigo = f"    @ literal {no['valor']}\n"
    codigo += carregarConstante(label)
    codigo += "    mov r7, #0\n"

    return codigo


def gerarVariavel(no, estado):
    nome = no["nome"]

    codigo = f"    @ leitura da memoria {nome}\n"
    codigo += f"    ldr r9, ={labelMemoria(nome)}\n"
    codigo += "    vldr d0, [r9]\n"
    codigo += "    mov r7, #0\n"

    return codigo


def gerarLeituraMemoria(no, estado, indice_atual):
    return gerarNo(no["variavel"], estado, indice_atual)


def gerarAtribuicaoLiteral(no, estado, indice_atual):
    destino = no["destino"]

    codigo = f"    @ atribuicao literal para {destino}\n"
    codigo += gerarNo(no["valor"], estado, indice_atual)
    codigo += exigirNaoNull()
    codigo += f"    ldr r9, ={labelMemoria(destino)}\n"
    codigo += "    vstr d0, [r9]\n"
    codigo += "    mov r7, #0\n"

    return codigo


def gerarAtribuicaoVariavel(no, estado, indice_atual):
    destino = no["destino"]

    codigo = f"    @ atribuicao de variavel para {destino}\n"
    codigo += gerarNo(no["origem"], estado, indice_atual)
    codigo += exigirNaoNull()
    codigo += f"    ldr r9, ={labelMemoria(destino)}\n"
    codigo += "    vstr d0, [r9]\n"
    codigo += "    mov r7, #0\n"

    return codigo


def gerarOperandosBinarios(no, estado, indice_atual):
    """
    Gera os dois operandos de uma operação binária.

    Resultado:
        d0 = operando esquerdo
        d1 = operando direito
    """

    codigo = gerarNo(no["esquerda"], estado, indice_atual)
    codigo += exigirNaoNull()
    codigo += empilharD0()

    codigo += gerarNo(no["direita"], estado, indice_atual)
    codigo += exigirNaoNull()

    codigo += recuperarEsquerdaComDireitaEmD1()

    return codigo


def verificarDivisorDouble():
    return (
        "    ldr r0, =const_zero\n"
        "    vldr d3, [r0]\n"
        "    vcmp.f64 d1, d3\n"
        "    vmrs APSR_nzcv, FPSCR\n"
        "    beq erro_div_zero\n"
    )


def gerarDivisaoInteiraOuResto(operador):
    """
    O verificador semântico já garantiu que os operandos são inteiros.

    Convenções:
        /  -> divisão inteira
        // -> divisão inteira mantida por compatibilidade
        %  -> resto inteiro
    """

    codigo = verificarDivisorDouble()

    codigo += "    @ operandos inteiros ja foram validados semanticamente\n"
    codigo += "    @ calcula quociente e converte para inteiro\n"
    codigo += "    vdiv.f64 d2, d0, d1\n"
    codigo += "    vcvt.s32.f64 s4, d2\n"
    codigo += "    vcvt.f64.s32 d2, s4\n"

    if operador in {"/", "//"}:
        codigo += "    vmov.f64 d0, d2\n"

    elif operador == "%":
        codigo += "    @ resto = dividendo - (quociente * divisor)\n"
        codigo += "    vmul.f64 d3, d2, d1\n"
        codigo += "    vsub.f64 d0, d0, d3\n"

    codigo += "    mov r7, #0\n"

    return codigo


def gerarPotencia(estado):
    """
    Recebe:
        d0 = base
        d1 = expoente

    O expoente deve ser inteiro nao negativo.
    """

    inicio = novoLabel("pot_loop", estado)
    fim = novoLabel("pot_fim", estado)

    codigo = "    @ potenciacao: expoente inteiro nao negativo\n"

    codigo += "    vcvt.s32.f64 s4, d1\n"
    codigo += "    vmov r1, s4\n"

    codigo += "    cmp r1, #0\n"
    codigo += "    blt erro_expoente\n"

    codigo += "    vmov.f64 d3, d0\n"
    codigo += carregarConstante("const_um")

    codigo += f"{inicio}:\n"
    codigo += "    cmp r1, #0\n"
    codigo += f"    beq {fim}\n"
    codigo += "    vmul.f64 d0, d0, d3\n"
    codigo += "    sub r1, r1, #1\n"
    codigo += f"    b {inicio}\n"

    codigo += f"{fim}:\n"
    codigo += "    mov r7, #0\n"

    return codigo


def gerarOperacaoAritmetica(no, estado, indice_atual):
    operador = no["operador"]

    codigo = f"    @ operacao aritmetica {operador}\n"
    codigo += gerarOperandosBinarios(no, estado, indice_atual)

    if operador == "+":
        codigo += "    vadd.f64 d0, d0, d1\n"
        codigo += "    mov r7, #0\n"

    elif operador == "-":
        codigo += "    vsub.f64 d0, d0, d1\n"
        codigo += "    mov r7, #0\n"

    elif operador == "*":
        codigo += "    vmul.f64 d0, d0, d1\n"
        codigo += "    mov r7, #0\n"

    elif operador == "|":
        codigo += verificarDivisorDouble()
        codigo += "    vdiv.f64 d0, d0, d1\n"
        codigo += "    mov r7, #0\n"

    elif operador in {"/", "//", "%"}:
        codigo += gerarDivisaoInteiraOuResto(operador)

    elif operador == "^":
        codigo += gerarPotencia(estado)

    else:
        raise ErroGeracaoAssembly(
            f"Operador aritmético não implementado: {operador}"
        )

    return codigo


def gerarOperacaoRelacional(no, estado, indice_atual):
    operador = no["operador"]

    verdadeiro = novoLabel("rel_true", estado)
    fim = novoLabel("rel_fim", estado)

    saltos = {
        "==": "beq",
        "!=": "bne",
        ">": "bgt",
        "<": "blt",
        ">=": "bge",
        "<=": "ble",
    }

    if operador not in saltos:
        raise ErroGeracaoAssembly(
            f"Operador relacional não implementado: {operador}"
        )

    codigo = f"    @ operacao relacional {operador}\n"
    codigo += gerarOperandosBinarios(no, estado, indice_atual)

    codigo += "    vcmp.f64 d0, d1\n"
    codigo += "    vmrs APSR_nzcv, FPSCR\n"

    codigo += carregarConstante("const_zero")
    codigo += f"    {saltos[operador]} {verdadeiro}\n"
    codigo += f"    b {fim}\n"

    codigo += f"{verdadeiro}:\n"
    codigo += carregarConstante("const_um")

    codigo += f"{fim}:\n"
    codigo += "    mov r7, #0\n"

    return codigo


def testarCondicaoFalsa(label_falso):
    """
    Uma condição deve resultar em:
        d0 = 0.0 -> falso
        d0 = 1.0 -> verdadeiro

    NULL não pode ser usado como condição.
    """

    return (
        "    cmp r7, #0\n"
        "    bne erro_null\n"
        "    ldr r0, =const_zero\n"
        "    vldr d1, [r0]\n"
        "    vcmp.f64 d0, d1\n"
        "    vmrs APSR_nzcv, FPSCR\n"
        f"    beq {label_falso}\n"
    )


def gerarDecisao(no, estado, indice_atual):
    """
    Para:
        (condicao acao se)

    Se verdadeiro:
        retorna exatamente o resultado da ação,
        inclusive sua flag NULL.

    Se falso:
        retorna NULL.
    """

    falso = novoLabel("se_falso", estado)
    fim = novoLabel("se_fim", estado)

    codigo = "    @ decisao se\n"

    # Avalia a condição.
    codigo += gerarNo(no["condicao"], estado, indice_atual)
    codigo += testarCondicaoFalsa(falso)

    # Condição verdadeira:
    # executa a ação e NÃO altera r7 depois dela.
    # Assim, se a ação retornar NULL, o se externo também retorna NULL.
    codigo += gerarNo(no["acao"], estado, indice_atual)
    codigo += f"    b {fim}\n"

    # Condição falsa:
    # não houve resultado da ação.
    codigo += f"{falso}:\n"
    codigo += carregarConstante("const_zero")
    codigo += "    mov r7, #1          @ resultado NULL\n"

    codigo += f"{fim}:\n"

    return codigo

def gerarRepeticao(no, estado, indice_atual):
    """
    Para:
        (condicao acao enquanto)

    Se executar ao menos uma vez:
        retorna exatamente o resultado da última ação,
        inclusive a flag NULL.

    Se nunca executar:
        retorna NULL.
    """

    inicio = novoLabel("enquanto_inicio", estado)
    fim = novoLabel("enquanto_fim", estado)

    label_valor, label_null = novoTemporarioLaco(estado)

    codigo = "    @ repeticao enquanto\n"

    # Antes da primeira iteração, o laço ainda não produziu resultado.
    codigo += carregarConstante("const_zero")
    codigo += f"    ldr r9, ={label_valor}\n"
    codigo += "    vstr d0, [r9]\n"

    codigo += "    mov r7, #1          @ inicialmente NULL\n"
    codigo += f"    ldr r9, ={label_null}\n"
    codigo += "    str r7, [r9]\n"

    codigo += f"{inicio}:\n"

    # Avalia a condição.
    codigo += gerarNo(no["condicao"], estado, indice_atual)
    codigo += testarCondicaoFalsa(fim)

    # Executa a ação.
    # Não deve alterar r7 após gerarNo(), pois a ação pode retornar NULL.
    codigo += gerarNo(no["acao"], estado, indice_atual)

    # Guarda exatamente o resultado da última ação.
    codigo += f"    ldr r9, ={label_valor}\n"
    codigo += "    vstr d0, [r9]\n"

    codigo += f"    ldr r9, ={label_null}\n"
    codigo += "    str r7, [r9]\n"

    codigo += f"    b {inicio}\n"

    codigo += f"{fim}:\n"

    # Recupera o resultado final do laço.
    codigo += f"    ldr r9, ={label_valor}\n"
    codigo += "    vldr d0, [r9]\n"

    codigo += f"    ldr r9, ={label_null}\n"
    codigo += "    ldr r7, [r9]\n"

    return codigo


def adicionarOffset(codigo, registrador, offset):
    if offset != 0:
        codigo += f"    add {registrador}, {registrador}, #{offset}\n"

    return codigo


def gerarRes(no, estado, indice_atual):
    """
    Gera Assembly para o comando isolado (N RES).

    Regras:
    - N começa em zero;
    - (0 RES) busca o resultado imediatamente anterior;
    - (1 RES) busca o segundo resultado anterior;
    - (2 RES) busca o terceiro resultado anterior;
    - o valor e a flag NULL da linha referenciada são copiados;
    - RES nunca referencia o próprio comando atual.
    """

    indice = int(no["indice"])

    # A posição começa em zero:
    # indice_atual - 1         -> comando imediatamente anterior
    # indice_atual - (indice+1) -> posição pedida por RES
    alvo = indice_atual - (indice + 1)

    if alvo < 1:
        raise ErroGeracaoAssembly(
            f"RES inválido na linha {no.get('linha', '?')}: "
            f"a posição anterior {indice} não existe."
        )

    # Cada resultado double ocupa 8 bytes.
    # Cada flag NULL ocupa 4 bytes.
    offset_valor = (alvo - 1) * 8
    offset_null = (alvo - 1) * 4

    codigo = (
        f"    @ RES {indice}: carrega resultado do comando {alvo}\n"
    )

    # Carrega o valor exatamente como foi produzido.
    codigo += "    ldr r8, =resultados\n"
    codigo = adicionarOffset(codigo, "r8", offset_valor)
    codigo += "    vldr d0, [r8]\n"

    # Carrega a flag NULL correspondente.
    # r7 = 0 -> existe valor
    # r7 = 1 -> resultado é NULL
    codigo += "    ldr r8, =resultados_null\n"
    codigo = adicionarOffset(codigo, "r8", offset_null)
    codigo += "    ldr r7, [r8]\n"

    return codigo

def gerarNo(no, estado, indice_atual):
    """
    Encaminha cada tipo de nó da árvore atribuída para
    a respectiva função geradora.
    """

    categoria = no.get("categoria")

    if categoria == "literal":
        return gerarLiteral(no, estado)

    if categoria == "variavel":
        return gerarVariavel(no, estado)

    if categoria == "leitura_memoria":
        return gerarLeituraMemoria(no, estado, indice_atual)

    if categoria == "atribuicao_literal":
        return gerarAtribuicaoLiteral(no, estado, indice_atual)

    if categoria == "atribuicao_variavel":
        return gerarAtribuicaoVariavel(no, estado, indice_atual)

    if categoria == "operacao_aritmetica":
        return gerarOperacaoAritmetica(no, estado, indice_atual)

    if categoria == "operacao_relacional":
        return gerarOperacaoRelacional(no, estado, indice_atual)

    if categoria == "decisao":
        return gerarDecisao(no, estado, indice_atual)

    if categoria == "repeticao":
        return gerarRepeticao(no, estado, indice_atual)

    if categoria == "res":
        return gerarRes(no, estado, indice_atual)

    raise ErroGeracaoAssembly(
        f"Categoria não implementada no Assembly: {categoria}"
    )


def salvarResultado(indice):
    """
    Salva resultado e flag NULL do comando principal atual.
    """

    offset_valor = (indice - 1) * 8
    offset_null = (indice - 1) * 4

    codigo = f"    @ salva resultado do comando {indice}\n"

    codigo += "    ldr r8, =resultados\n"
    codigo = adicionarOffset(codigo, "r8", offset_valor)
    codigo += "    vstr d0, [r8]\n"

    codigo += "    ldr r8, =resultados_null\n"
    codigo = adicionarOffset(codigo, "r8", offset_null)
    codigo += "    str r7, [r8]\n\n"

    return codigo


def gerarAssembly(arvore_atribuida):
    """
    Entrada:
        árvore sintática atribuída semanticamente válida.

    Saída:
        string contendo código Assembly ARMv7 para Cpulator.

    Nenhuma expressão é calculada em Python.
    Python somente percorre a árvore e escreve o Assembly.
    """

    if arvore_atribuida.get("categoria") != "programa":
        raise ErroGeracaoAssembly(
            "A entrada do Assembly deve ser uma árvore atribuída de programa."
        )

    tipos = arvore_atribuida.get("tipos_validados", {})

    if tipos.get("erros_semanticos"):
        raise ErroGeracaoAssembly(
            "Assembly não gerado: existem erros semânticos."
        )

    estado = inicializarEstado(arvore_atribuida)

    codigo = gerarCabecalho()

    for indice, comando in enumerate(
        arvore_atribuida.get("comandos", []),
        start=1
    ):
        codigo += "    @ ==========================================\n"
        codigo += (
            f"    @ Comando {indice} - linha fonte "
            f"{comando.get('linha', '?')}\n"
        )
        codigo += "    @ ==========================================\n"

        codigo += gerarNo(comando, estado, indice)
        codigo += salvarResultado(indice)

    codigo += "    b fim\n"
    codigo += gerarRodape(estado)

    return codigo


def salvarAssembly(codigo, caminho="output/assembly_ultima_execucao.s"):
    diretorio = os.path.dirname(caminho)

    if diretorio:
        os.makedirs(diretorio, exist_ok=True)

    with open(caminho, "w", encoding="utf-8") as arquivo:
        arquivo.write(codigo)