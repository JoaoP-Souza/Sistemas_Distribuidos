def lista_games(estoque):
    if len(estoque) == 0:
        print("Nenhum Game cadastrado.")
    else:
        print("Games cadastrados:")
        for game in estoque:
            print(game)

def cadastra_game(estoque):
    game = input("Digite o nome do game: ")
    plataforma = input("Digite a plataforma do game: ")
    quantidade = int(input("Digite a quantidade de cópias: "))
    estoque.append({"game": game, "plataforma": plataforma, "quantidade": quantidade})
    print(f"Game '{game}' cadastrado no sistema!")

def consulta_game(estoque):
    nome_game = input("Digite o nome do jogo que deseja consultar: ")
    for game in estoque:
        if game["game"] == nome_game:
            print(f"Game: {game['game']}")
            print(f"Plataforma: {game['plataforma']}")
            print(f"Quantidade: {game['quantidade']}")
            return
    print("O Game não foi encontrado no sistema :(")

def vende_game(estoque):
    nome_game = input("Digite o nome do game que deseja vender: ")
    for game in estoque:
        if game["game"] == nome_game:
            quantidade = int(input("Digite a quantidade de cópias que deseja vender: "))
            if game["quantidade"] < quantidade:
                print("Quantidade insuficiente no estoque!")
            else:
                game["quantidade"] -= quantidade
                print(f"Venda realizada com sucesso! Quantidade restante: {game['quantidade']}")
            return
    print("Game não encontrado no sistema :(")   

def main():
    estoque = []
    while True:
        print('------------------------------------------------------')
        print("Bem vindo a MyGamestore!")
        print("Selecione uma opção:")
        print("1. Listar Games já cadastrados")	
        print("2. Cadastrar novo Game")
        print("3. Consultar Game disponível")
        print("4. Vender Game")
        print("5. Sair")
        print('------------------------------------------------------')
        
        opcao = input("Escolha uma opção: ")
        
        if opcao == '1':
            lista_games(estoque)
        elif opcao == '2':
            cadastra_game(estoque)
        elif opcao == '3':
            consulta_game(estoque)
        elif opcao == '4':
            vende_game(estoque)
        elif opcao == '5':
            print("Até mais!")
            break
        else:
            print("Digite uma opção válida!")

if __name__ == "__main__":
    main()