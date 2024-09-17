import socket

def cliente():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('127.0.0.1', 9999))  # Conectando ao servidor local

    while True:
        # Receber a mensagem do servidor
        mensagem = client.recv(1024).decode('utf-8')
        if not mensagem:
            break
        
        # Exibir a mensagem recebida no console
        print(f"Servidor: {mensagem}")

        if "Pergunta" in mensagem:
            # Solicitar a resposta do usuário
            resposta = input("Sua resposta: ")
            client.send(resposta.encode('utf-8'))

        if "Jogo terminado" in mensagem:
            break

    client.close()

if __name__ == "__main__":
    cliente()
