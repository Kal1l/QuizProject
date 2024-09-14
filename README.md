<h1>Issues</h1>
<h3>Question Delivery</h3> Server sends questions to clients, but this feature needs improvement. The server should exclusively handle question management and delivery to clients.
<h3>Win Condition & Scoring</h3> Functionality is in place and operational.

<h3>Multi-Player Support</h3> Multiple players can participate.

<h3>Client Synchronization</h3>Currently, synchronization is not optimal. Clients progress to the next question only after their individual answers, rather than waiting for any player to provide a correct answer.

<h3>Client Answer Handling</h3> Each client can currently answer only once per question. The system should be updated to allow multiple attempts per client, with the game advancing to the next question once any player answers correctly.

## Todo List
Servidor:
- [ ] Banco de perguntas(como vai ser definido?) 
- [ ] Randomizador de perguntas
- [x] Mandar as perguntas aos clientes
- [ ] Receber as respostas
- [ ] Interpretador de respostas
- [ ] Sincronização para enviar as perguntas e receber as respostas
- [X] Atribuir ponto ao cliente
- [X] Condição de fim de jogo
Cliente:
- [ ] Atribuir nome
- [X] Ligar com o servidor
- [X] Receber as perguntas
- [X] Responder as perguntas
- [ ] Sincronização do tempo de respostas
