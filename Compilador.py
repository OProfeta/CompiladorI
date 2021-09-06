from Sintatico import Sintatico
from Scanner import Scanner

def main():
    sintatico = Sintatico("correto.lalg.txt")
    sintatico.analisar()

    print("Tabela de simbolos:")
    print(sintatico.tabelaSimbolo)
    print("Codigo intermediario:")
    print(sintatico.codigo)

if __name__ == "__main__":
    main()
