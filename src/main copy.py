#main.py
import sys
from file_reader import ler_arquivo
from lexer import parserExpressao
from token_reader import salvarTokens, lerTokens
from gramatica import mostrargramatica, construirGramatica
from arvore import gerarArvore, imprimirArvore, salvarArvoreTxt, salvarArvoreJson
from parser import parsear
#from executor import executarExpressao
#from assembly_generator import (
#    inicializar_contexto, 
#    gerarAssembly
#)




def main():
    # ver se tem um arquivo depois do nome do programa
    # ou
    # se o arquivo termina com .txt
    if len(sys.argv) != 2 or not sys.argv[1].endswith(".txt"):
        print("Para rodar deve ter um arquivo.txt, exemplo:: python src/main.py <arquivo.txt>")
        return

    nome_arquivo = sys.argv[1]
    
    
    
    linhas = ler_arquivo(nome_arquivo)

    if not linhas:
        print("nao tem linhas dentro do arquivo ", nome_arquivo)
        return

    # Para a gramatica - Tem a estrutura de dados contento gramática , FIST, FOLLOW e tabela LL(1)
    
    tabelall = construirGramatica()
    print(tabelall)
    print("Conferir a gramatica")
    mostrargramatica()
    
    
    
    #print("Arquivo lido com sucesso!")
    
    #codigoAssembly = inicializar_contexto()
    
    tokens_programa =[]
    for linha in linhas:
        tokens = []
        tokens = parserExpressao(linha, tokens)
        #resultados_novos, memoria, resultados = executarExpressao(tokens, memoria, resultados)
        #print(tokens)
        #codigoAssembly = gerarAssembly(tokens, codigoAssembly)
        print(tokens)
        for token in tokens:
                if token[0] == "INVALIDO":
                    print("Erro léxico:", token)
                    return
        tokens_programa.extend(tokens)
    
    salvarTokens(tokens_programa, "output/tokens_ultima_execucao.txt")

    tokens_lidos = lerTokens("output/tokens_ultima_execucao.txt")
    
    resultadoparser = parsear(tokens_lidos,tabelall)
    
    if resultadoparser["aceito"]:
        
        print("Programa aceito pela gramática.")
        print(resultadoparser)
        arvore = gerarArvore(resultadoparser)

        print("\n=== ÁRVORE SINTÁTICA ===")
        imprimirArvore(arvore)

        salvarArvoreTxt(arvore, "output/arvore_sintatica.txt")
        salvarArvoreJson(arvore, "output/arvore_sintatica.json")

        print("\nArquivos da árvore gerados:")
        print("- output/arvore_sintatica.txt")
        print("- output/arvore_sintatica.json")
    else:
        print("Programa rejeitado pela gramática.")
        for erro in resultadoparser["erros"]:
            print(erro)
    
    #codigoAssembly = montar_codigo_final(codigoAssembly)        
    #print(codigoAssembly)
    
    #with open("output/assembly_ultima_execucao.s", "w", encoding="utf-8") as f:
    #    f.write(codigoAssembly)

if __name__ == "__main__":
    main()