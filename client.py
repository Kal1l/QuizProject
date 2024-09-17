import socket
import random
import threading
import time  # Importar time para adicionar sleep

respostas_possiveis = [
    "Paris", "H2O", "Mercúrio", "Miguel de Cervantes", "Leonardo da Vinci"
]

def simular_resposta(canal, pergunta):
    resposta_certa_encontrada = False

    while not resposta_certa_encontrada:
        resposta = random.choice(respostas_possiveis)
        print(f"Enviando resposta: {resposta}")
        canal.send(resposta.encode('utf-8'))

        feedback = canal.recv(1024).decode('utf-8')
        print(f"Feedback do servidor: {feedback}")

        if "Correto" in feedback:
            resposta_certa_encontrada = True
        else:
            time.sleep(1)  # Pausa entre as tentativas

def cliente(jogador_id):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('127.0.0.1', 9999))

    while True:
        pergunta = client_socket.recv(1024).decode('utf-8')
        print(f"Jogador {jogador_id} recebeu a pergunta: {pergunta}")

        simular_resposta(client_socket, pergunta)

def iniciar_cliente(jogador_id):
    cliente_thread = threading.Thread(target=cliente, args=(jogador_id,))
    cliente_thread.start()

if __name__ == "__main__":
    jogador_id = random.randint(1, 1000)
    iniciar_cliente(jogador_id)
