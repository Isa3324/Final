# Sobre o que deve ser feito

1. Ler a gramática
2. Separar terminais e não-terminais
3. Calcular FIRST
4. Calcular FOLLOW
5. Montar a tabela LL(1)
6. Verificar conflitos
7. Mostrar:
   - FIRST de cada não-terminal
   - FOLLOW de cada não-terminal
   - Tabela LL(1)
   - Se é LL(1) ou não




Teria o seguinte:

    calcularFirst():
        enquanto houver mudança:
            para cada produção A -> α:
                adicione FIRST(α) em FIRST(A)

    calcularFollow():
        coloque $ em FOLLOW(S)
        
        enquanto houver mudança:
            para cada produção A -> α:
                para cada não-terminal B dentro de α:
                    veja o que vem depois de B
                    adicione FIRST(depois) sem ε em FOLLOW(B)
                    
                    se depois pode virar ε:
                        adicione FOLLOW(A) em FOLLOW(B)

    construirTabela():
        para cada produção A -> α:
            para cada terminal a em FIRST(α):
                tabela[A][a] recebe A -> α
                
            se ε está em FIRST(α):
                para cada terminal b em FOLLOW(A):
                    tabela[A][b] recebe A -> α
                    
            se alguma célula receber duas regras:
                conflito