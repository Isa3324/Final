# Compilador de Linguagem Pós-Fixada com Análise Semântica e Geração Assembly

## Informações Acadêmicas

| Informação                | Dados                               |
| ------------------------- | ----------------------------------- |
| Instituição de Ensino |            PUC                         |
| Disciplina                | Linguagens Formais e Compiladores             |
| Professor(a)              | FRANK COELHO DE ALCANTARA |
| Ano                       | 2026                       |
| Grupo no Canvas           | `RA2 24`                            |

## Integrantes do Grupo

Em ordem alfabética:

* Isa Stohler Bertolaccini


---

# 1. Descrição do Projeto

Este projeto implementa um compilador para uma linguagem de expressões em **notação polonesa reversa**, também chamada de **RPN** ou notação pós-fixada.

A linguagem utiliza comandos entre parênteses, como:

```txt
(2 3 +)
```

Nesse exemplo, os operandos aparecem antes do operador:

```txt
2 + 3
```

Além das operações numéricas, a linguagem possui:

```txt
variáveis de memória;
referência a resultados anteriores com RES;
estruturas condicionais com se;
estruturas de repetição com enquanto;
comentários;
análise sintática LL(1);
análise semântica;
geração de Assembly ARMv7 para execução no CPUlator.
```

Todo programa completo deve começar com:

```txt
(START)
```

e terminar com:

```txt
(END)
```

Exemplo:

```txt
(START)
(1 A)
(2 B)
(A B +)
(END)
```

---

# 2. Organização do Projeto

A implementação foi separada em módulos, de acordo com cada etapa do compilador.

```txt
projeto/
│
├── README.md
│
├── docs/
│   └── regras_tipos.md
│
├── output/
│   ├── tokens_ultima_execucao.txt
│   ├── arvore_sintatica.txt
│   ├── arvore_sintatica.json
│   ├── tabela_simbolos.json
│   ├── tipos_inferidos.json
│   ├── arvore_atribuida.json
│   └── assembly_ultima_execucao.s
│
├── tests/
│   ├── gramaticatest.txt
│   ├── tabela_ll1.json
│   ├── teste1.txt
│   ├── teste2.txt
│   ├── teste3.txt
│   ├── teste4.txt
│   ├── teste5.txt
│   └── teste6.txt
│
└── src/
    ├── main.py
    ├── file_reader.py
    ├── lexer.py
    ├── token_reader.py
    ├── gramatica.py
    ├── parser.py
    ├── arvore.py
    ├── semantico.py
    ├── tabela_simbolos.py
    ├── verificar_tipos.py
    ├── arvore_atribuida.py
    └── assembly_generator.py
```

## 2.1 Responsabilidade dos Módulos

| Arquivo                 | Responsabilidade                                                       |
| ----------------------- | ---------------------------------------------------------------------- |
| `main.py`               | Coordena a execução completa do compilador via linha de comando.       |
| `file_reader.py`        | Lê o arquivo fonte recebido como argumento.                            |
| `lexer.py`              | Reconhece tokens e remove comentários no formato `*{ ... }*`.          |
| `token_reader.py`       | Salva e relê os tokens em formato JSON.                                |
| `gramatica.py`          | Define a gramática, calcula FIRST e FOLLOW e constrói a tabela LL(1).  |
| `parser.py`             | Executa o parsing LL(1) com pilha e produz a derivação/árvore inicial. |
| `arvore.py`             | Salva e imprime a árvore sintática inicial.                            |
| `semantico.py`          | Integra lexer, parser e preparação da entrada semântica.               |
| `tabela_simbolos.py`    | Registra variáveis, atribuições, usos e erros de declaração.           |
| `verificar_tipos.py`    | Infere tipos e valida operações, controles, `RES` e `NULL`.            |
| `arvore_atribuida.py`   | Produz a árvore sintática anotada com informações semânticas.          |
| `assembly_generator.py` | Gera código Assembly ARMv7 a partir da árvore atribuída.               |

---

# 3. Como Executar

## 3.1 Requisitos

O projeto utiliza:

```txt
Python 3
```

Não é necessário instalar bibliotecas externas para executar os módulos atuais, pois são utilizadas apenas bibliotecas padrão do Python, como:

```txt
os
sys
json
decimal
```

## 3.2 Executar um Programa Fonte

A execução é realizada por argumento de linha de comando, sem menu interativo.

A partir da raiz do projeto, execute:

```bash
python src/main.py tests/teste1.txt
```

No Windows, também pode ser utilizado:

```bash
py src/main.py tests/teste1.txt
```

Caso nenhum arquivo `.txt` seja informado, o programa apresenta a forma correta de uso:

```txt
python src/main.py <arquivo.txt>
```

## 3.3 Saídas Geradas

Quando o programa for válido, os seguintes artefatos são produzidos na pasta `output`:

| Arquivo                      | Conteúdo                                          |
| ---------------------------- | ------------------------------------------------- |
| `tokens_ultima_execucao.txt` | Vetor de tokens reconhecido pelo lexer.           |
| `arvore_sintatica.txt`       | Visualização textual da árvore sintática inicial. |
| `arvore_sintatica.json`      | Árvore sintática inicial em JSON.                 |
| `tabela_simbolos.json`       | Variáveis, tipos, linhas de definição e uso.      |
| `tipos_inferidos.json`       | Tipos inferidos e validações semânticas.          |
| `arvore_atribuida.json`      | Árvore anotada utilizada na geração de código.    |
| `assembly_ultima_execucao.s` | Código Assembly final.                            |

No início de cada nova execução, os artefatos da execução anterior são removidos. Assim, um programa inválido não deixa um arquivo Assembly antigo na pasta `output`.

## 3.4 Gerar o Relatório da Gramática LL(1)

A gramática possui funções específicas para gerar:

```txt
tests/gramaticatest.txt
tests/tabela_ll1.json
```

Execute, a partir da raiz do projeto:

```bash
python -c "import sys; sys.path.insert(0, 'src'); from gramatica import mostrargramatica; mostrargramatica()"
```

O arquivo `gramaticatest.txt` registra:

```txt
gramática utilizada;
terminais e não-terminais;
conjuntos FIRST;
conjuntos FOLLOW;
tabela LL(1);
resultado da verificação de conflitos.
```

## 3.5 Executar o Assembly

Após executar um programa semanticamente válido, abra o arquivo:

```txt
output/assembly_ultima_execucao.s
```

no CPUlator configurado para ARMv7/DE1-SoC.

Ao finalizar a execução, o programa permanece no rótulo:

```asm
fim:
    b fim
```

Nesse momento, os valores podem ser conferidos na memória:

```txt
mem_<VARIAVEL>
resultados
resultados_null
```

---

# 4. Descrição da Linguagem

## 4.1 Tokens

| Token      | Significado                              | Exemplo                          |                        |
| ---------- | ---------------------------------------- | -------------------------------- | ---------------------- |
| `START`    | Início do programa                       | `(START)`                        |                        |
| `END`      | Fim do programa                          | `(END)`                          |                        |
| `EPAR`     | Parêntese de abertura                    | `(`                              |                        |
| `DPAR`     | Parêntese de fechamento                  | `)`                              |                        |
| `NUM`      | Literal numérico                         | `2`, `2.00`                      |                        |
| `MEM`      | Variável de memória em letras maiúsculas | `A`, `TOTAL`                     |                        |
| `RES`      | Recupera resultado anterior              | `(0 RES)`                        |                        |
| `OP`       | Operador aritmético                      | `+`, `-`, `*`, \| , `/`, `//`, `%`, `^` |
| `OPREL`    | Operador relacional                      | `==`, `!=`, `>`, `<`, `>=`, `<=` |                        |
| `SE`       | Estrutura condicional                    | `se`                             |                        |
| `ENQUANTO` | Estrutura de repetição                   | `enquanto`                       |                        |

Observações:

```txt
START e END só são válidos nas formas completas (START) e (END).
RES é escrito em letras maiúsculas.
se e enquanto são escritos em letras minúsculas.
Identificadores MEM são compostos por letras latinas maiúsculas.
```

## 4.2 Comentários

Comentários começam com:

```txt
*{
```

e terminam com:

```txt
}*
```

Eles podem aparecer:

```txt
em uma linha inteira;
ao final de um comando;
entre elementos de uma expressão;
em múltiplas linhas.
```

Exemplo:

```txt
(START)
*{ comentario em linha inteira }*
(1 A) *{ comentario ao final da linha }*
((A 2 <) *{ comentario entre elementos }* A se)
(END)
```

O conteúdo dos comentários é descartado durante a análise léxica. As quebras de linha internas são preservadas para que mensagens de erro continuem apontando a linha correta do arquivo fonte.

---

# 5. Tipos Suportados

A linguagem possui quatro categorias semânticas relevantes:

| Tipo      | Descrição                                                                            |
| --------- | ------------------------------------------------------------------------------------ |
| `inteiro` | Literal numérico escrito sem ponto decimal, como `2` ou `0`.                         |
| `real`    | Literal decimal ou qualquer variável `MEM`, como `2.00` ou `A`.                      |
| `logico`  | Tipo interno produzido por uma comparação usada como condição de `se` ou `enquanto`. |
| `NULL`    | Ausência de resultado de uma estrutura de controle.                                  |

## 5.1 Variáveis

Toda variável armazenada em memória possui tipo:

```txt
real
```

independentemente do literal utilizado em sua atribuição:

```txt
(1 A)    -> A : real
(1.00 A) -> A : real
```

As únicas formas de atribuição permitidas são:

```txt
(NUM MEM)
(MEM MEM)
```

Exemplos:

```txt
(1 A)
(A B)
```

Atribuir o resultado de uma expressão diretamente para uma variável não é permitido:

```txt
((A 1 +) A)
```

## 5.2 Operações Numéricas

| Operador | Regra de tipo |
| --- | --- |
| `+`, `-`, `*` | Aceitam inteiro e real; promovem para `real` caso algum operando seja real. |
| `\|` | Divisão real; aceita números e retorna `real`. |
| `/`, `//`, `%` | Exigem dois operandos `inteiro` e retornam `inteiro`. |
| `^` | Aceita base numérica e expoente literal numericamente inteiro não negativo. |
Exemplos válidos:

```txt
(2 3 +)
(2.00 3 +)
(4.00 2 |)
(2 0 ^)
(2.00 3.00 ^)
```

Exemplos inválidos:

```txt
(2.00 3.50 ^)
```

## 5.3 Operadores Relacionais

Os operadores relacionais são:

```txt
==  !=  >  <  >=  <=
```

Eles aceitam operandos numéricos, mas somente são válidos como condição direta de:

```txt
se
enquanto
```

Válido:

```txt
((A B <) A se)
```

Inválido:

```txt
(A B <)
```

O tipo `logico` existe somente durante a validação da condição; ele não representa um resultado comum de linha.

## 5.4 `se`, `enquanto` e `NULL`

A decisão possui formato:

```txt
(condicao acao se)
```

O laço possui formato:

```txt
(condicao acao enquanto)
```

Regras:

```txt
se a condição de se for falsa, o resultado é NULL;
se enquanto não executar nenhuma vez, o resultado é NULL;
se uma ação interna retornar NULL, o controle externo propaga NULL;
NULL não é o mesmo que o número 0;
um resultado que pode ser NULL não pode ser usado em operação aritmética ou relacional.
```

Uma variável nova não pode ser definida pela primeira vez dentro de `se` ou `enquanto`. Porém, uma variável já definida antes pode ser reatribuída dentro da estrutura.

## 5.5 `RES`

O comando `RES` possui formato:

```txt
(N RES)
```

Ele só pode aparecer como comando principal isolado.

A contagem começa em zero:

| Comando   | Referência                       |
| --------- | -------------------------------- |
| `(0 RES)` | Resultado imediatamente anterior |
| `(1 RES)` | Segundo resultado anterior       |
| `(2 RES)` | Terceiro resultado anterior      |

`RES` copia exatamente o resultado referenciado:

```txt
valor numérico permanece valor numérico;
NULL permanece NULL.
```

Exemplos válidos:

```txt
(START)
(10 A)
(0 RES)
(END)
```

Exemplos inválidos:

```txt
((0 RES) 2 +)
(0.00 RES)
```

---

# 6. Gramática Sintática em EBNF

A gramática sintática implementada é representada abaixo em EBNF.

```ebnf
programa         = START, lista_comandos, END ;

lista_comandos   = { comando } ;

comando          = EPAR, conteudo, DPAR ;

conteudo         = MEM, cont_mem
                 | NUM, cont_num
                 | comando, cont_comando ;

cont_mem         = MEM, fim_mem
                 | NUM, operador_final
                 | comando, operador_final
                 | ε ;

cont_num         = MEM, fim_mem
                 | RES
                 | NUM, operador_final
                 | comando, operador_final ;

cont_comando     = MEM, fim_mem
                 | NUM, operador_final
                 | comando, operador_final ;

fim_mem          = operador_final
                 | ε ;

operador_final   = OP
                 | OPREL
                 | SE
                 | ENQUANTO ;
```

## 6.1 Terminais

```txt
START
END
EPAR
DPAR
NUM
MEM
RES
OP
OPREL
SE
ENQUANTO
```

## 6.2 Restrições Semânticas Aplicadas Sobre a Gramática

A gramática aceita a estrutura geral dos comandos. A análise semântica restringe construções que, embora sintaticamente formadas, não pertencem à linguagem válida implementada.

| Estrutura                  | Regra semântica                                            |
| -------------------------- | ---------------------------------------------------------- |
| `(NUM MEM)`                | Define ou reatribui uma variável `real`.                   |
| `(MEM MEM)`                | Copia uma variável já definida para outra variável `real`. |
| `(expressao MEM)`          | Proibida.                                                  |
| `(A B OPREL)`              | Só pode ser condição direta de `se` ou `enquanto`.         |
| `(N RES)`                  | Só pode aparecer isolado; `N` é inteiro não negativo.      |
| `(condicao acao se)`       | Condição deve ser `logico`; resultado pode ser `NULL`.     |
| `(condicao acao enquanto)` | Condição deve ser `logico`; resultado pode ser `NULL`.     |

---

## 6.3 Atributos Semânticos Associados às Produções

| Produção | Atributo produzido | Regra |
| --- | --- | --- |
| `(NUM MEM)` | `tipo = real` | Toda variável armazenada em memória possui tipo `real`. |
| `(MEM MEM)` | `tipo = real` | A origem deve ter sido definida anteriormente. |
| `(e1 e2 OP)` | `tipo_resultado` | Definido pelas regras numéricas da seção 7. |
| `(cond acao se)` | `tipo_resultado`, `pode_ser_null = true` | A condição deve ser `logico`. |
| `(cond acao enquanto)` | `tipo_resultado`, `pode_ser_null = true` | A condição deve ser `logico`. |
| `(N RES)` | `tipo_resultado`, `pode_ser_null` | Copia os atributos do resultado anterior referenciado. |

# 7. Gramática Atribuída e Regras Semânticas

A análise utiliza um ambiente de tipos `Γ`, que registra as variáveis já definidas no arquivo atual.

## 7.1 Literais

```txt
n é literal sem ponto decimal
------------------------------
Γ ⊢ n : inteiro
```

```txt
r é literal com ponto decimal
------------------------------
Γ ⊢ r : real
```

## 7.2 Variáveis de Memória

```txt
Γ ⊢ v : inteiro ou real       X ainda não definida
---------------------------------------------------
Γ, X:real ⊢ (v X) : real
```

```txt
Γ(A) = real
------------------------
Γ, B:real ⊢ (A B) : real
```

## 7.3 Operações Aritméticas

Para `op ∈ {+, -, *}`:

```txt
Γ ⊢ e1 : numérico     Γ ⊢ e2 : numérico
-----------------------------------------
Γ ⊢ (e1 e2 op) : promoção(e1, e2)
```

Para divisão real:

```txt
Γ ⊢ e1 : numérico     Γ ⊢ e2 : numérico
-----------------------------------------
Γ ⊢ (e1 e2 |) : real
```

Para divisão inteira e resto:

```txt
Γ ⊢ e1 : inteiro     Γ ⊢ e2 : inteiro
---------------------------------------
Γ ⊢ (e1 e2 /) : inteiro
```

```txt
Γ ⊢ e1 : inteiro     Γ ⊢ e2 : inteiro
---------------------------------------
Γ ⊢ (e1 e2 %) : inteiro
```

Para potenciação:

```txt
Γ ⊢ base : numérico
expoente é literal numérico
valor(expoente) ∈ ℤ
valor(expoente) ≥ 0
-------------------------------------------------
Γ ⊢ (base expoente ^) : promoção(base, expoente)
```

## 7.4 Operadores Relacionais

```txt
Γ ⊢ e1 : numérico     Γ ⊢ e2 : numérico     oprel ∈ {==, !=, >, <, >=, <=}
---------------------------------------------------------------------------------
Γ ⊢ (e1 e2 oprel) : logico        somente em condição de se ou enquanto
```

## 7.5 Estruturas de Controle

```txt
Γ ⊢ cond : logico     Γ ⊢ acao : T
-----------------------------------
Γ ⊢ (cond acao se) : T ou NULL
```

```txt
Γ ⊢ cond : logico     Γ ⊢ acao : T
-----------------------------------
Γ ⊢ (cond acao enquanto) : T ou NULL
```

## 7.6 `RES`

```txt
N é literal inteiro     N ≥ 0     existe resultado anterior na posição N
----------------------------------------------------------------------------
Γ ⊢ (N RES) : tipo(resultado_referenciado)
```

Caso o resultado referenciado possa ser `NULL`, `RES` também pode resultar em `NULL`.

A documentação completa das regras semânticas também está disponível em:

```txt
docs/regras_tipos.md
```

---

# 8. Tabela de Símbolos

A tabela de símbolos é construída após a árvore sintática inicial e antes da verificação de tipos.

Ela registra:

| Campo                     | Significado                          |
| ------------------------- | ------------------------------------ |
| `identificador`           | Nome da variável.                    |
| `tipo`                    | Tipo da variável, sempre `real`.     |
| `linha_definicao`         | Primeira linha em que foi atribuída. |
| `linhas_atribuicao`       | Linhas de definição e reatribuição.  |
| `linha_ultima_atribuicao` | Última linha onde recebeu valor.     |
| `linhas_uso`              | Linhas onde foi consultada.          |
| `linha_ultimo_uso`        | Última linha onde foi consultada.    |

Exemplo para:

```txt
(START)
(1 A)
(2 A)
(A)
(END)
```

Resultado esperado:

```json
{
    "A": {
        "identificador": "A",
        "tipo": "real",
        "linha_definicao": 2,
        "linhas_atribuicao": [2, 3],
        "linha_ultima_atribuicao": 3,
        "linhas_uso": [4],
        "linha_ultimo_uso": 4
    }
}
```

A tabela também detecta:

```txt
uso antes da definição;
definição inicial dentro de se;
definição inicial dentro de enquanto;
atribuição proibida de resultado de expressão.
```

---

# 9. Árvore Sintática Atribuída

A árvore sintática atribuída é gerada somente após a ausência de erros semânticos.

Ela contém:

```txt
categoria de cada comando;
tipo resultante;
linha do código fonte;
informações da tabela de símbolos;
possibilidade de NULL;
referência utilizada por RES.
```

## 9.1 Exemplo de Atribuição

```json
{
    "categoria": "atribuicao_literal",
    "destino": "A",
    "valor": {
        "categoria": "literal",
        "valor": "1",
        "tipo": "inteiro"
    },
    "tipo_resultado": "real"
}
```

## 9.2 Exemplo de Decisão

```json
{
    "categoria": "decisao",
    "tipo_condicao": "logico",
    "tipo_resultado": "real",
    "pode_ser_null": true,
    "acao_pode_ser_null": false
}
```

## 9.3 Exemplo de Repetição

```json
{
    "categoria": "repeticao",
    "tipo_condicao": "logico",
    "tipo_resultado": "real",
    "pode_ser_null": true,
    "resultado_quando_executa": "resultado_da_ultima_execucao"
}
```

## 9.4 Exemplo de `RES`

```json
{
    "categoria": "res",
    "indice": 0,
    "tipo_resultado": "real",
    "pode_ser_null": true,
    "linha_resultado_referenciado": 4
}
```

---

# 10. Geração de Assembly

O Assembly é gerado somente para programas sem erros léxicos, sintáticos ou semânticos.

A implementação utiliza:

```txt
d0 -> valor do resultado atual
r7 -> flag de NULL
```

Convenção:

```txt
r7 = 0 -> existe valor válido em d0
r7 = 1 -> resultado é NULL
```

Os resultados dos comandos principais são armazenados em dois vetores:

```txt
resultados
resultados_null
```

Essa estratégia permite diferenciar:

```txt
resultado numérico igual a 0
resultado ausente representado por NULL
```

O comando `RES` recupera os dois valores: o valor produzido e a flag correspondente.

---

# 11. Exemplos de Programas

## 11.1 Programa Válido

```txt
(START)
(1 A)
(2 B)
(A B +)
((A B <) A se)
(0 RES)
(END)
```

Esse programa:

```txt
define A e B;
calcula A + B;
executa se com condição relacional válida;
recupera o resultado imediatamente anterior com RES.
```

## 11.2 Programa Inválido: Variável Não Declarada

```txt
(START)
(A B +)
(END)
```

Erro esperado:

```txt
variável A utilizada antes de sua definição;
variável B utilizada antes de sua definição.
```

## 11.3 Programa Inválido: Comparação Isolada

```txt
(START)
(2 3 <)
(END)
```

Erro esperado:

```txt
operador relacional só pode ser usado como condição direta de se ou enquanto.
```

## 11.4 Programa Inválido: `RES` Dentro de Expressão

```txt
(START)
(10 A)
((0 RES) 2 +)
(END)
```

Erro esperado:

```txt
RES só pode ser usado como comando isolado no formato (N RES).
```

---

# 12. Testes

A pasta `tests` contém arquivos separados para programas válidos e inválidos. Foram criados mais de três arquivos, todos planejados com pelo menos dez linhas, cobrindo erros léxicos, sintáticos e semânticos, comentários, tipos, aninhamento e estruturas de controle.

## 12.1 Tipos de Teste Implementados

| Arquivo                                       | Tipo de teste              | Elementos verificados                                                                               |
| --------------------------------------------- | -------------------------- | --------------------------------------------------------------------------------------------------- |
| `teste1.txt`                | Programa válido completo   | Comentários em posições diferentes, inteiro, real, potência, `se`, `enquanto`, aninhamento e `RES`. |
| `teste2.txt`         | Erro léxico                | Comentário aberto e não finalizado; mensagem sem traceback.                                         |
| `teste3.txt`                 | Erro sintático             | Estrutura inválida com tokens reconhecidos.                                                         |
| `teste4.txt` | Erros de declaração        | Variável não definida, definição dentro de controle e atribuição proibida.                          |
| `teste5.txt`           | Erros de tipo              | Divisão inteira com real, potência inválida, OPREL isolado, `NULL` e `RES` aninhado.                |
| `teste6.txt`                | Programa válido com `NULL` | `se` falso, `enquanto` sem execução e propagação de `NULL` por `RES`.                               |

## 12.2 Comandos para Executar os Testes

```bash
python src/main.py tests/teste_01_valido_completo.txt
python src/main.py tests/teste_02_erro_lexico_comentario.txt
python src/main.py tests/teste_03_erro_sintatico.txt
python src/main.py tests/teste_04_erro_semantico_tabela_simbolos.txt
python src/main.py tests/teste_05_erro_semantico_tipos.txt
python src/main.py tests/teste_06_valido_null_res.txt
```

## 12.3 Teste Válido Completo

Arquivo:

```txt
tests/teste_01_valido_completo.txt
```

Conteúdo sugerido:

```txt
(START)
*{ comentario em linha inteira antes das declaracoes }*
(1 A)
(2 B) *{ comentario ao final de um comando }*
(3 C)
(4 D)
(5 S)
(2.00 3 +)
(2.00 3.00 ^)
((A C <=) *{ comentario entre elementos }* ((A B <=) D se) se)
((A B <) (2 A) enquanto)
(0 RES)
(END)
```

Resultado esperado:

```txt
Análise semântica concluída com sucesso.
Árvore sintática atribuída gerada com sucesso.
Assembly gerado com sucesso.
```

## 12.4 Teste de Erro Léxico

Arquivo:

```txt
tests/teste_02_erro_lexico_comentario.txt
```

Conteúdo sugerido:

```txt
(START)
(1 A)
(2 B)
(3 C)
(4 D)
(5 E)
(A B +)
(2.00 3 +)
(2 0 ^)
(A)
*{ comentario iniciado e nao finalizado
(END)
```

Resultado esperado:

```txt
Erro léxico:
- Comentário iniciado na posição ... não foi fechado com }*.
```

O programa não deve exibir traceback nem gerar Assembly.

## 12.5 Teste de Erro Sintático

Arquivo:

```txt
tests/teste_03_erro_sintatico.txt
```

Conteúdo sugerido:

```txt
(START)
(1 A)
(2 B)
(3 C)
(4 D)
(5 E)
(A B +)
(A C *)
(2.00 3 +)
(A B + C)
(END)
```

O erro está no comando:

```txt
(A B + C)
```

Resultado esperado:

```txt
Programa rejeitado pela gramática.
Erro sintático: ...
```

## 12.6 Teste de Erros na Tabela de Símbolos

Arquivo:

```txt
tests/teste_04_erro_semantico_tabela_simbolos.txt
```

Conteúdo sugerido:

```txt
(START)
(1 A)
(2 B)
(3 D)
(4 E)
((A B <) (3 C) se)
((A B <) (4 F) enquanto)
(C)
(G B)
((A B +) A)
(END)
```

Esse teste deve detectar:

```txt
definição inicial de C dentro de se;
definição inicial de F dentro de enquanto;
uso de C antes de definição;
uso de G antes de definição;
atribuição proibida de resultado de expressão para A.
```

## 12.7 Teste de Erros de Tipo

Arquivo:

```txt
tests/teste_05_erro_semantico_tipos.txt
```

Conteúdo sugerido:

```txt
(START)
(1 A)
(2 B)
(3 C)
(4 D)
(A 2 /)
(2.00 3.50 ^)
(A B <)
(((A B <) A se) 2 +)
((A B <) (0 RES) se)
(END)
```

Esse teste deve detectar:

```txt
divisão inteira com operando real;
potenciação com expoente fracionário;
operador relacional isolado;
resultado possivelmente NULL utilizado em soma;
RES utilizado dentro de se.
```

## 12.8 Teste Válido de `NULL` e `RES`

Arquivo:

```txt
tests/teste_06_valido_null_res.txt
```

Conteúdo sugerido:

```txt
(START)
(2 A)
(1 B)
(3 C)
(4 D)
*{ o se abaixo possui condicao falsa e retorna NULL }*
((A B <) D se)
(0 RES)
*{ o enquanto abaixo nao executa e retorna NULL }*
((A B <) (1 A) enquanto)
(0 RES)
(A)
(END)
```

Resultado esperado:

```txt
Análise semântica concluída com sucesso.
Árvore sintática atribuída gerada com sucesso.
Assembly gerado com sucesso.
```

Durante a execução no CPUlator:

```txt
resultados_null[4] = 1
resultados_null[5] = 1
resultados_null[6] = 1
resultados_null[7] = 1
```

---

# 13. Tratamento de Erros

O compilador apresenta mensagens separadas para cada fase.

## 13.1 Erro Léxico

Exemplo:

```txt
Erro léxico:
- Comentário iniciado na posição ... não foi fechado com }*.
```

## 13.2 Erro Sintático

Exemplo:

```txt
Programa rejeitado pela gramática.
Erro sintático em comando: encontrado ...
```

## 13.3 Erro Semântico de Declaração

Exemplo:

```txt
Erro semântico na linha 4: variável A utilizada antes de sua definição.
```

## 13.4 Erro Semântico de Tipo

Exemplo:

```txt
Erro semântico na linha 2: o expoente de ^ deve ser um literal inteiro não negativo, mas recebeu 3.50.
```

Quando qualquer erro é detectado:

```txt
a geração da árvore atribuída é interrompida;
o código Assembly não é gerado;
arquivos antigos de execução são removidos no início da nova compilação.
```

---

# 14. Limitações da Implementação Atual

A linguagem implementada não permite atribuir diretamente o resultado de uma expressão para uma variável.

Assim, este formato é inválido:

```txt
((A 1 +) A)
```

Portanto, embora `enquanto` permita reatribuir uma variável já existente por literal ou por outra variável, a implementação atual não representa diretamente comandos equivalentes a:

```txt
A = A + 1
```

sem uma futura extensão da sintaxe e das regras semânticas.

---

# 15. Repositório e Entregáveis

Antes da entrega, o repositório deve conter:

```txt
README.md
docs/regras_tipos.md
src/
tests/
output/ com artefatos finais de uma execução válida
```

Os commits e pull requests devem identificar claramente:

```txt
implementação do lexer e comentários;
gramática LL(1), FIRST, FOLLOW e tabela;
parser e árvore sintática;
tabela de símbolos;
verificação de tipos;
árvore atribuída;
geração de Assembly;
testes e documentação.
```

# 16. Extensão: Comando Morse com Saída em LED

Foi adicionada uma extensão à linguagem para permitir que uma palavra ou frase seja convertida para código Morse e exibida por meio dos LEDs no CPUlator ARMv7 DE1-SoC.

O comando segue a mesma ideia pós-fixada da linguagem: primeiro vem o conteúdo, depois o comando.

```txt
([TEXTO] morse)
```

Exemplos:

```txt
(START)
([SOS] morse)
(END)
```

```txt
(START)
([João 123!] morse)
(END)
```

Nesse comando, o texto deve ficar entre colchetes `[ ]`, e o comando `morse` deve ser escrito em letras minúsculas.

---

## Tokens adicionados

Foram adicionados dois novos tokens ao analisador léxico:

| Token  | Significado                      | Exemplo                |
| ------ | -------------------------------- | ---------------------- |
| `PALA` | Palavra ou frase entre colchetes | `[SOS]`, `[João 123!]` |
| `MOR`  | Comando Morse                    | `morse`                |

Exemplo de entrada:

```txt
([SOS] morse)
```

Sequência de tokens gerada:

```txt
EPAR PALA MOR DPAR
```

Caso o texto seja iniciado com `[` e não seja fechado com `]`, ocorre erro léxico.

Exemplo inválido:

```txt
([SOS morse)
```

---

## Alteração na gramática

A gramática foi estendida para aceitar comandos Morse sem alterar a estrutura principal da linguagem.

Foram adicionadas as produções:

```ebnf
conteudo  = PALA, cont_pala ;
cont_pala = MOR ;
```

Com isso, o comando:

```txt
([SOS] morse)
```

é reconhecido como:

```txt
EPAR PALA MOR DPAR
```

A extensão mantém a linguagem em formato pós-fixado, pois o texto aparece antes do operador/comando `morse`.

---

## Arquivo `morse_utils.py`

Foi criado o arquivo `morse_utils.py`, responsável por centralizar as funções relacionadas ao código Morse.

Esse arquivo contém:

```txt
tabela de conversão Morse;
normalização de texto;
remoção de acentos;
remoção de cedilha;
validação de caracteres aceitos;
conversão de texto para sequências de ponto e traço.
```

A normalização permite que entradas com acento sejam aceitas.

Exemplos:

```txt
João  -> JOAO
ação  -> ACAO
Ç     -> C
```

Assim, o comando:

```txt
([João] morse)
```

é tratado internamente como:

```txt
JOAO
```

Espaços são preservados como espaços. Eles não são convertidos para `/`.

---

## Caracteres aceitos

O comando Morse aceita:

```txt
letras de A até Z;
números de 0 até 9;
espaços;
pontuações cadastradas na tabela Morse.
```

Foram incluídos símbolos como:

```txt
. , ? ' ! / ( ) & : ; = - _ " $ @
```

Caso algum caractere não possua conversão Morse cadastrada, ocorre erro semântico.

Exemplo inválido:

```txt
(START)
([TESTE#] morse)
(END)
```

Nesse caso, o caractere `#` não possui conversão Morse cadastrada.

---

## Alterações na análise semântica

O comando Morse não define variável e não utiliza variável `MEM`. Por isso, a tabela de símbolos apenas ignora comandos no formato:

```txt
(PALA MOR)
```

Exemplo:

```txt
([SOS] morse)
```

Esse comando não cria entrada na tabela de símbolos.

Na verificação de tipos, o comando Morse é validado como um comando especial. O verificador confere se todos os caracteres do texto possuem conversão Morse cadastrada.

Quando o comando é válido, ele é anotado com a categoria:

```txt
morse
```

---

## Árvore sintática atribuída

A árvore sintática atribuída recebeu uma nova categoria:

```json
{
    "categoria": "morse",
    "texto_original": "João 123!",
    "texto_normalizado": "JOAO 123!",
    "tipo_resultado": "comando"
}
```

Essa estrutura é utilizada pelo gerador de Assembly para produzir as chamadas das rotinas de ponto, traço e espaçamento.

---

## Geração de Assembly

O gerador de Assembly foi estendido para reconhecer nós da categoria:

```txt
morse
```

Para cada caractere do texto, o compilador consulta a tabela Morse e gera chamadas para as rotinas correspondentes.

Exemplo:

```txt
([SOS] morse)
```

Conversão:

```txt
S = ...
O = ---
S = ...
```

Chamadas geradas de forma simplificada:

```asm
bl morse_ponto
bl morse_gap_simbolo
bl morse_ponto
bl morse_gap_simbolo
bl morse_ponto
bl morse_gap_letra

bl morse_traco
bl morse_gap_simbolo
bl morse_traco
bl morse_gap_simbolo
bl morse_traco
bl morse_gap_letra

bl morse_ponto
bl morse_gap_simbolo
bl morse_ponto
bl morse_gap_simbolo
bl morse_ponto
```

Ao final da palavra ou frase, o código entra em loop e repete a saída Morse continuamente.

Por esse motivo, recomenda-se que o comando Morse seja o último comando antes do `(END)`.

Exemplo recomendado:

```txt
(START)
([Isa] morse)
(END)
```

---

## Device Map utilizado

A saída Morse utiliza os LEDs vermelhos da placa DE1-SoC no CPUlator ARMv7.

Endereço utilizado:

```asm
.equ LEDR_BASE, 0xFF200000
```

Esse endereço representa os LEDs vermelhos no Device Map da DE1-SoC.

Para controlar o tempo das piscadas, foi utilizado o timer:

```asm
.equ TIMER_BASE, 0xFF202000
```

O timer foi usado para gerar intervalos aproximados em milissegundos.

---

## Tempos definidos para o código Morse

Os tempos adotados foram:

| Parte do Morse         |   Tempo |
| ---------------------- | ------: |
| Ponto                  |  300 ms |
| Traço                  |  600 ms |
| Espaço dentro da letra |  450 ms |
| Espaço entre letras    |  900 ms |
| Espaço entre palavras  | 2000 ms |

A lógica usada foi:

```txt
ponto  = LED ligado por 300 ms
traço  = LED ligado por 600 ms

espaço dentro da letra = LED desligado por 450 ms
espaço entre letras    = LED desligado por 900 ms
espaço entre palavras  = LED desligado por 2000 ms
```

Exemplo para `SOS`:

```txt
S = ...
O = ---
S = ...
```

Execução esperada:

```txt
ponto, espaço interno, ponto, espaço interno, ponto
espaço entre letras
traço, espaço interno, traço, espaço interno, traço
espaço entre letras
ponto, espaço interno, ponto, espaço interno, ponto
espaço entre palavras
repete
```

---

## Arquivos alterados

| Arquivo                 | Alteração                                                   |
| ----------------------- | ----------------------------------------------------------- |
| `morse_utils.py`        | Novo arquivo com tabela Morse, normalização e validação.    |
| `lexer.py`              | Adicionados os tokens `PALA` e `MOR`.                       |
| `gramatica.py`          | Adicionada a produção `PALA MOR`.                           |
| `tabela_simbolos.py`    | Comando Morse é ignorado pela tabela, pois não usa `MEM`.   |
| `verificar_tipos.py`    | Valida caracteres aceitos no Morse.                         |
| `arvore_atribuida.py`   | Cria nós da categoria `morse`.                              |
| `assembly_generator.py` | Gera as chamadas Assembly para ponto, traço e espaçamentos. |
| `README.md`             | Documenta a nova funcionalidade.                            |

---

## Testes sugeridos

### Teste 1: letra com ponto

```txt
(START)
([E] morse)
(END)
```

Resultado esperado:

```txt
1 piscada curta em loop
```

### Teste 2: letra com traço

```txt
(START)
([T] morse)
(END)
```

Resultado esperado:

```txt
1 piscada longa em loop
```

### Teste 3: SOS

```txt
(START)
([SOS] morse)
(END)
```

Resultado esperado:

```txt
... --- ... em loop
```

### Teste 4: acentos

```txt
(START)
([Isa] morse)
(END)
```

Resultado esperado:

```txt
Isa em código Morse
```

### Teste 5: números e pontuação

```txt
(START)
([A 1!] morse)
(END)
```

Resultado esperado:

```txt
A, espaço, número 1 e exclamação em código Morse
```

### Teste 6: caractere inválido

```txt
(START)
([TESTE#] morse)
(END)
```

Resultado esperado:

```txt
Erro semântico informando que o caractere # não possui conversão Morse cadastrada.
```

---

## Limitação importante

Como o comando Morse entra em loop infinito para repetir a palavra ou frase, comandos escritos depois dele não serão executados.

Exemplo não recomendado:

```txt
(START)
([SOS] morse)
(1 A)
(END)
```

Nesse caso, o comando `(1 A)` não será executado, pois a execução ficará presa no loop do Morse.

O uso recomendado é deixar o Morse como último comando do programa:

```txt
(START)
([SOS] morse)
(END)
```


---

# 17. Conclusão

O projeto implementa as etapas principais de um compilador para uma linguagem pós-fixada:

```txt
análise léxica;
análise sintática LL(1);
construção da tabela de símbolos;
verificação semântica e inferência de tipos;
árvore sintática atribuída;
geração de Assembly ARMv7.
```

A implementação diferencia valores numéricos de `NULL`, restringe operadores relacionais às estruturas de controle, valida referências com `RES` e somente gera Assembly quando o programa é considerado semanticamente válido.
