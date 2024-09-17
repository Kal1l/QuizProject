import socket
import threading
import random

# Banco de questões no servidor
questoes = [
    ("Qual é a capital da França?", "Paris"),
    ("Qual é a fórmula química da água?", "H2O"),
    ("Quem pintou a Mona Lisa?", "Leonardo da Vinci"),
    ("Qual é o planeta mais próximo do Sol?", "Mercúrio"),
    ("Quem escreveu 'Dom Quixote'?", "Miguel de Cervantes")
]

# Definir o número de jogadores (excluindo o servidor)
NUM_JOGADORES = 2  # 4 jogadores + servidor que apenas administra
NUM_QUESTOES = 5

# Randomizar as questões
random.shuffle(questoes)

# Estrutura para manter as pontuações dos jogadores
pontuacoes = {}
jogadores = {}
jogadores_conectados = 0
lock = threading.Lock()

# Função que trata as conexões com os clientes
def handle_client(client_socket, client_address, jogador_id):
    global jogadores, jogadores_conectados, lock
    print(f"Conexão estabelecida com o jogador {jogador_id} de {client_address}")

    # Adiciona o jogador à lista de jogadores conectados
    with lock:
        jogadores[jogador_id] = client_socket
        pontuacoes[jogador_id] = 0
        jogadores_conectados += 1

    # Espera até que todos os jogadores estejam conectados
    while jogadores_conectados < NUM_JOGADORES:
        pass

    print(f"Todos os jogadores conectados! Começando o jogo.")

# Função para enviar uma mensagem para todos os clientes
def enviar_para_todos(mensagem):
    for jogador_socket in jogadores.values():
        try:
            jogador_socket.send(mensagem.encode('utf-8'))
        except:
            print("Erro ao enviar mensagem para um jogador.")

# Função principal do servidor (apenas admin, sem participação como jogador)
def servidor():
    global jogadores_conectados
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', 9999))  # Porta 9999
    server.listen(NUM_JOGADORES)
    print("Servidor aguardando conexões...")

    # Aguardando os jogadores conectarem (ignora o servidor como jogador)
    threads = []
    for jogador_id in range(NUM_JOGADORES):
        client_socket, client_address = server.accept()
        thread = threading.Thread(target=handle_client, args=(client_socket, client_address, jogador_id))
        threads.append(thread)
        thread.start()

    # Espera até que todos os jogadores estejam conectados
    for thread in threads:
        thread.join()

    # Jogo começa aqui (o servidor apenas envia perguntas e analisa respostas)
    for i, (pergunta, resposta_correta) in enumerate(questoes[:NUM_QUESTOES]):
        print(f"Iniciando questão {i+1}: {pergunta}")
        vencedor_encontrado = False

        # Enviar a pergunta para todos os jogadores de uma vez
        enviar_para_todos(f"Pergunta {i+1}: {pergunta}")

        while not vencedor_encontrado:
            for jogador_id, jogador_socket in jogadores.items():
                try:
                    resposta_cliente = jogador_socket.recv(1024).decode('utf-8').strip()

                    # Se o jogador acertar a resposta
                    if resposta_cliente.lower() == resposta_correta.lower():
                        pontuacoes[jogador_id] += 1  # Atribuir ponto ao jogador que acertou
                        jogador_socket.send("Correto! Aguardando a próxima pergunta...".encode('utf-8'))

                        # Informar a todos os jogadores que a questão foi acertada
                        enviar_para_todos(f"Jogador {jogador_id} acertou a questão! Preparando próxima pergunta...")

                        # Dar uma pequena pausa antes de enviar a próxima questão
                        vencedor_encontrado = True
                        break  # Sai do loop dos jogadores

                except:
                    print(f"Erro ao comunicar com o jogador {jogador_id}")

    # Fechar as conexões e mostrar o vencedor
    print("\n--- Jogo terminado ---")
    for jogador, pontos in pontuacoes.items():
        print(f"Jogador {jogador}: {pontos} pontos")

    vencedor = max(pontuacoes, key=pontuacoes.get)
    print(f"O jogador {vencedor} venceu o jogo!")

    # Fechar todas as conexões
    for jogador_socket in jogadores.values():
        jogador_socket.close()

if __name__ == "__main__":
    servidor()
