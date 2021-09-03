from Scanner import Scanner

def main():
    scan = Scanner("correto.lalg.txt")
    while True:
        token = scan.nextToken()
        if token == None:
            break
        print(token.toString())

if __name__ == "__main__":
    main()