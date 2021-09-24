from Sintatico import Sintatico
import sys

def main(arquivo):

    sintatico = Sintatico(arquivo)
    sintatico.analisar()

    print("Tabela de simbolos:")
    print(sintatico.tabelaSimbolo)
    print("Codigo intermediario:")
    print(sintatico.codigo)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Por favor passe o arquivo de entrada.")
    elif len(sys.argv) > 2:
        print("Por favor passe somente o arquivo de entrada.")
    main(sys.argv[1])
