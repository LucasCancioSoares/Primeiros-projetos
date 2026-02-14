# Dicionário com mensagens em três idiomas
mensagens = {
    "pt": {
        "saudacao": "Bem-vindo! Escolha seu idioma:",
        "opcoes": "1. Português\n2. English\n3. Español",
        "escolha": "Digite sua escolha (1, 2 ou 3): ",
        "nome": "Qual é o seu nome? ",
        "idade": "Qual é a sua idade? ",
        "pais": "Qual é o seu país? ",
        "resultado": "Olá mundo, eu sou {}, tenho {} anos e sou do {}",
        "invalido": "Opção inválida! Tente novamente."
    },
    "en": {
        "saudacao": "Welcome! Choose your language:",
        "opcoes": "1. Português\n2. English\n3. Español",
        "escolha": "Enter your choice (1, 2 or 3): ",
        "nome": "What is your name? ",
        "idade": "What is your age? ",
        "pais": "What is your country? ",
        "resultado": "Hello world, I am {}, I am {} years old and I am from {}",
        "invalido": "Invalid option! Try again."
    },
    "es": {
        "saudacao": "¡Bienvenido! Elige tu idioma:",
        "opcoes": "1. Português\n2. English\n3. Español",
        "escolha": "Ingresa tu opción (1, 2 o 3): ",
        "nome": "¿Cuál es tu nombre? ",
        "idade": "¿Cuál es tu edad? ",
        "pais": "¿Cuál es tu país? ",
        "resultado": "Hola mundo, yo soy {}, tengo {} años y soy de {}",
        "invalido": "¡Opción inválida! Intenta de nuevo."
    }
}

# Função para obter o idioma escolhido
def escolher_idioma():
    while True:
        print(mensagens["pt"]["saudacao"])
        print(mensagens["pt"]["opcoes"])
        opcao = input(mensagens["pt"]["escolha"])
        
        if opcao == "1":
            return "pt"
        elif opcao == "2":
            return "en"
        elif opcao == "3":
            return "es"
        else:
            print(mensagens["pt"]["invalido"])
            print()

# Função para coletar dados do usuário
def coletar_dados(idioma):
    msgs = mensagens[idioma]
    nome = input(msgs["nome"])
    idade = input(msgs["idade"])
    pais = input(msgs["pais"])
    return nome, idade, pais

# Programa principal
print()
idioma_selecionado = escolher_idioma()
print()

nome, idade, pais = coletar_dados(idioma_selecionado)
print()

print(mensagens[idioma_selecionado]["resultado"].format(nome, idade, pais))
print()
