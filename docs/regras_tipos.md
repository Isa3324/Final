# Sistema de Regras de Tipos e Regras Semânticas

## 1. Objetivo

Este documento descreve as regras semânticas utilizadas pela linguagem, incluindo os tipos existentes, a definição e o uso de variáveis, as restrições para estruturas de controle e as condições necessárias para que um programa seja considerado semanticamente válido.

A análise semântica é realizada após a análise sintática. Portanto, um comando pode estar sintaticamente correto e ainda assim ser rejeitado por utilizar tipos incompatíveis, variáveis não definidas ou construções proibidas pela linguagem.

---

## 2. Tipos da Linguagem

A linguagem utiliza os seguintes tipos semânticos:

| Tipo      | Descrição                                                                                     | Exemplos                                     |
| --------- | --------------------------------------------------------------------------------------------- | -------------------------------------------- |
| `inteiro` | Literal numérico escrito sem ponto decimal.                                                   | `0`, `2`, `15`                               |
| `real`    | Literal numérico escrito com ponto decimal ou qualquer variável armazenada em memória.        | `0.0`, `2.50`, `A`, `TOTAL`                  |
| `logico`  | Resultado interno de uma comparação relacional utilizada como condição de `se` ou `enquanto`. | Resultado de `(A B <)` dentro de um controle |
| `NULL`    | Ausência de resultado produzida por `se` ou `enquanto` quando nenhuma ação gera valor.        | `se` falso ou `enquanto` sem execução        |

O tipo `logico` não representa um resultado comum de linha. Ele existe apenas para validar condições de estruturas de controle.

---

## 3. Ambiente de Tipos e Tabela de Símbolos

Durante a análise semântica, utiliza-se um ambiente `Γ` contendo as variáveis já definidas no arquivo atual.

Cada arquivo representa um escopo independente. Portanto, uma variável definida em um arquivo não existe automaticamente em outro arquivo.

A tabela de símbolos registra, para cada variável:

| Informação                | Significado                                           |
| ------------------------- | ----------------------------------------------------- |
| `identificador`           | Nome da variável.                                     |
| `tipo`                    | Tipo armazenado pela variável, sempre `real`.         |
| `linha_definicao`         | Linha onde a variável foi definida pela primeira vez. |
| `linhas_atribuicao`       | Linhas onde a variável recebeu um valor.              |
| `linha_ultima_atribuicao` | Linha da atribuição mais recente.                     |
| `linhas_uso`              | Linhas em que a variável foi utilizada.               |
| `linha_ultimo_uso`        | Linha da utilização mais recente.                     |

Exemplo:

```json
{
    "A": {
        "identificador": "A",
        "tipo": "real",
        "linha_definicao": 2,
        "linhas_atribuicao": [2, 4],
        "linha_ultima_atribuicao": 4,
        "linhas_uso": [5],
        "linha_ultimo_uso": 5
    }
}
```

---

## 4. Literais Numéricos

Um literal escrito sem ponto decimal possui tipo `inteiro`.

```txt
Γ ⊢ 0 : inteiro
Γ ⊢ 2 : inteiro
Γ ⊢ 15 : inteiro
```

Um literal escrito com ponto decimal possui tipo `real`.

```txt
Γ ⊢ 0.0 : real
Γ ⊢ 2.00 : real
Γ ⊢ 15.75 : real
```

Formalmente:

```txt
n é literal escrito sem ponto decimal
--------------------------------------
Γ ⊢ n : inteiro
```

```txt
r é literal escrito com ponto decimal
--------------------------------------
Γ ⊢ r : real
```

---

## 5. Variáveis de Memória

Toda variável armazenada por `MEM` possui tipo `real`, independentemente do tipo do literal recebido na atribuição.

Assim:

```txt
(1 A)    -> A : real
(1.0 A)  -> A : real
(2.75 B) -> B : real
```

Formalmente:

```txt
Γ ⊢ n : inteiro ou real       X não definida anteriormente
-----------------------------------------------------------
Γ, X:real ⊢ (n X) : real
```

Uma variável só pode ser utilizada depois de ser definida.

```txt
Γ(X) = real
-----------
Γ ⊢ X : real
```

Exemplo válido:

```txt
(START)
(1 A)
(A)
(END)
```

Exemplo inválido:

```txt
(START)
(A)
(END)
```

Erro esperado:

```txt
Erro semântico: variável A utilizada antes de sua definição.
```

---

## 6. Atribuições Permitidas

A linguagem permite atribuição literal para uma variável:

```txt
(NUM MEM)
```

Exemplos:

```txt
(1 A)
(2.50 TOTAL)
(0 CONTADOR)
```

Também permite copiar o valor de uma variável previamente definida para outra variável:

```txt
(MEM MEM)
```

Exemplo válido:

```txt
(START)
(1 A)
(A B)
(B)
(END)
```

Nesse exemplo:

```txt
A : real
B : real
```

Formalmente:

```txt
Γ(A) = real
------------------------
Γ, B:real ⊢ (A B) : real
```

Caso a variável de origem ainda não esteja definida, a atribuição é inválida:

```txt
(START)
(A B)
(END)
```

Erro esperado:

```txt
Erro semântico: variável A utilizada antes de sua definição.
```

---

## 7. Definição e Reatribuição em `se` e `enquanto`

Uma variável nova não pode ser definida pela primeira vez dentro de uma estrutura `se` ou `enquanto`, pois a ação pode não ser executada.

Exemplo inválido:

```txt
(START)
(1 A)
(2 B)
((A B <) (3 C) se)
(C)
(END)
```

A variável `C` não pode ser considerada definida, pois a condição do `se` pode ser falsa.

Erro esperado:

```txt
Erro semântico: a variável C não pode ser definida pela primeira vez dentro de se.
Erro semântico: variável C utilizada antes de sua definição.
```

Entretanto, uma variável que já tenha sido definida antes da estrutura de controle pode ser reatribuída dentro dela.

Exemplo válido:

```txt
(START)
(1 A)
(2 B)
(0 C)
((A B <) (3 C) se)
(C)
(END)
```

Nesse exemplo, `C` já existia antes do `se`. Portanto, `(3 C)` representa apenas uma reatribuição.

A mesma regra vale para `enquanto`.

Exemplo válido:

```txt
(START)
(1 A)
(2 B)
((A B <) (2 A) enquanto)
(END)
```

A variável `A` já foi definida antes do laço e pode ser atualizada durante sua execução.

---

## 8. Atribuições Proibidas

A linguagem não permite atribuir diretamente o resultado de uma expressão para uma variável.

São inválidos:

```txt
((3 4 +) A)
((A B +) A)
((3 4 <=) A)
```

Mesmo que `A` já tenha sido definida anteriormente, o formato:

```txt
(expressao MEM)
```

não representa uma atribuição permitida nesta linguagem.

As únicas formas aceitas de atribuição são:

```txt
(NUM MEM)
(MEM MEM)
```
## 9. Operações Aritméticas

A linguagem possui os seguintes operadores aritméticos:

| Operador | Significado | Exemplo |
| --- | --- | --- |
| `+` | Adição | `(A B +)` |
| `-` | Subtração | `(A B -)` |
| `*` | Multiplicação | `(A B *)` |
| `\|` | Divisão real | `(A B \|)` |
| `/` | Divisão inteira | `(A B /)` |
| `//` | Divisão inteira alternativa | `(A B //)` |
| `%` | Resto da divisão inteira | `(A B %)` |
| `^` | Potenciação | `(A B ^)` |
As operações seguem o formato pós-fixado:

```txt
(operando_esquerdo operando_direito operador)
```

---

### 9.1 Adição, Subtração e Multiplicação

Os operadores `+`, `-` e `*` aceitam operandos numéricos dos tipos `inteiro` e `real`.

São válidas todas as combinações:

```txt
inteiro com inteiro
inteiro com real
real com inteiro
real com real
```

Quando ambos os operandos forem `inteiro`, o resultado será `inteiro`.

Quando pelo menos um dos operandos for `real`, o resultado será `real`.

| Expressão    | Tipo do resultado |
| ------------ | ----------------- |
| `(2 3 +)`    | `inteiro`         |
| `(2 3 -)`    | `inteiro`         |
| `(2 3 *)`    | `inteiro`         |
| `(2.00 3 +)` | `real`            |
| `(2.00 3 -)` | `real`            |
| `(2.00 3 *)` | `real`            |
| `(2 3.50 +)` | `real`            |

Formalmente, para `op ∈ {+, -, *}`:

```txt
Γ ⊢ e1 : inteiro     Γ ⊢ e2 : inteiro
---------------------------------------
Γ ⊢ (e1 e2 op) : inteiro
```

```txt
Γ ⊢ e1 : real        Γ ⊢ e2 : numérico
---------------------------------------
Γ ⊢ (e1 e2 op) : real
```

```txt
Γ ⊢ e1 : numérico    Γ ⊢ e2 : real
---------------------------------------
Γ ⊢ (e1 e2 op) : real
```

Onde:

```txt
numérico = inteiro ou real
```

Exemplo válido:

```txt
(START)
(2.00 3 +)
(2.00 3 -)
(2.00 3 *)
(END)
```

---

### 9.2 Divisão Real

O operador `|` representa divisão real.

Ele aceita operandos numéricos dos tipos `inteiro` ou `real`, em qualquer combinação, e sempre produz resultado do tipo `real`.

| Expressão | Tipo do resultado |
| --- | --- |
| `(4 2 \|)` | `real` |
| `(4.00 2 \|)` | `real` |
| `(4 2.00 \|)` | `real` |
| `(4.00 2.00 \|)` | `real` |

Formalmente:

```txt
Γ ⊢ e1 : numérico    Γ ⊢ e2 : numérico
---------------------------------------
Γ ⊢ (e1 e2 |) : real
```

Exemplo válido:

```txt
(START)
(4.00 2 |)
(END)
```

A divisão por zero não produz um resultado válido. Caso o divisor seja zero durante a execução, o código Assembly deve interromper a operação em uma rotina de erro.

---

### 9.3 Divisão Inteira e Resto

Os operadores `/` e `//` representam divisão inteira.  
O operador `%` representa o resto da divisão inteira.

Todos exigem dois operandos do tipo `inteiro`.

```txt
/  -> divisão inteira
// -> divisão inteira
%  -> resto da divisão inteira

Assim, ambos os operandos devem ser literais ou resultados do tipo `inteiro`.

| Expressão    | Situação | Tipo do resultado |
| ------------ | -------- | ----------------- |
| `(4 2 /)`    | Válida   | `inteiro`         |
| `(5 2 %)`    | Válida   | `inteiro`         |
| `(4.00 2 /)` | Inválida | —                 |
| `(5 2.00 %)` | Inválida | —                 |

Como toda variável `MEM` possui tipo `real`, uma variável não pode ser utilizada diretamente em divisão inteira ou resto, mesmo que tenha recebido um literal escrito sem casas decimais.

Exemplo inválido:

```txt
(START)
(4 A)
(A 2 /)
(END)
```

Embora a atribuição tenha utilizado o literal `4`, a variável `A` possui tipo `real`. Portanto, ela não atende à regra da divisão inteira.

Formalmente:

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

```txt
Γ ⊢ e1 : inteiro     Γ ⊢ e2 : inteiro
---------------------------------------
Γ ⊢ (e1 e2 //) : inteiro
```

Quando algum operando não for `inteiro`, ocorre erro semântico.

---

## 10. Potenciação

O operador `^` representa potenciação:

```txt
(base expoente ^)
```

A base pode possuir tipo `inteiro` ou `real`.

O expoente deve ser um literal numérico que represente um valor inteiro não negativo. Portanto, números escritos com casas decimais iguais a zero também são aceitos como expoentes.

São exemplos válidos:

```txt
(2 3 ^)
(2.00 3 ^)
(2 0 ^)
(2.00 0.00 ^)
(2.00 3.00 ^)
```

São exemplos inválidos:

```txt
(2.00 3.50 ^)
(2 A ^)
```

No primeiro caso, `3.50` não representa um número inteiro.

No segundo caso, mesmo que `A` possua algum valor numérico durante a execução, o expoente não é um literal diretamente verificável pela análise semântica.

---

### 10.1 Expoente Inteiro Não Negativo

A função semântica considera válidos:

| Expoente | Válido? | Motivo                                     |
| -------- | ------: | ------------------------------------------ |
| `0`      |     Sim | Inteiro não negativo                       |
| `0.00`   |     Sim | Representa o inteiro zero                  |
| `3`      |     Sim | Inteiro positivo                           |
| `3.00`   |     Sim | Representa o inteiro três                  |
| `3.50`   |     Não | Possui parte fracionária diferente de zero |

Exemplos:

```txt
(2 0 ^)       -> válido, resultado correspondente a 2 elevado a 0
(2.00 3.00 ^) -> válido, pois 3.00 representa o inteiro 3
(2.00 3.50 ^) -> erro semântico
```

---

### 10.2 Tipo Resultante da Potenciação

A potenciação segue a promoção numérica adotada para as operações aritméticas.

Quando a base e o expoente forem escritos como `inteiro`, o resultado será `inteiro`.

Quando a base ou o expoente forem escritos como `real`, mesmo que o expoente represente um inteiro, o resultado será `real`.

| Expressão       | Tipo do resultado |
| --------------- | ----------------- |
| `(2 3 ^)`       | `inteiro`         |
| `(2 0 ^)`       | `inteiro`         |
| `(2.00 3 ^)`    | `real`            |
| `(2 3.00 ^)`    | `real`            |
| `(2.00 3.00 ^)` | `real`            |

Formalmente:

```txt
Γ ⊢ base : numérico
expoente é literal numérico
valor(expoente) ∈ ℤ
valor(expoente) ≥ 0
-------------------------------------------------
Γ ⊢ (base expoente ^) : promoção(base, expoente)
```

Onde:

```txt
promoção(inteiro, inteiro) = inteiro
promoção(real, inteiro)    = real
promoção(inteiro, real)    = real
promoção(real, real)       = real
```

---

### 10.3 Exemplos de Validação

Exemplo válido:

```txt
(START)
(2.00 3.00 ^)
(END)
```

O expoente `3.00` representa um inteiro não negativo. Portanto, a expressão é aceita e possui tipo `real`.

Exemplo inválido:

```txt
(START)
(2.00 3.50 ^)
(END)
```

Erro esperado:

```txt
Erro semântico: o expoente de ^ deve ser um literal inteiro não negativo, mas recebeu 3.50.
```

Exemplo inválido com variável como expoente:

```txt
(START)
(3 A)
(2 A ^)
(END)
```

Erro esperado:

```txt
Erro semântico: o expoente de ^ deve ser um literal inteiro não negativo, como 0, 3 ou 3.00.
```
## 11. Operadores Relacionais

A linguagem possui os seguintes operadores relacionais:

| Operador | Significado      | Exemplo em condição |
| -------- | ---------------- | ------------------- |
| `==`     | Igual a          | `((A B ==) A se)`   |
| `!=`     | Diferente de     | `((A B !=) A se)`   |
| `>`      | Maior que        | `((A B >) A se)`    |
| `<`      | Menor que        | `((A B <) A se)`    |
| `>=`     | Maior ou igual a | `((A B >=) A se)`   |
| `<=`     | Menor ou igual a | `((A B <=) A se)`   |

Os operadores relacionais comparam dois operandos numéricos:

```txt
(operando_esquerdo operando_direito OPREL)
```

São aceitas comparações entre:

```txt
inteiro e inteiro
inteiro e real
real e inteiro
real e real
```

Exemplos de condições numericamente válidas:

```txt
(2 3 <)
(2.00 3 <=)
(2 3.00 !=)
(A B >=)
```

Entretanto, uma comparação relacional **não pode aparecer como comando principal isolado**. Ela somente pode ser utilizada como condição direta de uma estrutura `se` ou `enquanto`.

Assim, este programa é inválido:

```txt
(START)
(2 3 <)
(END)
```

Erro esperado:

```txt
Erro semântico: o operador relacional < só pode ser usado como condição direta de se ou enquanto.
```

Já este programa é válido:

```txt
(START)
(1 A)
(2 B)
((A B <) A se)
(END)
```

---

### 11.1 Tipo `logico`

O tipo `logico` existe apenas durante a validação das condições de controle.

Uma comparação utilizada corretamente em uma condição produz internamente:

```txt
logico
```

Porém, esse resultado não pode ser tratado como um resultado comum de linha, não pode ser recuperado por `RES` diretamente e não pode ser utilizado em uma operação aritmética.

Formalmente:

```txt
Γ ⊢ e1 : numérico     Γ ⊢ e2 : numérico     oprel ∈ {==, !=, >, <, >=, <=}
---------------------------------------------------------------------------------
Γ ⊢ (e1 e2 oprel) : logico        somente em condição de se ou enquanto
```

Exemplo inválido:

```txt
(START)
((2 3 <) 4 +)
(END)
```

A comparação `(2 3 <)` produziria um valor `logico`, mas esse valor não pode ser utilizado como operando de uma soma.

---

## 12. Estrutura de Decisão `se`

A estrutura de decisão segue o formato pós-fixado:

```txt
(condicao acao se)
```

A condição deve ser obrigatoriamente uma comparação relacional direta e válida.

Exemplo:

```txt
((A B <) A se)
```

Nesse comando:

```txt
(A B <) -> condição
A       -> ação
se      -> comando de decisão
```

A execução segue a regra:

```txt
se a condição for verdadeira:
    o resultado do comando é o resultado da ação

se a condição for falsa:
    o resultado do comando é NULL
```

Exemplo válido:

```txt
(START)
(1 A)
(2 B)
((A B <) A se)
(END)
```

Como `A < B` é verdadeiro durante a execução, a ação `A` poderá produzir o valor armazenado em `A`.

A análise semântica, entretanto, não executa a condição. Por isso, todo comando `se` é marcado como podendo retornar `NULL`.

---

### 12.1 Regra Formal de `se`

```txt
Γ ⊢ cond : logico     Γ ⊢ acao : T
-----------------------------------
Γ ⊢ (cond acao se) : T ou NULL
```

O tipo principal do resultado é o tipo da ação. A possibilidade de `NULL` é registrada separadamente.

Exemplo:

```txt
((A B <) A se)
```

Se:

```txt
Γ(A) = real
Γ(B) = real
```

então:

```txt
Γ ⊢ (A B <) : logico
Γ ⊢ A : real
Γ ⊢ ((A B <) A se) : real ou NULL
```

---

### 12.2 `se` Aninhado

Uma ação de `se` pode ser outro comando `se`.

Exemplo válido:

```txt
(START)
(1 A)
(2 B)
(3 C)
(4 D)
((A B >=) ((A C <=) D se) se)
(END)
```

A interpretação é:

```txt
se A >= B:
    se A <= C:
        retorna D
    senão:
        retorna NULL
senão:
    retorna NULL
```

Nesse caso, o `se` externo pode retornar `NULL` por dois motivos:

```txt
a condição externa é falsa
ou
a ação interna retorna NULL
```

Na árvore sintática atribuída, essa informação é registrada por:

```json
{
    "categoria": "decisao",
    "tipo_resultado": "real",
    "pode_ser_null": true,
    "acao_pode_ser_null": true
}
```

---

## 13. Estrutura de Repetição `enquanto`

A estrutura de repetição segue o formato pós-fixado:

```txt
(condicao acao enquanto)
```

A condição deve ser obrigatoriamente uma comparação relacional direta e válida.

Exemplo:

```txt
((A B <) (2 A) enquanto)
```

A execução segue a regra:

```txt
enquanto a condição for verdadeira:
    executa a ação

se executar ao menos uma vez:
    o resultado do comando é o resultado da última execução da ação

se não executar nenhuma vez:
    o resultado do comando é NULL
```

Exemplo válido:

```txt
(START)
(1 A)
(2 B)
((A B <) (2 A) enquanto)
(END)
```

Nesse exemplo, `A` já foi definida antes do laço. Portanto, `(2 A)` representa uma reatribuição permitida dentro de `enquanto`.

---

### 13.1 Regra Formal de `enquanto`

```txt
Γ ⊢ cond : logico     Γ ⊢ acao : T
-----------------------------------
Γ ⊢ (cond acao enquanto) : T ou NULL
```

O tipo principal do resultado é o tipo da ação. A possibilidade de `NULL` é registrada separadamente, pois o corpo pode não executar nenhuma vez.

---

### 13.2 `enquanto` com Ação Aninhada

Uma ação de `enquanto` pode ser uma estrutura de controle aninhada.

Exemplo válido quanto à análise semântica:

```txt
(START)
(1 A)
(2 B)
(3 C)
(4 D)
(5 S)
((D S <=) ((A B >=) ((A C <=) D se) se) enquanto)
(END)
```

A interpretação é:

```txt
enquanto D <= S:
    se A >= B:
        se A <= C:
            retorna D
        senão:
            retorna NULL
    senão:
        retorna NULL
```

Nesse caso, o `enquanto` pode retornar `NULL` porque:

```txt
o laço pode não executar nenhuma vez
ou
a ação executada pode retornar NULL
```

Na árvore sintática atribuída, a informação pode ser registrada como:

```json
{
    "categoria": "repeticao",
    "tipo_resultado": "real",
    "pode_ser_null": true,
    "acao_pode_ser_null": true
}
```

---

## 14. Valor Especial `NULL`

`NULL` representa a ausência de resultado produzido por uma estrutura de controle.

Ele não representa o número zero.

Assim:

```txt
0    -> valor numérico válido
NULL -> ausência de valor
```

Exemplo com resultado numérico zero:

```txt
(START)
(0 A)
(END)
```

Nesse caso, a linha produz um valor válido, ainda que esse valor seja `0`.

Exemplo com `NULL`:

```txt
(START)
(2 A)
(1 B)
((A B <) A se)
(END)
```

Como `2 < 1` é falso durante a execução, a ação não é realizada e o comando `se` produz `NULL`.

---

### 14.1 Restrições para `NULL`

Um resultado que pode ser `NULL` não pode ser utilizado como operando de:

```txt
operação aritmética
operação relacional
```

Exemplo inválido:

```txt
(START)
(1 A)
(2 B)
(((A B <) A se) 2 +)
(END)
```

O resultado de:

```txt
((A B <) A se)
```

pode ser `NULL`. Portanto, ele não pode participar da soma.

Erro esperado:

```txt
Erro semântico: o operador + não pode utilizar um resultado que pode ser NULL.
```

Também é inválido utilizar um possível `NULL` em nova comparação:

```txt
(START)
(1 A)
(2 B)
((((A B <) A se) B <) A se)
(END)
```

Erro esperado:

```txt
Erro semântico: o operador relacional < não pode utilizar um resultado que pode ser NULL.
```

---

### 14.2 Propagação de `NULL`

Quando uma estrutura de controle é utilizada como ação de outra estrutura de controle, `NULL` pode ser propagado.

Exemplo:

```txt
((A B >=) ((A C <=) D se) se)
```

Se o `se` externo executar sua ação, mas o `se` interno produzir `NULL`, então o resultado final do `se` externo também será `NULL`.

Formalmente:

```txt
Γ ⊢ cond : logico     Γ ⊢ acao : T ou NULL
-------------------------------------------
Γ ⊢ (cond acao se) : T ou NULL
```

```txt
Γ ⊢ cond : logico     Γ ⊢ acao : T ou NULL
-------------------------------------------
Γ ⊢ (cond acao enquanto) : T ou NULL
```

---

### 14.3 Representação de `NULL` no Assembly

Como `0.0` é um valor numérico válido, `NULL` não pode ser representado somente pelo valor zero.

Durante a geração de Assembly, cada resultado possui:

```txt
um espaço para o valor produzido
uma flag indicando se o resultado é NULL
```

A convenção utilizada é:

```txt
resultados[i]      -> valor numérico produzido
resultados_null[i] -> 0 quando existe valor
resultados_null[i] -> 1 quando o resultado é NULL
```

Durante a avaliação de uma expressão:

```txt
d0 -> valor numérico resultante
r7 -> flag de NULL

r7 = 0 -> d0 contém valor válido
r7 = 1 -> o resultado é NULL
```

Assim, é possível diferenciar corretamente:

```txt
resultado numérico 0.0
resultado NULL
```
## 15. Comando Especial `RES`

O comando `RES` recupera o resultado produzido por um comando principal anterior.

Sua forma sintática válida é:

```txt
(N RES)
```

onde `N` é um literal inteiro não negativo utilizado como índice de busca nos resultados anteriores.

A contagem começa em zero:

| Comando   | Resultado recuperado                        |
| --------- | ------------------------------------------- |
| `(0 RES)` | Resultado do comando imediatamente anterior |
| `(1 RES)` | Resultado do segundo comando anterior       |
| `(2 RES)` | Resultado do terceiro comando anterior      |

O comando `RES` nunca referencia a própria linha, pois consulta somente resultados já produzidos anteriormente.

---

### 15.1 Índice de `RES`

O índice de `RES` deve ser escrito como um literal inteiro não negativo.

São válidos:

```txt
(0 RES)
(1 RES)
(2 RES)
```

São inválidos:

```txt
(0.00 RES)
(1.00 RES)
(2.50 RES)
```

Embora `0.00` e `1.00` representem valores numericamente inteiros em operações como potenciação, `RES` utiliza um índice de posição. Portanto, o índice deve ser escrito diretamente como `inteiro`, sem ponto decimal.

Formalmente:

```txt
N é literal inteiro     N ≥ 0     existe o resultado anterior na posição N
----------------------------------------------------------------------------
Γ ⊢ (N RES) : tipo(resultado_referenciado)
```

---

### 15.2 Contagem das Posições Anteriores

A posição utilizada por `RES` considera apenas os resultados dos comandos principais que já foram processados antes do próprio `RES`.

Exemplo:

```txt
(START)
(10 A)
(20 B)
(0 RES)
(END)
```

Os resultados anteriores ao `RES` são:

| Posição anterior | Comando referenciado | Resultado |
| ---------------: | -------------------- | --------: |
|              `0` | `(20 B)`             |      `20` |
|              `1` | `(10 A)`             |      `10` |

Assim:

```txt
(0 RES) -> recupera o resultado de (20 B)
```

Outro exemplo:

```txt
(START)
(10 A)
(20 B)
(1 RES)
(END)
```

Nesse caso:

```txt
(1 RES) -> recupera o resultado de (10 A)
```

---

### 15.3 Posição Inexistente

Caso `RES` solicite uma posição anterior que ainda não exista, ocorre erro semântico.

Exemplo inválido:

```txt
(START)
(10 A)
(1 RES)
(END)
```

Antes de `(1 RES)`, existe somente um resultado anterior:

```txt
posição 0 -> resultado de (10 A)
```

A posição `1` ainda não existe.

Erro esperado:

```txt
Erro semântico: RES solicitou a posição anterior 1, mas existe apenas 1 resultado anterior disponível.
```

Também é inválido utilizar `RES` quando nenhum resultado anterior existe:

```txt
(START)
(0 RES)
(END)
```

Erro esperado:

```txt
Erro semântico: RES solicitou a posição anterior 0, mas não existe resultado anterior disponível.
```

---

### 15.4 Tipo Retornado por `RES`

O comando `RES` não possui um tipo fixo próprio. Ele retorna exatamente o tipo do resultado referenciado.

Exemplo com resultado `inteiro`:

```txt
(START)
(2 3 +)
(0 RES)
(END)
```

Como:

```txt
(2 3 +) -> inteiro
```

então:

```txt
(0 RES) -> inteiro
```

Exemplo com resultado `real`:

```txt
(START)
(2.00 3 +)
(0 RES)
(END)
```

Como:

```txt
(2.00 3 +) -> real
```

então:

```txt
(0 RES) -> real
```

Formalmente:

```txt
resultado_anterior[N] : T
----------------------------
Γ ⊢ (N RES) : T
```

---

### 15.5 `RES` e `NULL`

Caso o resultado referenciado seja `NULL`, o próprio comando `RES` também retorna `NULL`.

Exemplo:

```txt
(START)
(2 A)
(1 B)
((A B <) A se)
(0 RES)
(END)
```

Durante a execução:

```txt
A < B
2 < 1 -> falso
```

Portanto:

```txt
((A B <) A se) -> NULL
(0 RES)         -> NULL
```

Nesse caso, `RES` não converte `NULL` em `0` e não cria um valor substituto. Ele propaga exatamente a ausência de resultado da estrutura referenciada.

Formalmente:

```txt
resultado_anterior[N] : NULL
----------------------------
Γ ⊢ (N RES) : NULL
```

Na árvore sintática atribuída, essa possibilidade é registrada por:

```json
{
    "categoria": "res",
    "indice": 0,
    "tipo_resultado": "real",
    "pode_ser_null": true
}
```

O campo `tipo_resultado` informa o tipo que existiria caso a estrutura referenciada produzisse valor; o campo `pode_ser_null` informa que, em execução, esse valor pode não existir.

---

### 15.6 `RES` Somente Como Comando Isolado

O comando `RES` somente pode aparecer diretamente como um comando principal do programa:

```txt
(N RES)
```

Exemplo válido:

```txt
(START)
(10 A)
(0 RES)
(END)
```

Não é permitido utilizar `RES` como parte de outra expressão, como operando, condição ou ação de uma estrutura de controle.

São inválidos:

```txt
((0 RES) 2 +)
((0 RES) A se)
((A B <) (0 RES) se)
((A B <) (0 RES) enquanto)
```

Erro esperado:

```txt
Erro semântico: RES só pode ser usado como comando isolado no formato (N RES).
```

Essa restrição impede que resultados eventualmente `NULL` recuperados por `RES` sejam utilizados de maneira indevida dentro de outras expressões.

---

### 15.7 Representação de `RES` no Assembly

O código Assembly mantém dois vetores paralelos:

```txt
resultados      -> valores produzidos pelos comandos principais
resultados_null -> flags que indicam ausência de resultado
```

Para cada resultado:

```txt
resultados_null[i] = 0 -> existe um valor válido em resultados[i]
resultados_null[i] = 1 -> o resultado é NULL
```

Ao gerar Assembly para:

```txt
(0 RES)
```

o compilador calcula a posição do comando imediatamente anterior e carrega:

```txt
o valor armazenado em resultados
a flag correspondente em resultados_null
```

Assim, o comportamento de `RES` preserva corretamente a diferença entre:

```txt
resultado igual a 0
resultado igual a NULL
```
## 16. Fluxo da Análise Semântica

A análise semântica ocorre somente após o programa ter sido aceito pelo analisador léxico e pelo analisador sintático.

O fluxo da compilação é:

```txt
arquivo fonte
    ↓
remoção de comentários e geração de tokens
    ↓
análise sintática LL(1)
    ↓
árvore sintática inicial
    ↓
construção da tabela de símbolos
    ↓
verificação de tipos e regras semânticas
    ↓
árvore sintática atribuída
    ↓
geração de Assembly
```

O Assembly somente é gerado quando não existirem erros:

```txt
léxicos
sintáticos
semânticos
```

---

### 16.1 Construção da Tabela de Símbolos

A primeira etapa semântica registra as variáveis utilizadas no programa.

Ela verifica:

```txt
se a variável foi definida antes do uso;
se a atribuição utiliza um formato permitido;
se uma variável nova está sendo criada dentro de se ou enquanto;
se uma variável já existente está sendo apenas reatribuída.
```

Exemplo:

```txt
(START)
(1 A)
(2 B)
(A B +)
(END)
```

Tabela de símbolos esperada:

```json
{
    "A": {
        "tipo": "real",
        "linha_definicao": 2,
        "linhas_atribuicao": [2],
        "linhas_uso": [4]
    },
    "B": {
        "tipo": "real",
        "linha_definicao": 3,
        "linhas_atribuicao": [3],
        "linhas_uso": [4]
    }
}
```

---

### 16.2 Verificação de Tipos

Após a tabela de símbolos, o analisador verifica os tipos produzidos por cada comando.

Essa etapa verifica:

```txt
compatibilidade entre inteiro e real;
restrições de / e %;
restrições de ^;
uso de OPREL somente em condição direta;
validação de se e enquanto;
validação de RES;
restrições de NULL.
```

Exemplo:

```txt
(START)
(2.00 3 +)
(END)
```

Resultado inferido:

```txt
real
```

Exemplo:

```txt
(START)
(2 3 +)
(END)
```

Resultado inferido:

```txt
inteiro
```

---

### 16.3 Árvore Sintática Atribuída

Depois da validação, a árvore sintática inicial é transformada em uma árvore atribuída.

Cada comando recebe informações como:

```txt
categoria semântica
tipo do resultado
possibilidade de NULL
variável utilizada ou modificada
linha do código fonte
```

Exemplo de nó de decisão:

```json
{
    "categoria": "decisao",
    "tipo_resultado": "real",
    "pode_ser_null": true,
    "acao_pode_ser_null": false
}
```

Exemplo de nó `RES`:

```json
{
    "categoria": "res",
    "indice": 0,
    "tipo_resultado": "real",
    "pode_ser_null": true
}
```

---

### 16.4 Geração de Assembly

O código Assembly é produzido somente a partir da árvore sintática atribuída.

O gerador não calcula o resultado das expressões em Python. Ele apenas produz as instruções necessárias para que o programa seja executado posteriormente.

A geração utiliza a convenção:

```txt
d0 -> valor produzido pelo comando atual
r7 -> flag de NULL

r7 = 0 -> existe valor válido em d0
r7 = 1 -> resultado é NULL
```

Os resultados dos comandos principais são armazenados em:

```txt
resultados
resultados_null
```

Assim, o comando `RES` consegue recuperar tanto o valor quanto a informação de ausência de resultado.

---

## 17. Casos de Teste Semântico

Os testes a seguir devem ser utilizados para verificar as regras da linguagem.

---

### 17.1 Programa Válido: Atribuição e Operação Numérica

```txt
(START)
(1 A)
(2 B)
(A B +)
(END)
```

Resultado esperado:

```txt
programa semanticamente válido
A : real
B : real
(A B +) : real
Assembly gerado
```

A soma produz `real`, pois `A` e `B` são variáveis armazenadas em memória e toda variável `MEM` possui tipo `real`.

---

### 17.2 Programa Válido: Operação entre Real e Inteiro

```txt
(START)
(2.00 3 +)
(2.00 3 -)
(2.00 3 *)
(4.00 2 |)
(END)
```

Resultado esperado:

```txt
programa semanticamente válido
todas as operações produzem real
Assembly gerado
```

---

### 17.3 Programa Válido: Potenciação

```txt
(START)
(2 0 ^)
(2.00 0.00 ^)
(2.00 3.00 ^)
(END)
```

Resultado esperado:

```txt
programa semanticamente válido
Assembly gerado
```

Os expoentes `0`, `0.00` e `3.00` são aceitos porque representam inteiros não negativos.

---

### 17.4 Programa Válido: Decisão

```txt
(START)
(1 A)
(2 B)
((A B <) A se)
(0 RES)
(END)
```

Resultado esperado:

```txt
programa semanticamente válido
(A B <) utilizado somente como condição de se
se : real ou NULL
RES recupera exatamente o resultado do se
Assembly gerado
```

---

### 17.5 Programa Válido: Decisão Aninhada

```txt
(START)
(1 A)
(2 B)
(3 C)
(4 D)
((A B >=) ((A C <=) D se) se)
(END)
```

Resultado esperado:

```txt
programa semanticamente válido
se interno : real ou NULL
se externo : real ou NULL
Assembly gerado
```

---

### 17.6 Programa Válido: Reatribuição Dentro de `enquanto`

```txt
(START)
(1 A)
(2 B)
((A B <) (2 A) enquanto)
(0 RES)
(END)
```

Resultado esperado:

```txt
programa semanticamente válido
A pode ser reatribuída, pois foi definida antes do laço
enquanto : real ou NULL
RES recupera o resultado do enquanto
Assembly gerado
```

Durante a execução, o laço executa uma vez:

```txt
A = 1
B = 2
A < B -> verdadeiro
A recebe 2
A < B -> falso
```

Logo, o resultado final do `enquanto` é `2`, e não `NULL`.

---

## 18. Casos de Teste com Erro

### 18.1 Erro: Variável Usada Antes da Definição

```txt
(START)
(A B +)
(END)
```

Resultado esperado:

```txt
Erro semântico: variável A utilizada antes de sua definição.
Erro semântico: variável B utilizada antes de sua definição.
Assembly não gerado.
```

---

### 18.2 Erro: Definição Inicial Dentro de `se`

```txt
(START)
(1 A)
(2 B)
((A B <) (3 C) se)
(C)
(END)
```

Resultado esperado:

```txt
Erro semântico: a variável C não pode ser definida pela primeira vez dentro de se.
Erro semântico: variável C utilizada antes de sua definição.
Assembly não gerado.
```

---

### 18.3 Erro: Definição Inicial Dentro de `enquanto`

```txt
(START)
(1 A)
(2 B)
((A B <) (3 C) enquanto)
(C)
(END)
```

Resultado esperado:

```txt
Erro semântico: a variável C não pode ser definida pela primeira vez dentro de enquanto.
Erro semântico: variável C utilizada antes de sua definição.
Assembly não gerado.
```

---

### 18.4 Erro: Atribuição de Resultado de Expressão

```txt
(START)
(1 A)
((A 2 +) A)
(END)
```

Resultado esperado:

```txt
Erro semântico: não é permitido atribuir o resultado de uma expressão à variável A.
Assembly não gerado.
```

As formas permitidas de atribuição continuam sendo somente:

```txt
(NUM MEM)
(MEM MEM)
```

---

### 18.5 Erro: Operador Relacional Isolado

```txt
(START)
(2 3 <)
(END)
```

Resultado esperado:

```txt
Erro semântico: o operador relacional < só pode ser usado como condição direta de se ou enquanto.
Assembly não gerado.
```

---

### 18.6 Erro: Potenciação com Expoente Fracionário

```txt
(START)
(2.00 3.50 ^)
(END)
```

Resultado esperado:

```txt
Erro semântico: o expoente de ^ deve ser um literal inteiro não negativo, mas recebeu 3.50.
Assembly não gerado.
```

---

### 18.7 Erro: Divisão Inteira com Operando Real

```txt
(START)
(4 A)
(A 2 /)
(END)
```

Resultado esperado:

```txt
Erro semântico: o operador / exige dois operandos inteiros, mas recebeu real e inteiro.
Assembly não gerado.
```

---

### 18.8 Erro: Posição Inexistente em `RES`

```txt
(START)
(10 A)
(1 RES)
(END)
```

Resultado esperado:

```txt
Erro semântico: RES solicitou a posição anterior 1, mas existe apenas 1 resultado anterior disponível.
Assembly não gerado.
```

A única posição existente antes de `(1 RES)` é:

```txt
posição 0 -> resultado de (10 A)
```

---

### 18.9 Erro: `RES` Utilizado Dentro de Expressão

```txt
(START)
(10 A)
((0 RES) 2 +)
(END)
```

Resultado esperado:

```txt
Erro semântico: RES só pode ser usado como comando isolado no formato (N RES).
Assembly não gerado.
```

---

### 18.10 Erro: Resultado Possivelmente `NULL` em Operação

```txt
(START)
(1 A)
(2 B)
(((A B <) A se) 2 +)
(END)
```

Resultado esperado:

```txt
Erro semântico: o operador + não pode utilizar um resultado que pode ser NULL.
Assembly não gerado.
```

---

### 18.11 Erro: Resultado Possivelmente `NULL` em Comparação

```txt
(START)
(1 A)
(2 B)
((((A B <) A se) B <) A se)
(END)
```

Resultado esperado:

```txt
Erro semântico: o operador relacional < não pode utilizar um resultado que pode ser NULL.
Assembly não gerado.
```

---

## 19. Casos de Teste Léxico e de Integração

### 19.1 Comentário Multilinha Válido

```txt
(START)
*{ comentário
em múltiplas
linhas }*
(1 A)
(A)
(END)
```

Resultado esperado:

```txt
comentário descartado pelo analisador léxico
programa semanticamente válido
numeração das linhas preservada
Assembly gerado
```

---

### 19.2 Comentário Não Finalizado

```txt
(START)
(1 A)
*{ comentário sem fechamento
(END)
```

Resultado esperado:

```txt
Erro léxico: comentário iniciado e não finalizado com }*.
Assembly não gerado.
```

O compilador deve apresentar uma mensagem clara, sem traceback do Python.

---

### 19.3 Saídas de Execução Anterior

Procedimento de teste:

```txt
1. Executar um programa válido que gere Assembly.
2. Confirmar a existência de output/assembly_ultima_execucao.s.
3. Executar um programa semanticamente inválido.
4. Conferir que output/assembly_ultima_execucao.s não permanece da execução anterior.
```

Resultado esperado:

```txt
artefatos antigos são removidos no início da nova compilação
programa inválido não deixa Assembly anterior na pasta output
```

---

## 20. Conclusão das Regras Semânticas

Um programa é semanticamente válido quando:

```txt
todas as variáveis são utilizadas após definição;
variáveis novas não são definidas dentro de se ou enquanto;
reatribuições dentro de controles ocorrem apenas para variáveis previamente definidas;
operações usam operandos compatíveis;
potenciação utiliza expoente literal inteiro não negativo;
operadores relacionais aparecem somente como condições diretas;
RES aparece somente isolado e referencia uma posição anterior existente;
resultados que podem ser NULL não são utilizados em operações ou comparações.
```

Somente após a validação dessas regras o compilador produz a árvore sintática atribuída e gera o código Assembly final.
