"""
Integrantes do grupo:
Isa Stohler Bertolaccini

Nome do grupo no Canvas: RA2 24
    
"""
# Não consegui pegar o grupo do RA3, pois todos já estão com pessoas
#main.py
import sys
import os
from semantico import prepararEntradaSemantica
from tabela_simbolos import lerArvoreJson, construirTabelaSimbolos
from verificar_tipos import verificarTipos
from arvore_atribuida import gerarArvoreAtribuida
from assembly_generator import gerarAssembly, salvarAssembly, ErroGeracaoAssembly

def limparSaidasAnteriores():
    """
    Remove os artefatos produzidos pela execução anterior.

    Isso evita que um Assembly antigo permaneça na pasta output
    quando o programa atual possuir erro léxico, sintático ou semântico.
    """

    arquivos_saida = [
        "output/tokens_ultima_execucao.txt",
        "output/arvore_sintatica.txt",
        "output/arvore_sintatica.json",
        "output/tabela_simbolos.json",
        "output/tipos_inferidos.json",
        "output/arvore_atribuida.json",
        "output/assembly_ultima_execucao.s"
    ]

    for caminho in arquivos_saida:
        if os.path.exists(caminho):
            os.remove(caminho)

def main():
    # ver se tem um arquivo depois do nome do programa
    # ou
    # se o arquivo termina com .txt
    if len(sys.argv) != 2 or not sys.argv[1].endswith(".txt"):
        print("Para rodar deve ter um arquivo.txt, exemplo:: python src/main.py <arquivo.txt>")
        return
    limparSaidasAnteriores()
    nome_arquivo = sys.argv[1]


    try:
        entrada = prepararEntradaSemantica(nome_arquivo)

    except SyntaxError as erro:
        print("Erro léxico:")
        print(f"- {erro}")
        return
    
    if entrada is None:
        print("A preparação da entrada semântica falhou.")
        return

    #print("Entrada semântica preparada com sucesso.")
    #print("Quantidade de tokens:", len(entrada["tokens"]))
    #print("Arquivo de tokens:", entrada["arquivo_tokens"])
    #print("Arquivo da árvore:", entrada["arquivo_arvore"])
    
    arvore = lerArvoreJson("output/arvore_sintatica.json")

    resultado_simbolos = construirTabelaSimbolos(arvore)

    if resultado_simbolos["erros_semanticos"]:
        print("Erros semânticos encontrados:")

        for erro in resultado_simbolos["erros_semanticos"]:
            print("-", erro)

        return
    resultado_tipos = verificarTipos(
        arvore,
        resultado_simbolos["tabela_simbolos"]
    )

    if resultado_tipos["erros_semanticos"]:
        print("Erros de tipo encontrados:")

        for erro in resultado_tipos["erros_semanticos"]:
            print("-", erro)

        return

    print("Análise semântica concluída com sucesso.")
    print("Arquivo gerado: output/tipos_inferidos.json")
    print("Tabela de símbolos construída com sucesso.")
    print("Arquivo gerado: output/tabela_simbolos.json")
    
    arvore_atribuida = gerarArvoreAtribuida(
        arvore,
        resultado_simbolos["tabela_simbolos"],
        resultado_tipos
    )

    print("Árvore sintática atribuída gerada com sucesso.")
    print("Arquivo gerado: output/arvore_atribuida.json")
    try:
            codigo_assembly = gerarAssembly(arvore_atribuida)

            salvarAssembly(
                codigo_assembly,
                "output/assembly_ultima_execucao.s"
            )

            print("Assembly gerado com sucesso.")
            print("Arquivo gerado: output/assembly_ultima_execucao.s")

    except ErroGeracaoAssembly as erro:
            print("A geração do Assembly foi interrompida.")
            print(erro)
            return
if __name__ == "__main__":
    main()