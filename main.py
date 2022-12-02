from src.assistant import Assistant
import os

def main():
    assistant = Assistant()
    answer = assistant.start()
    while answer:
        message = input(answer)
        answer = assistant.next(message)

if __name__ == '__main__':
    main()