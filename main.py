from src.assistant import Assistant


def main():
    assistant = Assistant()
    answer = assistant.start()
    while answer:
        message = input(answer)
        answer = assistant.next(message)

if __name__ == '__main__':
    main()