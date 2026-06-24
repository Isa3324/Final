from file_reader import ler_arquivo
from lexer import parserExpressao, removerComentarios
from token_reader import salvarTokens, lerTokens
from gramatica import construirGramatica
from arvore import gerarArvore, salvarArvoreTxt, salvarArvoreJson
from parser import parsear

def prepararEntradaSemantica(nome_arquivo):
    tabelall = construirGramatica()
    
    linhas = ler_arquivo(nome_arquivo)

    if not linhas:
        print("nao tem linhas dentro do arquivo ", nome_arquivo)
        return

    # Junta o arquivo inteiro para permitir comentário em qualquer lugar
    codigo = "\n".join(linhas)
    
    # Remove comentários *{ ... }*
    codigo_sem_comentarios = removerComentarios(codigo)

    # Volta para linhas normais
    linhas_sem_comentarios = codigo_sem_comentarios.splitlines()
    
    

    tokens_programa =[]
    for numero_linha, linha in enumerate(linhas_sem_comentarios, start=1):
        linha = linha.strip()

        if linha == "":
            continue
        
        tokens = []
        tokens = parserExpressao(linha, tokens)
        for token in tokens:
            if token[0] == "INVALIDO":
                print(f"Erro léxico na linha {numero_linha}:", token)
                return None

            tipo_token, valor, posicao = token
            tokens_programa.append((tipo_token, valor, posicao, numero_linha))
    
    salvarTokens(tokens_programa, "output/tokens_ultima_execucao.txt")
    tokens_lidos = lerTokens("output/tokens_ultima_execucao.txt")
    resultadoparser = parsear(tokens_lidos,tabelall)
    
    if resultadoparser["aceito"]:
        #print("Programa aceito pela gramática.")
        #print(resultadoparser)
        arvore = gerarArvore(resultadoparser)
        #print("\n=== ÁRVORE SINTÁTICA ===")
        #imprimirArvore(arvore)
        salvarArvoreTxt(arvore, "output/arvore_sintatica.txt")
        salvarArvoreJson(arvore, "output/arvore_sintatica.json")
        #print("\nArquivos da árvore gerados:")
        #print("- output/arvore_sintatica.txt")
        #print("- output/arvore_sintatica.json")
        return {
            "tokens": tokens_lidos,
            "arvore": arvore,
            "resultado_parser": resultadoparser,
            "arquivo_tokens": "output/tokens_ultima_execucao.txt",
            "arquivo_arvore": "output/arvore_sintatica.json"
        }
    else:
        print("Programa rejeitado pela gramática.")
        for erro in resultadoparser["erros"]:
            print(erro)
        return None
    


