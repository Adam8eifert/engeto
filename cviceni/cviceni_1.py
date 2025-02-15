def zapisovac(text, filename="jazyky.txt"):
    with open(filename, mode="w") as file:
        file.write(text)
    return text

zapisovac(f'Python,\nScala,\nJavaScript,\nJava.')


    