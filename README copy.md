- Coisas para anotar sobre Fase 3.

- Implementar em analisador lexico a capacidade de descartar o senguinte em qualquer lugar do codigo. *{comantario}*. MUITO IMPORTANTE: NÃO PRECISA ALTERAR A GRAMTICA, VAI SER TRATADO NO ANALIZADOR LEXICO.

- Para utilizar um MEM, a variavel deve ser defenida. agora nao aceita quando ela nao for defenida. acho que deve ser testado isso no analisador semantico.

- Regras de validação de tipo para a linguagem - feito pelo analizador semantico. Sendo os tipos utilizados: inteiros, reais e lógicos (bool).
Deve ser claramente defividas e documentadas em cálculos de sequentes
    - sendo que, a definicao de tipos em artefatos nao literais sera inferida a partir do contexto. Deve ser capaz de realizar inferencia de tipos e validar as operacoes de acordo com as regras de compatibilidade de tipos definidas.
    - Os tipos usados nesta linguagem deve ser estáticos e fortes, são definidos e nao pode ser alterados posteriormente, operacoes entre tipos imcompativeis deve resultadr em erros semanticos.

- O assemble deve ser feito a partir pela árvore sinática aumentada gerada pelo analizador semantico. sem precisar representar intermadiria

- nao entendi onde deve fazer as funcoes de teste




1. Alterar lexer para ignorar comentários *{ ... }*
2. Criar semantico.py
3. Criar função construirTabelaSimbolos(arvore)
4. Criar função verificarTipos(arvore, tabela_simbolos)
5. Criar função gerarArvoreAtribuida(arvore, tabela_simbolos, tipos)
6. Salvar arvore_atribuida.json
7. Criar tests/teste_semantico.py
8. Só depois mexer em gerarAssembly(arvore_atribuida)

lexer        -> remove comentários e gera tokens
parser       -> valida sintaxe
semantico    -> valida variáveis e tipos
arvore       -> gera/salva árvore
assembly     -> gera código a partir da árvore atribuída
tests        -> valida cada parte separadamente
