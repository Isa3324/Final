#assembly_generator
from lexer import (
    token_EPar, token_DPar, token_Num, token_OP,
    token_Mem, token_Res, token_Invalido
)

def inicializar_estado():
    return {
        "codigo_texto": "",
        "constantes": {},
        "ordem_constantes": [],
        "contador_constantes": 0,
        "indice_linha": 0,
        "contador_labels": 0,
        "memorias": set()
    }

def obter_ou_criar_constante(valor, estado):
    """
    Se o valor já tiver constante, reutiliza.
    Senão, cria uma nova.
    """
    if valor in estado["constantes"]:
        return estado["constantes"][valor]

    label = f"const_{estado['contador_constantes']}"
    estado["contador_constantes"] += 1

    estado["constantes"][valor] = label
    estado["ordem_constantes"].append((label, valor))

    return label

def adicionar_cabecalho():
    codigo = ""
    codigo += ".syntax unified\n"
    codigo += ".global _start\n\n"
    codigo += ".text\n"
    codigo += "_start:\n"
    codigo += "    ldr r10, =pilha          @ topo da pilha\n"
    codigo += "    ldr r11, =resultados     @ vetor de resultados\n"
    codigo += "\n"
    return codigo

def adicionar_rodape(estado):
    codigo = ""
    codigo += "fim:\n"
    codigo += "    b fim\n\n"
    codigo += "erro_div_zero:\n"
    codigo += "    b erro_div_zero\n\n"
    codigo += ".data\n"
    codigo += "    .align 8\n"

    codigo += "zero_const: .double 0.0\n"
    codigo += "const_um: .double 1.0\n"

    for label, valor in estado["ordem_constantes"]:
        valor_str = str(valor)
        if "." not in valor_str:
            valor_str += ".0"
        codigo += f"{label}: .double {valor_str}\n"

    for nome_mem in sorted(estado["memorias"]):
        codigo += f"{nome_mem}: .double 0.0\n"

    codigo += "pilha: .space 2048\n"
    codigo += "resultados: .space 800\n"
    return codigo

def gerar_res(n, indice_linha):
    """
    Gera o assembly para (N RES),
    onde N significa 'N linhas anteriores'.
    """
    linha_alvo = indice_linha - n

    trecho = ""

    if linha_alvo < 1:
        trecho += f"    @ RES invalido: ({n} RES) na linha {indice_linha}\n"
        trecho += "    ldr r0, =zero_const\n"
        trecho += "    vldr d0, [r0]\n"
        trecho += "    vstr d0, [r10]\n"
        trecho += "    add r10, r10, #8\n"
        return trecho

    offset = (linha_alvo - 1) * 8

    trecho += f"    @ RES -> carregar resultado da linha {linha_alvo}\n"
    trecho += "    ldr r9, =resultados\n"
    if offset != 0:
        trecho += f"    add r9, r9, #{offset}\n"
    trecho += "    vldr d0, [r9]\n"
    trecho += "    vstr d0, [r10]\n"
    trecho += "    add r10, r10, #8\n"

    return trecho

def gerar_push_numero(valor, estado):
    label = obter_ou_criar_constante(valor, estado)

    trecho = ""
    trecho += f"    @ push {valor}\n"
    trecho += f"    ldr r0, ={label}\n"
    trecho += f"    vldr d0, [r0]\n"
    trecho += f"    vstr d0, [r10]\n"
    trecho += f"    add r10, r10, #8\n"
    return trecho

def gerar_operador(op):
    trecho = ""
    trecho += f"    @ operador {op}\n"
    trecho += "    sub r10, r10, #8\n"
    trecho += "    vldr d1, [r10]\n"
    trecho += "    sub r10, r10, #8\n"
    trecho += "    vldr d0, [r10]\n"

    # divisão real
    if op == "/":
        trecho += "    @ verificar divisao por zero (double)\n"
        trecho += "    ldr r0, =zero_const\n"
        trecho += "    vldr d3, [r0]\n"
        trecho += "    vcmp.f64 d1, d3\n"
        trecho += "    vmrs APSR_nzcv, FPSCR\n"
        trecho += "    beq erro_div_zero\n"
        trecho += "    vdiv.f64 d2, d0, d1\n"

    elif op == "+":
        trecho += "    vadd.f64 d2, d0, d1\n"

    elif op == "-":
        trecho += "    vsub.f64 d2, d0, d1\n"

    elif op == "*":
        trecho += "    vmul.f64 d2, d0, d1\n"

    trecho += "    vstr d2, [r10]\n"
    trecho += "    add r10, r10, #8\n"

    return trecho

def gerar_divisao_ou_resto(op):
    trecho = ""
    trecho += f"    @ operador {op}\n"
    trecho += "    sub r10, r10, #8\n"
    trecho += "    vldr d1, [r10]\n"
    trecho += "    sub r10, r10, #8\n"
    trecho += "    vldr d0, [r10]\n"

    trecho += "    @ double -> int\n"
    trecho += "    vcvt.s32.f64 s0, d0\n"
    trecho += "    vmov r0, s0\n"
    trecho += "    vcvt.s32.f64 s1, d1\n"
    trecho += "    vmov r1, s1\n"

    trecho += "    @ verificar divisao por zero\n"
    trecho += "    cmp r1, #0\n"
    trecho += "    beq erro_div_zero\n"

    trecho += "    @ quociente = A // B\n"
    trecho += "    sdiv r2, r0, r1\n"

    if op == "//":
        trecho += "    @ resultado = quociente\n"
        trecho += "    vmov s2, r2\n"

    elif op == "%":
        trecho += "    @ resto = A - (quociente * B)\n"
        trecho += "    mul r3, r2, r1\n"
        trecho += "    sub r4, r0, r3\n"
        trecho += "    vmov s2, r4\n"

    trecho += "    @ int -> double\n"
    trecho += "    vcvt.f64.s32 d2, s2\n"

    trecho += "    vstr d2, [r10]\n"
    trecho += "    add r10, r10, #8\n"
    return trecho

def novo_label(base, estado):
    label = f"{base}_{estado['contador_labels']}"
    estado["contador_labels"] += 1
    return label

def gerar_potencia(estado):
    loop_label = novo_label("loop_pot", estado)
    fim_label = novo_label("fim_pot", estado)

    trecho = ""
    trecho += "    @ operador ^\n"
    trecho += "    sub r10, r10, #8\n"
    trecho += "    vldr d1, [r10]\n"
    trecho += "    sub r10, r10, #8\n"
    trecho += "    vldr d0, [r10]\n"

    trecho += "    @ converter expoente B para inteiro\n"
    trecho += "    vcvt.s32.f64 s1, d1\n"
    trecho += "    vmov r1, s1\n"

    trecho += "    @ resultado = 1.0\n"
    trecho += "    ldr r0, =const_um\n"
    trecho += "    vldr d2, [r0]\n"

    trecho += f"{loop_label}:\n"
    trecho += "    cmp r1, #0\n"
    trecho += "    blt erro_expoente_negativo\n"
    trecho += f"    beq {fim_label}\n"
    trecho += "    vmul.f64 d2, d2, d0\n"
    trecho += "    sub r1, r1, #1\n"
    trecho += f"    b {loop_label}\n"

    trecho += f"{fim_label}:\n"
    trecho += "    vstr d2, [r10]\n"
    trecho += "    add r10, r10, #8\n"
    return trecho

def gerar_store_mem(nome_mem, estado):
    estado["memorias"].add(nome_mem)

    trecho = ""
    trecho += f"    @ store em memoria {nome_mem}\n"
    trecho += f"    ldr r9, ={nome_mem}\n"
    trecho += "    sub r10, r10, #8\n"
    trecho += "    vldr d0, [r10]\n"
    trecho += "    vstr d0, [r9]\n"
    trecho += "    @ recoloca na pilha\n"
    trecho += "    vstr d0, [r10]\n"
    trecho += "    add r10, r10, #8\n"
    return trecho

def gerar_load_mem(nome_mem, estado):
    estado["memorias"].add(nome_mem)

    trecho = ""
    trecho += f"    @ load de memoria {nome_mem}\n"
    trecho += f"    ldr r9, ={nome_mem}\n"
    trecho += "    vldr d0, [r9]\n"
    trecho += "    vstr d0, [r10]\n"
    trecho += "    add r10, r10, #8\n"
    return trecho

def salvar_resultado_da_linha(indice_linha):
    trecho = ""
    trecho += f"    @ salva resultado da linha {indice_linha}\n"
    trecho += "    sub r10, r10, #8\n"
    trecho += "    vldr d0, [r10]\n"
    trecho += "    vstr d0, [r11]\n"
    trecho += "    add r11, r11, #8\n"
    return trecho

def extrair_tokens_uteis(tokens):
    uteis = []
    for tipo, lexema, pos in tokens:
        if tipo not in (token_EPar, token_DPar):
            uteis.append((tipo, lexema, pos))
    return uteis

def gerarAssembly(tokens, estado):
    """
    Gera o Assembly pelos tokens
    """

    estado["indice_linha"] += 1
    indice = estado["indice_linha"]

    trecho = ""
    trecho += f"    @ ==========================================\n"
    trecho += f"    @ Linha {indice}\n"
    trecho += f"    @ ==========================================\n"

    uteis = extrair_tokens_uteis(tokens)

    # Caso: (N RES)
    if len(uteis) == 2 and uteis[0][0] == token_Num and uteis[1][0] == token_Res:
        n = int(float(uteis[0][1]))
        trecho += gerar_res(n, indice)
        trecho += salvar_resultado_da_linha(indice)
        trecho += "\n"
        estado["codigo_texto"] += trecho
        return
    
    # (X)
    if len(uteis) == 1 and uteis[0][0] == token_Mem:
        nome_mem = uteis[0][1]
        trecho += gerar_load_mem(nome_mem, estado)
        trecho += salvar_resultado_da_linha(indice)
        estado["codigo_texto"] += trecho
        trecho += "\n"
        estado["codigo_texto"] += trecho
        return
      

    # (5 X)
    if (
        len(uteis) == 2
        and uteis[0][0] == token_Num
        and uteis[1][0] == token_Mem
    ):
        valor = uteis[0][1]
        nome_mem = uteis[1][1]
        trecho += gerar_push_numero(valor, estado)
        trecho += gerar_store_mem(nome_mem, estado)
        trecho += salvar_resultado_da_linha(indice)
        estado["codigo_texto"] += trecho
        estado["codigo_texto"] += trecho
        return

    # Caso geral
    for tipo, lexema, pos in uteis:
        if tipo == token_Num:
            trecho += gerar_push_numero(lexema, estado)

        elif tipo == token_OP and lexema in ["+", "-", "*", "/"]:
            trecho += gerar_operador(lexema)

        elif tipo == token_OP and lexema in ["//", "%"]:
            trecho += gerar_divisao_ou_resto(lexema)

        elif tipo == token_OP and lexema == "^":
            trecho += gerar_potencia(estado)

        elif tipo == token_Mem:
            trecho += gerar_load_mem(lexema, estado)

        elif tipo == token_Invalido:
            trecho += f"    @ token invalido '{lexema}' na posicao {pos}\n"

        else:
            trecho += f"    @ token '{lexema}' ainda nao implementado\n"

    trecho += salvar_resultado_da_linha(indice)
    trecho += "\n"

    estado["codigo_texto"] += trecho

def montar_codigo_final(estado):
    codigo = ""
    codigo += adicionar_cabecalho()
    codigo += estado["codigo_texto"]
    codigo += adicionar_rodape(estado)
    return codigo