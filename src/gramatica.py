
import os
import json

EPSILON = "ε"
ENDMARKER = "$"

class LL1Analyzer:
    def __init__(self, grammar, start_symbol):
        self.grammar = grammar
        self.start_symbol = start_symbol

        self.nonterminals = set(grammar.keys())
        self.terminals = self._find_terminals()

        self.first = {nt: set() for nt in self.nonterminals}
        self.follow = {nt: set() for nt in self.nonterminals}

        self.table = {}
        self.conflicts = []

    def _find_terminals(self):
        terminals = set()

        for productions in self.grammar.values():
            for production in productions:
                for symbol in production:
                    if symbol != EPSILON and symbol not in self.nonterminals:
                        terminals.add(symbol)

        return terminals

    def first_of_symbol(self, symbol):
        if symbol == EPSILON:
            return {EPSILON}

        if symbol in self.terminals:
            return {symbol}

        if symbol in self.nonterminals:
            return self.first[symbol]

        raise ValueError(f"Símbolo desconhecido: {symbol}")

    def first_of_sequence(self, sequence):
        if not sequence:
            return {EPSILON}

        result = set()

        for symbol in sequence:
            symbol_first = self.first_of_symbol(symbol)

            result.update(symbol_first - {EPSILON})

            if EPSILON not in symbol_first:
                break
        else:
            result.add(EPSILON)

        return result

    def calculate_first(self):
        changed = True

        while changed:
            changed = False

            for nonterminal, productions in self.grammar.items():
                for production in productions:
                    before = len(self.first[nonterminal])

                    production_first = self.first_of_sequence(production)
                    self.first[nonterminal].update(production_first)

                    after = len(self.first[nonterminal])

                    if after > before:
                        changed = True

    def calculate_follow(self):
        self.follow[self.start_symbol].add(ENDMARKER)

        changed = True

        while changed:
            changed = False

            for left_side, productions in self.grammar.items():
                for production in productions:
                    for i, symbol in enumerate(production):
                        if symbol not in self.nonterminals:
                            continue

                        beta = production[i + 1:]
                        first_beta = self.first_of_sequence(beta)

                        before = len(self.follow[symbol])

                        self.follow[symbol].update(first_beta - {EPSILON})

                        if EPSILON in first_beta:
                            self.follow[symbol].update(self.follow[left_side])

                        after = len(self.follow[symbol])

                        if after > before:
                            changed = True

    def build_ll1_table(self):
        for nonterminal in self.nonterminals:
            self.table[nonterminal] = {}

        for left_side, productions in self.grammar.items():
            for production in productions:
                production_first = self.first_of_sequence(production)

                for terminal in production_first - {EPSILON}:
                    self._add_to_table(left_side, terminal, production)

                if EPSILON in production_first:
                    for terminal in self.follow[left_side]:
                        self._add_to_table(left_side, terminal, production)

    def _add_to_table(self, nonterminal, terminal, production):
        if terminal in self.table[nonterminal]:
            existing = self.table[nonterminal][terminal]

            if existing != production:
                self.conflicts.append({
                    "nonterminal": nonterminal,
                    "terminal": terminal,
                    "existing": existing,
                    "new": production
                })
        else:
            self.table[nonterminal][terminal] = production

    def analyze(self):
        self.calculate_first()
        self.calculate_follow()
        self.build_ll1_table()
def definirRegrasGramatica():
    grammar = {
        "programa": [["START", "lista_comandos", "END"]],

        "lista_comandos": [
            ["comando", "lista_comandos"],
            [EPSILON]
        ],

        "comando": [["EPAR", "conteudo", "DPAR"]],

        "conteudo": [
            ["MEM", "cont_mem"],
            ["NUM", "cont_num"],
            ["comando", "cont_comando"]
        ],

        "cont_mem": [
            ["MEM", "fim_mem"],
            ["NUM", "operador_final"],
            ["comando", "operador_final"],
            [EPSILON]
        ],

        "cont_num": [
            ["MEM", "fim_mem"],
            ["RES"],
            ["NUM", "operador_final"],
            ["comando", "operador_final"]
        ],

        "cont_comando": [
            ["MEM", "fim_mem"],
            ["NUM", "operador_final"],
            ["comando", "operador_final"]
        ],

        "fim_mem": [
            ["operador_final"],
            [EPSILON]
        ],

        "operador_final": [
            ["OP"],
            ["OPREL"],
            ["SE"],
            ["ENQUANTO"]
        ]
    }

    start_symbol = "programa"
    return grammar, start_symbol
def construirGramatica():
    resultado = construirAnaliseLL1()

    if not resultado["eh_ll1"]:
        raise Exception("A gramática não é LL(1). Verifique o arquivo tests/gramaticatest.txt.")

    return resultado["tabela_ll1"]
def formatar_conjunto(conjunto):
    return "{ " + ", ".join(sorted(conjunto)) + " }"
def salvarRelatorioGramatica(analyzer, caminho="output/gramaticatest.txt"):
    os.makedirs(os.path.dirname(caminho), exist_ok=True)

    with open(caminho, "w", encoding="utf-8") as arquivo:
        arquivo.write("RELATÓRIO DE TESTE DA GRAMÁTICA LL(1)\n")
        arquivo.write("=" * 50 + "\n\n")

        arquivo.write("1. GRAMÁTICA\n\n")

        for nao_terminal, producoes in analyzer.grammar.items():
            for producao in producoes:
                arquivo.write(f"{nao_terminal} -> {' '.join(producao)}\n")

        arquivo.write("\n" + "=" * 50 + "\n\n")

        arquivo.write("2. NÃO-TERMINAIS\n\n")
        for nt in sorted(analyzer.nonterminals):
            arquivo.write(f"- {nt}\n")

        arquivo.write("\n" + "=" * 50 + "\n\n")

        arquivo.write("3. TERMINAIS\n\n")
        for t in sorted(analyzer.terminals):
            arquivo.write(f"- {t}\n")

        arquivo.write("\n" + "=" * 50 + "\n\n")

        arquivo.write("4. CONJUNTOS FIRST\n\n")
        for nt in sorted(analyzer.nonterminals):
            arquivo.write(f"FIRST({nt}) = {formatar_conjunto(analyzer.first[nt])}\n")

        arquivo.write("\n" + "=" * 50 + "\n\n")

        arquivo.write("5. CONJUNTOS FOLLOW\n\n")
        for nt in sorted(analyzer.nonterminals):
            arquivo.write(f"FOLLOW({nt}) = {formatar_conjunto(analyzer.follow[nt])}\n")

        arquivo.write("\n" + "=" * 50 + "\n\n")

        arquivo.write("6. TABELA LL(1)\n\n")

        terminais = sorted(analyzer.terminals) + [ENDMARKER]

        for nt in sorted(analyzer.nonterminals):
            arquivo.write(f"[{nt}]\n")

            for terminal in terminais:
                if terminal in analyzer.table[nt]:
                    producao = " ".join(analyzer.table[nt][terminal])
                    arquivo.write(f"  com {terminal}: {nt} -> {producao}\n")

            arquivo.write("\n")

        arquivo.write("=" * 50 + "\n\n")

        arquivo.write("7. RESULTADO\n\n")

        if not analyzer.conflicts:
            arquivo.write("A gramática é LL(1). Não há conflitos na tabela.\n")
        else:
            arquivo.write("A gramática NÃO é LL(1). Conflitos encontrados:\n\n")

            for conflito in analyzer.conflicts:
                nt = conflito["nonterminal"]
                terminal = conflito["terminal"]
                existente = " ".join(conflito["existing"])
                novo = " ".join(conflito["new"])

                arquivo.write(f"Conflito em Tabela[{nt}, {terminal}]\n")
                arquivo.write(f"  Já existia: {nt} -> {existente}\n")
                arquivo.write(f"  Tentou adicionar: {nt} -> {novo}\n\n")
def salvarTabelaLL1Json(analyzer, caminho="tests/tabela_ll1.json"):
    os.makedirs(os.path.dirname(caminho), exist_ok=True)

    dados = {
        "simbolo_inicial": analyzer.start_symbol,
        "epsilon": EPSILON,
        "endmarker": ENDMARKER,
        "nao_terminais": sorted(analyzer.nonterminals),
        "terminais": sorted(analyzer.terminals),
        "tabela_ll1": analyzer.table
    }

    with open(caminho, "w", encoding="utf-8") as arquivo:
        json.dump(dados, arquivo, indent=4, ensure_ascii=False)
def construirAnaliseLL1():
    grammar, start_symbol = definirRegrasGramatica()

    analyzer = LL1Analyzer(grammar, start_symbol)
    analyzer.analyze()

    return {
        "analyzer": analyzer,
        "gramatica": analyzer.grammar,
        "simbolo_inicial": analyzer.start_symbol,
        "terminais": analyzer.terminals,
        "nao_terminais": analyzer.nonterminals,
        "first": analyzer.first,
        "follow": analyzer.follow,
        "tabela_ll1": analyzer.table,
        "conflitos": analyzer.conflicts,
        "eh_ll1": len(analyzer.conflicts) == 0
    }
def mostrargramatica():
    resultado = construirAnaliseLL1()
    analyzer = resultado["analyzer"]

    salvarRelatorioGramatica(analyzer, "tests/gramaticatest.txt")
    salvarTabelaLL1Json(analyzer, "tests/tabela_ll1.json")