EPSILON = "ε"
ENDMARKER = "$"


class LL1Analyzer:
    def __init__(self, grammar, start_symbol):
        """
        grammar: dicionário no formato:
        {
            "E": [["T", "E'"]],
            "E'": [["+", "T", "E'"], ["ε"]],
            "T": [["NUM"], ["ID"]]
        }

        start_symbol: símbolo inicial da gramática
        """

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
        """
        Calcula FIRST de uma sequência.
        Exemplo:
        FIRST(["A", "B", "c"])
        """

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
                self.conflicts.append(
                    {
                        "nonterminal": nonterminal,
                        "terminal": terminal,
                        "existing": existing,
                        "new": production
                    }
                )
        else:
            self.table[nonterminal][terminal] = production

    def analyze(self):
        self.calculate_first()
        self.calculate_follow()
        self.build_ll1_table()

    def print_first(self):
        print("\n=== FIRST ===")
        for nonterminal in sorted(self.nonterminals):
            print(f"FIRST({nonterminal}) = {self.first[nonterminal]}")

    def print_follow(self):
        print("\n=== FOLLOW ===")
        for nonterminal in sorted(self.nonterminals):
            print(f"FOLLOW({nonterminal}) = {self.follow[nonterminal]}")

    def print_table(self):
        print("\n=== TABELA LL(1) ===")

        terminals = sorted(self.terminals) + [ENDMARKER]

        for nonterminal in sorted(self.nonterminals):
            print(f"\n{nonterminal}:")
            for terminal in terminals:
                if terminal in self.table[nonterminal]:
                    production = " ".join(self.table[nonterminal][terminal])
                    print(f"  com {terminal}: {nonterminal} -> {production}")

    def print_conflicts(self):
        print("\n=== RESULTADO ===")

        if not self.conflicts:
            print("A gramática é LL(1). Não há conflitos na tabela.")
        else:
            print("A gramática NÃO é LL(1). Conflitos encontrados:")

            for conflict in self.conflicts:
                nt = conflict["nonterminal"]
                terminal = conflict["terminal"]
                existing = " ".join(conflict["existing"])
                new = " ".join(conflict["new"])

                print()
                print(f"Conflito em Tabela[{nt}, {terminal}]")
                print(f"  Já existia: {nt} -> {existing}")
                print(f"  Tentou adicionar: {nt} -> {new}")


# ==========================
# EXEMPLO DE USO
# ==========================

# ==========================
# EXEMPLO DE USO
# ==========================

EPSILON = "ε"

grammar = {
    "S": [["start", "L", "end"]],

    "L": [
        ["C", "L"],
        [EPSILON]
    ],

    "C": [["epar", "K", "dpar"]],

    "K": [
        ["mem", "A"],
        ["num", "B"],
        ["C", "D"]
    ],

    "A": [
        ["mem", "Z"],
        ["num", "H"],
        ["C", "H"],
        [EPSILON]
    ],

    "B": [
        ["mem", "Z"],
        ["res"],
        ["num", "H"],
        ["C", "H"]
    ],

    "D": [
        ["mem", "Z"],
        ["num", "H"],
        ["C", "H"]
    ],

    "Z": [
        ["H"],
        [EPSILON]
    ],

    "H": [
        ["op"],
        ["oprel"],
        ["se"],
        ["enquanto"]
    ]
}

start_symbol = "S"

analyzer = LL1Analyzer(grammar, start_symbol)

analyzer.analyze()

analyzer.print_first()
analyzer.print_follow()
analyzer.print_table()
analyzer.print_conflicts()