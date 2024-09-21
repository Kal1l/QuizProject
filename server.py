import socket
import threading
import random
import time
import select

# Banco de questões no servidor
questoes = [
    ("Qual é a capital da França?", "Paris"),
    ("Qual é a fórmula química da água?", "H2O"),
    ("Quem pintou a Mona Lisa?", "Leonardo da Vinci"),
    ("Qual é o planeta mais próximo do Sol?", "Mercúrio"),
    ("Quem escreveu 'Dom Quixote'?", "Miguel de Cervantes"),
    ("Quantos continentes existem no mundo?", "Sete"),
    ("Qual é o maior oceano do mundo?", "Pacífico"),
    ("Qual é o número romano para 10?", "X"),
    ("Quantos dias tem um ano bissexto?", "366"),
    ("Quem foi o primeiro homem a pisar na Lua?", "Neil Armstrong")
]

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Definir o número de jogadores (excluindo o servidor)
NUM_JOGADORES = 2  # 2 jogadores MUDAR PRA 4 QUANDO FOR TESTAR
NUM_QUESTOES = 10
MSG_LENGTH = 10

# Randomizar as questões
random.shuffle(questoes)

# Estrutura para manter as pontuações dos jogadores
pontuacoes = {}
jogadores = []
jogadores_conectados = 0
lock = threading.Lock()

# Função que trata as conexões com os clientes
def handle_client(client_socket, client_address, jogador_id):
    global jogadores, jogadores_conectados, lock
    print(f"Conexão estabelecida com o jogador {jogador_id} de {client_address}")

    # Adiciona o jogador à lista de jogadores conectados
    with lock:
        jogadores.append(client_socket)
        pontuacoes[jogador_id] = 0
        jogadores_conectados += 1

    # Espera até que todos os jogadores estejam conectados
    while jogadores_conectados < NUM_JOGADORES:
        pass

    print(f"Todos os jogadores conectados! Começando o jogo.")

# Função para enviar uma mensagem para todos os clientes
def enviar_para_todos(sender, mensagem):
    if isinstance(mensagem, str):
        mensagem_bytes = mensagem.encode('utf-8')
    else:
        mensagem_bytes = mensagem
    mensagem_completa = mensagem_bytes
    for jogador_socket in jogadores:
        try:
            jogador_socket.send(mensagem_completa)
        except Exception as e:
            print(f"Erro ao enviar mensagem: {e}")
            jogador_socket.close()
            jogadores.remove(jogador_socket)
                
def receber_mensagem(client_socket):
    try:
        mensagem = client_socket.recv(1024).decode('utf-8')
        if mensagem:
            return mensagem
        else:
            jogadores.remove(client_socket)
            client_socket.close()
            return None
    except Exception as e:
        print(f"Erro ao receber mensagem: {e}")
        jogadores.remove(client_socket)
        client_socket.close()
        return None
    
def enviar_uma_mensagem(receiver, mensagem):
    try:
        if isinstance(mensagem, str):
            mensagem_bytes = mensagem.encode('utf-8')
        else:
            mensagem_bytes = mensagem
        receiver.sendall(mensagem_bytes)
    except Exception as e:
        print(f"Erro ao enviar mensagem: {e}")
        receiver.close()
        jogadores.remove(receiver)
        
def enviar_mensagem_final():
    print("\n--- Jogo Terminado ---")
    mensagem_final = "\n--- Jogo Terminado ---\n"
    
    for jogador, pontos in pontuacoes.items():
        resultado = f"\nJogador {jogador}: {pontos} pontos\n"
        print(resultado)
        mensagem_final += resultado
        
    max_pontos = max(pontuacoes.values())
    vencedores = [jogador for jogador, pontos in pontuacoes.items() if pontos == max_pontos]
    
    if len(vencedores) > 1:
        resultado = f"\nEmpate entre os jogadores {', '.join(map(str, vencedores))} com {max_pontos} pontos!\n"
        print(resultado)
        mensagem_final += resultado
    else:
        vencedor = vencedores[0]
        resultado = f"\nO jogador {vencedor} venceu o jogo!\n"
        print(resultado)
        mensagem_final += resultado
        
    enviar_para_todos(server, mensagem_final)
    
    for jogador_socket in jogadores:
        jogador_socket.close()

# Função principal do servidor (apenas admin, sem participação como jogador)
def servidor():
    global jogadores_conectados
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('0.0.0.0', 9999))  # Porta 9999
    server.listen(NUM_JOGADORES)
    print("Servidor aguardando conexões...")

    # Aguardando os jogadores conectarem
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

        # Enviar a pergunta para todos os jogadores
        enviar_para_todos(server, f"Pergunta {i+1}: {pergunta}")
        time.sleep(1)  # Pausa para os jogadores receberem a pergunta
        
        respostas= {}
        sockets_jogadores = jogadores
        
        while len(respostas) < NUM_JOGADORES:
            readable, _, _ = select.select(sockets_jogadores, [], [], None)
            
            for jogador_socket in readable:
                jogador_id = jogadores.index(jogador_socket)
                try:
                    resposta_cliente = jogador_socket.recv(1024).decode('utf-8').strip()
                    if resposta_cliente:
                        respostas[jogador_id] = resposta_cliente  # Salvar a resposta do jogador
                except Exception as e:
                    print(f"Erro ao comunicar com o jogador {jogador_id}: {e}")
                    jogadores.remove(jogador_socket)
                    
        vencedor_encontrado = False
        primeiro_a_acertar = None
        for jogador_id, resposta_cliente in respostas.items():
            if resposta_cliente.lower() == resposta_correta.lower():
                if not vencedor_encontrado:
                    pontuacoes[jogador_id] += 1  # Atribuir ponto ao jogador que acertou
                    enviar_uma_mensagem(jogadores[jogador_id], "Correto! Você ganhou o ponto.")
                    enviar_para_todos(server, f"Jogador {jogador_id} acertou a questão!")
                    vencedor_encontrado = True
                    primeiro_a_acertar = jogador_id
                else:
                    enviar_uma_mensagem(jogadores[jogador_id], f"Você acertou, mas o Jogador {primeiro_a_acertar} respondeu primeiro e ganhou o ponto.")
            else:
                enviar_uma_mensagem(jogadores[jogador_id], "Incorreto. Aguardando a próxima pergunta.")
        
        # Dar uma pequena pausa antes de enviar a próxima pergunta
        time.sleep(3)

if __name__ == "__main__":
    servidor()
    enviar_mensagem_final()
