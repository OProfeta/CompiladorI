from Sintatico import Sintatico
from Scanner import Scanner

def main():
    # scan = Scanner("correto.lalg.txt")
    # while True:
    #     token = scan.nextToken()
    #     if token == None:
    #         break
    #     print(token.toString())
    sintatico = Sintatico("correto.lalg.txt")
    sintatico.analisar()

if __name__ == "__main__":
    main()