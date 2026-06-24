# arvore.py
import os
import json


def gerarArvore(derivacao):
    """
    Recebe o resultado da função parsear().
    Retorna a árvore sintática estruturada.
    """

    if not derivacao["aceito"]:
        raise ValueError("Não é possível gerar árvore: o parser encontrou erros sintáticos.")

    return derivacao["arvore"]


def imprimirArvore(no, nivel=0):
    """
    Imprime a árvore sintática de forma legível.
    """

    espaco = "  " * nivel
    simbolo = no["simbolo"]

    if no.get("token") is not None:
        print(f"{espaco}{simbolo} -> {no['token']}")
    else:
        print(f"{espaco}{simbolo}")

    for filho in no.get("filhos", []):
        imprimirArvore(filho, nivel + 1)


def arvoreParaTexto(no, nivel=0):
    """
    Converte a árvore para texto.
    """

    espaco = "  " * nivel
    simbolo = no["simbolo"]

    if no.get("token") is not None:
        texto = f"{espaco}{simbolo} -> {no['token']}\n"
    else:
        texto = f"{espaco}{simbolo}\n"

    for filho in no.get("filhos", []):
        texto += arvoreParaTexto(filho, nivel + 1)

    return texto


def salvarArvoreTxt(arvore, caminho="output/arvore_sintatica.txt"):
    os.makedirs(os.path.dirname(caminho), exist_ok=True)

    texto = arvoreParaTexto(arvore)

    with open(caminho, "w", encoding="utf-8") as arquivo:
        arquivo.write(texto)


def salvarArvoreJson(arvore, caminho="output/arvore_sintatica.json"):
    os.makedirs(os.path.dirname(caminho), exist_ok=True)

    with open(caminho, "w", encoding="utf-8") as arquivo:
        json.dump(arvore, arquivo, indent=4, ensure_ascii=False)