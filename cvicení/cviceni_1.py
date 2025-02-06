def deleni(a, b):
    try:
        a = int(input("Zadejte číslo a: "))
        b = int(input("Zadejte číslo b: "))
    except ValueError:
        print("Zadali jste neplatné číslo")
    except ZeroDivisionError:
        print("Nulou nelze dělit")
    else:
        print("zadna vyjimka")
    finally:
        print("toto se provede vzdy")


    return a / b

print(deleni(1, 2))
