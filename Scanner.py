class Scanner():

    def __init__(self, input):
        with open(input) as arq:
            self.conteudo = arq.read()