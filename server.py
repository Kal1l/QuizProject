import socket
import threading
import random
import time

# Banco de questões no servidor
questoes = [
    ("Qual é a capital da França?", "Paris"),
    ("Qual é a fórmula química da água?", "H2O"),
    ("Quem pintou a Mona Lisa?", "Leonardo da Vinci"),
    ("Qual é o planeta mais próximo do Sol?", "Mercúrio"),
    ("Quem escreveu 'Dom Quixote'?", "Miguel de Cervantes")
]

NUM_JOGADORES = 2
NUM_QUESTOES = 5

random.shuffle(questoes)

pontuacoes = {}
jogadores = {}
jogadores_conectados = 0
lock = threading.Lock()

def handle_client(client_socket, client_address, jogador_id):
    global jogadores, jogadores_conectados, lock
    print(f"Conexão estabelecida com o jogador {jogador_id} de {client_address}")

    with lock:
        jogadores[jogador_id] = client_socket
        pontuacoes[jogador_id] = 0
        jogadores_conectados += 1

    while jogadores_conectados < NUM_JOGADORES:
        pass

    print(f"Todos os jogadores conectados! Começando o jogo.")

def enviar_para_todos(mensagem):
    for jogador_socket in jogadores.values():
        try:
            jogador_socket.send(mensagem.encode('utf-8'))
        except:
            print("Erro ao enviar mensagem para um jogador.")

def servidor():
    global jogadores_conectados
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', 9999))
    server.listen(NUM_JOGADORES)
    print("Servidor aguardando conexões...")

    threads = []
    for jogador_id in range(NUM_JOGADORES):
        client_socket, client_address = server.accept()
        thread = threading.Thread(target=handle_client, args=(client_socket, client_address, jogador_id))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    # Jogo começa aqui
    for i, (pergunta, resposta_correta) in enumerate(questoes[:NUM_QUESTOES]):
        print(f"Iniciando questão {i+1}: {pergunta}")
        vencedor_encontrado = False

        enviar_para_todos(f"Pergunta {i+1}: {pergunta}")
        time.sleep(1)

        while not vencedor_encontrado:
            for jogador_id, jogador_socket in list(jogadores.items()):
                try:
                    jogador_socket.settimeout(10)  # Definir um tempo limite para respostas
                    resposta_cliente = jogador_socket.recv(1024).decode('utf-8').strip()

                    if resposta_cliente.lower() == resposta_correta.lower():
                        pontuacoes[jogador_id] += 1
                        jogador_socket.send("Correto! Aguardando a próxima pergunta...".encode('utf-8'))
                        enviar_para_todos(f"Jogador {jogador_id} acertou a questão! Preparando próxima pergunta...")
                        vencedor_encontrado = True
                        break
                    else:
                        jogador_socket.send("Resposta incorreta, tente novamente.".encode('utf-8'))

                except socket.timeout:
                    print(f"Tempo de resposta do jogador {jogador_id} esgotado.")
                except Exception as e:
                    print(f"Erro ao comunicar com o jogador {jogador_id}: {e}")

        time.sleep(1)

    print("\n--- Jogo terminado ---")
    for jogador, pontos in pontuacoes.items():
        print(f"Jogador {jogador}: {pontos} pontos")

    vencedor = max(pontuacoes, key=pontuacoes.get)
    print(f"O jogador {vencedor} venceu o jogo!")

    for jogador_socket in jogadores.values():
        jogador_socket.close()

if __name__ == "__main__":
    servidor()
