def loading(*args):
    print(*args, end=" ")


def error(*args):
    print("\033[91m")
    print(*args, end="")
    print("\033[0m")


def done():
    print("\033[92m" + "DONE" + "\033[0m")