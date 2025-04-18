import random
import requests
import time
import os

def random_num(min_val, max_val):
    return str(random.randint(min_val, max_val))

def procura_template_id(game_id):
    url = f"https://wordwall.net/pt/resource/{game_id}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36',
        'Pragma': 'no-cache',
        'Accept': '*/*'
    }
    response = requests.get(url, headers=headers)
    resposta_texto = response.text

    start = 's.templateId=Number('
    end = ');s.feedbackTemplateId='

    start_index = resposta_texto.find(start)
    end_index = resposta_texto.find(end, start_index)

    if start_index != -1 and end_index != -1:
        start_index += len(start)
        template_id = resposta_texto[start_index:end_index]
        return template_id.strip()
    else:
        return "Template ID não encontrado."

def escolha():
    os.system("cls" if os.name == "nt" else "clear")
    print("Escolha uma das opções:\n\n1- Qual Template ID?\n2- Input do placar")
    return input("\n")

def escolha_metodo():
    os.system("cls" if os.name == "nt" else "clear")
    print("Escolha o método de envio do score:\n\n1- Spam\n2- Somente Um")
    return input("\n")

def input_score_spam(template_id=None, game_id=None):
    score_input, nickname, game_id, template_id, tempo_mais_foda = get_score_input(template_id, game_id)

    url = "https://wordwall.net/leaderboardajax/addentry"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36',
        'Pragma': 'no-cache',
        'Accept': '*/*'
    }

    while True:
        var = random_num(10, 1000)
        data = {
            'score': score_input,
            'time': tempo_mais_foda,
            'name': nickname + var,
            'mode': '1',
            'activityId': game_id,
            'templateId': template_id
        }

        response = requests.post(url, headers=headers, data=data)
        print(response.text)
        time.sleep(0.1)  # Aguardar 100 milissegundos

def input_score_somente_um(template_id=None, game_id=None):
    score_input, nickname, game_id, template_id, tempo_mais_foda = get_score_input(template_id, game_id)

    url = "https://wordwall.net/leaderboardajax/addentry"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36',
        'Pragma': 'no-cache',
        'Accept': '*/*'
    }

    data = {
        'score': score_input,
        'time': tempo_mais_foda,
        'name': nickname,
        'mode': '1',
        'activityId': game_id,
        'templateId': template_id
    }

    response = requests.post(url, headers=headers, data=data)
    print(response.text)
    input()

def get_score_input(template_id=None, game_id=None):
    os.system("cls" if os.name == "nt" else "clear")
    score_input = input("Score Desejado: ")
    nickname = input("NickName: ")
    if game_id is None:
        game_id = input("ID do Jogo: ")
    if template_id is None:
        template_id = input("ID do Template: ")
    tempo = input("Tempo Em Segundos: ")

    try:
        numero_foda = float(tempo)
    except ValueError:
        print("Tempo deve ser um número.")
        return

    tempo_mais_foda = str(int(numero_foda * 1000))
    return score_input, nickname, game_id, template_id, tempo_mais_foda

def main():
    while True:
        opcao = escolha()

        if opcao == "1":
            game_id = input("ID do Jogo: ")
            template_id = procura_template_id(game_id)
            print(f"Template ID encontrado: {template_id}")

            usar_template = input("Deseja usar o Template ID encontrado para fazer o input do score? (s/n): ")
            if usar_template.lower() == 's':
                metodo = escolha_metodo()
                if metodo == "1":
                    input_score_spam(template_id, game_id)
                elif metodo == "2":
                    input_score_somente_um(template_id, game_id)
                else:
                    print("Método inválido. Por favor, escolha novamente.")
            else:
                metodo = escolha_metodo()
                if metodo == "1":
                    input_score_spam(game_id=game_id)
                elif metodo == "2":
                    input_score_somente_um(game_id=game_id)
                else:
                    print("Método inválido. Por favor, escolha novamente.")

        elif opcao == "2":
            metodo = escolha_metodo()
            if metodo == "1":
                input_score_spam()
            elif metodo == "2":
                input_score_somente_um()
            else:
                print("Método inválido. Por favor, escolha novamente.")
        else:
            print("Opção inválida. Por favor, escolha novamente.")

if __name__ == "__main__":
    main()
