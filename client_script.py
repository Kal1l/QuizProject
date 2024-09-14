import sys
import multiprocessing

def client(questions, answer, input_queue, event):
    # Client process
    for question in questions:
        print(f"\nQuestion: {question['question']}")
        user_answer = input("Your answer: ")
        answer.value = user_answer.encode()
        event.set()  # Signal that the answer has been submitted
        event.wait()  # Wait for the event to be cleared before moving to the next question
        event.clear()

if __name__ == "__main__":
    # Get the client index from the command line arguments
    client_index = int(sys.argv[1])

    # Shared memory variables (these should be passed or created appropriately)
    questions = [
        {"question": "What is the capital of France?", "correct_answer": "Paris"},
        {"question": "What is the largest planet in our solar system?", "correct_answer": "Jupiter"},
        {"question": "What is the color of the sky?", "correct_answer": "Blue"},
        {"question": "What is the symbol for the element Oxygen?", "correct_answer": "O"},
        {"question": "What is the square root of 16?", "correct_answer": "4"},
    ]
    answers = [multiprocessing.Array('c', 100) for _ in range(len(questions))]
    input_queue = multiprocessing.Queue()
    manager = multiprocessing.Manager()
    event = manager.Event()  # Create an event to signal when a question is answered correctly

    # Run the client process
    client(questions, answers[client_index], input_queue, event)