# morse_utils.py

"""
Utilidades para o comando Morse da linguagem.

Este arquivo centraliza:
- tabela internacional de código Morse;
- validação de caracteres aceitos;
- normalização do texto recebido pelo comando morse.

Sintaxe planejada na linguagem:
([SOS] morse)
([JOAO 123!] morse)
([ação] morse)  -> será normalizado para [ACAO]
"""

import unicodedata


TABELA_MORSE = {
    # Letras
    "A": ".-",
    "B": "-...",
    "C": "-.-.",
    "D": "-..",
    "E": ".",
    "F": "..-.",
    "G": "--.",
    "H": "....",
    "I": "..",
    "J": ".---",
    "K": "-.-",
    "L": ".-..",
    "M": "--",
    "N": "-.",
    "O": "---",
    "P": ".--.",
    "Q": "--.-",
    "R": ".-.",
    "S": "...",
    "T": "-",
    "U": "..-",
    "V": "...-",
    "W": ".--",
    "X": "-..-",
    "Y": "-.--",
    "Z": "--..",

    # Números
    "1": ".----",
    "2": "..---",
    "3": "...--",
    "4": "....-",
    "5": ".....",
    "6": "-....",
    "7": "--...",
    "8": "---..",
    "9": "----.",
    "0": "-----",

    # Pontuações e símbolos
    ".": ".-.-.-",
    ",": "--..--",
    "?": "..--..",
    "'": ".----.",
    "!": "-.-.--",
    "/": "-..-.",
    "(": "-.--.",
    ")": "-.--.-",
    "&": ".-...",
    ":": "---...",
    ";": "-.-.-.",
    "=": "-...-",
    "-": "-....-",
    "_": "..--.-",
    '"': ".-..-.",
    "$": "...-..-",
    "@": ".--.-.",
}


def remover_acentos(texto):
    """
    Remove acentos e cedilha.

    Exemplos:
    João  -> Joao
    ação  -> acao
    Ç     -> C
    """

    texto_normalizado = unicodedata.normalize("NFD", texto)

    texto_sem_acentos = ""

    for caractere in texto_normalizado:
        if unicodedata.category(caractere) != "Mn":
            texto_sem_acentos += caractere

    return texto_sem_acentos


def normalizar_texto_morse(texto):
    """
    Normaliza o texto recebido pelo comando morse.

    Regras:
    - remove acentos;
    - remove cedilha;
    - transforma letras em maiúsculas;
    - mantém números;
    - mantém pontuações aceitas;
    - mantém espaços como espaços.
    """

    texto = remover_acentos(texto)
    texto = texto.upper()

    return texto


def caractere_tem_morse(caractere):
    """
    Verifica se um caractere é aceito no Morse.

    O espaço é aceito separadamente, pois ele representa
    separação entre palavras, não um símbolo Morse.
    """

    if caractere == " ":
        return True

    return caractere in TABELA_MORSE


def caracteres_invalidos_morse(texto):
    """
    Retorna os caracteres que não possuem código Morse cadastrado.

    Exemplos:
    SOS      -> []
    João     -> []
    AÇÃO     -> []
    OLÁ      -> []
    teste#   -> ["#"]
    """

    texto_normalizado = normalizar_texto_morse(texto)
    invalidos = []

    for caractere in texto_normalizado:
        if not caractere_tem_morse(caractere):
            invalidos.append(caractere)

    return invalidos


def texto_morse_valido(texto):
    """
    Retorna True se todos os caracteres forem aceitos.
    """

    return len(caracteres_invalidos_morse(texto)) == 0


def converter_texto_para_morse(texto):
    """
    Converte um texto para uma lista de elementos Morse.

    Importante:
    - espaço continua sendo espaço;
    - espaço NÃO vira "/";
    - cada letra/número/símbolo vira seu código Morse.

    Exemplo:
    SOS -> ["...", "---", "..."]

    Exemplo:
    A B -> [".-", " ", "-..."]

    Exemplo:
    João -> [".---", "---", ".-", "---"]
    """

    texto_normalizado = normalizar_texto_morse(texto)

    invalidos = caracteres_invalidos_morse(texto_normalizado)

    if invalidos:
        raise ValueError(
            "Texto possui caracteres sem código Morse: "
            + ", ".join(sorted(set(invalidos)))
        )

    resultado = []

    for caractere in texto_normalizado:
        if caractere == " ":
            resultado.append(" ")
        else:
            resultado.append(TABELA_MORSE[caractere])

    return resultado

