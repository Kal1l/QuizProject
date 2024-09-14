import multiprocessing
import subprocess
import time
import client_script

def server(questions, answers, scores, event, input_queue):
    # Server process
    for i, question in enumerate(questions):
        print(f"\nWaiting for answers to Question {i+1}")
        time.sleep(1)  # Simulate some delay before processing the answer
        
        # Wait until a client answers correctly
        while True:
            for j, answer in enumerate(answers):
                if answer.value.decode().strip() == question["correct_answer"] and scores[j].value < 2:
                    scores[j].value += 1
                    print(f"Player {j+1} answered correctly!")
                    event.set()  # Signal that the question has been answered correctly
                    time.sleep(1)  # Give clients time to process the event
                    break
            if event.is_set():
                break
        event.clear()  # Clear the event for the next question

        # Check if any player has reached 2 points
        if any(score.value >= 2 for score in scores):
            print("Game over!")
            break

if __name__ == "__main__":
    # Number of players
    num_players = 3  # Change this value to set the number of players

    # Shared memory variables
    questions = [
        {"question": "What is the capital of France?", "correct_answer": "Paris"},
        {"question": "What is the largest planet in our solar system?", "correct_answer": "Jupiter"},
        {"question": "What is the color of the sky?", "correct_answer": "Blue"},
        {"question": "What is the symbol for the element Oxygen?", "correct_answer": "O"},
        {"question": "What is the square root of 16?", "correct_answer": "4"},
    ]
    answers = [multiprocessing.Array('c', 100) for _ in range(num_players)]  # Ensure answers list matches number of players
    scores = [multiprocessing.Value('i', 0) for _ in range(num_players)]  # Integer scores for each player

    # Create a queue for user input
    input_queue = multiprocessing.Queue()

    # Create a manager to handle shared objects
    manager = multiprocessing.Manager()
    event = manager.Event()  # Create an event to signal when a question is answered correctly

    # Create server and client processes
    server_process = multiprocessing.Process(target=server, args=(questions, answers, scores, event, input_queue))
    client_processes = [multiprocessing.Process(target=client_script.client, args=(questions, answers[i], input_queue, event)) for i in range(num_players)]

    # Start server process
    server_process.start()

    # Open a new terminal for each client process
    for i, p in enumerate(client_processes):
        subprocess.Popen(['start', 'cmd', '/k', 'python', 'client_script.py', str(i)], shell=True)

    # Wait for the terminals to open
    time.sleep(2)

    # Wait for the event to be set before moving on to the next question
    for question in questions:
        event.wait()  # Wait until the question is answered correctly
        event.clear()  # Clear the event for the next question

    # Wait for server and client processes to finish
    server_process.join()
    for p in client_processes:
        p.join()