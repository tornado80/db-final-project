def loading(*args):
    print(*args, end=" ")


def done():
    print("\033[92m" + "DONE" + "\033[0m")