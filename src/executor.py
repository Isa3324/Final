def resolver_grupo(grupo, memoria, resultados_anteriores):
    # grupo == []
    if  not grupo:
        return None
    # (NUM NUM OP)
    if len(grupo) == 3:
        pos0,pos1,pos2 = grupo

        if pos2[0] != "OP":
            return None
        
        # Ver se e de um variavel de memoria ou um numero
        def get_valor(pos):
            if pos[0] == "NUM":
                return float(pos[1])
            elif pos[0] == "MEM":
                return memoria.get(pos[1], 0)  # MEM não inicializada = 0
            else:
                return None
        
        NUM1 = get_valor(pos0)
        NUM2 = get_valor(pos1)
        
        if NUM1 is None or NUM2 is None:
            return None
        
        op = pos2[1]

        # se for difidir por 0
        if op in ["/", "//", "%"] and NUM2 == 0:
            return None

        if op == "+":
            return NUM1 + NUM2

        elif op == "-":
            return NUM1 - NUM2

        elif op == "*":
            return NUM1 * NUM2

        elif op == "/":
            return NUM1 / NUM2

        elif op == "//":
            if not NUM1.is_integer() or not NUM2.is_integer():
                return None
            return int(NUM1) // int(NUM2)

        elif op == "%":
            if not NUM1.is_integer() or not NUM2.is_integer():
                return None
            return int(NUM1) % int(NUM2)

        elif op == "^":
            if not NUM2.is_integer() or NUM2 <= 0:
                return None
            return NUM1 ** int(NUM2)

        return None       
    
    # (NUM MEM) / (NUM, RES)
    if len(grupo) == 2:
        pos0,pos1 = grupo

        # (NUM MEM) para guardar memoria
        if pos0[0] == "NUM" and pos1[0] == "MEM":
            NUM1 = float(pos0[1])
            nome = pos1[1]
            memoria[nome] = NUM1
            return NUM1
        
        # (NUM RES) pegar reposta na posisao NUM
        if pos0[0] == "NUM" and pos1[0] == "RES":
            num = int(float(pos0[1]))
            
            if num <= 0 or num > len(resultados_anteriores):
                return None
            return resultados_anteriores[-num]
        return None
    
    # (MEM) ler memoria
    if len(grupo) == 1:
        pos0 = grupo[0]

        if pos0[0] == "MEM":
            nome = pos0[1]
            if nome in memoria:
                return memoria[nome]
            return 0
        
        if pos0[0] == "NUM":
            return float(pos0[1])
        return None
    return None
            
def executarExpressao(tokens, memoria, resultados_anteriores):
    # ver se tem um tokens invalido, parar a execucao da expressao
    pilha = []
    for token in tokens:
        if token[0] == "INVALIDO":
            return None, memoria, resultados_anteriores

        elif token[0] != "DPAR":
            pilha.append(token)

        else:
            grupo = []

            while pilha:
                tok = pilha.pop()

                if tok[0] != "EPAR":
                    grupo.append(tok)
                else:
                    break

            grupo.reverse()

            resultado = resolver_grupo(grupo, memoria, resultados_anteriores)

            if resultado is None:
                print("Erro na expressão", tokens)
                return None, memoria, resultados_anteriores

            pilha.append(("NUM", str(resultado), -1))
    # resultado final
    if len(pilha) == 1:
        resultado_final = float(pilha[0][1])
        resultados_anteriores.append(resultado_final)
        return resultado_final, memoria, resultados_anteriores

    return None, memoria, resultados_anteriores

