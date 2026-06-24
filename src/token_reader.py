import json
import os


def salvarTokens(tokens, caminho="output/tokens_ultima_execucao.txt"):
    os.makedirs(os.path.dirname(caminho), exist_ok=True)

    tokens_json = []

    for token in tokens:
        tokens_json.append({
            "tipo": token[0],
            "valor": token[1],
            "posicao": token[2],
            "linha": token[3] if len(token) > 3 else None
        })

    with open(caminho, "w", encoding="utf-8") as arquivo:
        json.dump(tokens_json, arquivo, indent=4, ensure_ascii=False)


def lerTokens(caminho):
    with open(caminho, "r", encoding="utf-8") as arquivo:
        tokens_json = json.load(arquivo)

    tokens = []

    for token in tokens_json:
        tokens.append((
            token["tipo"],
            token["valor"],
            token["posicao"],
            token.get("linha")
        ))

    return tokens