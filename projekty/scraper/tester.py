import requests

url = "https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=12&xnumnuts=7103"  # Zadejte URL stránky, jejíž kód chcete získat
response = requests.get(url)

if response.status_code == 200:
    print(response.text)  # Vypíše HTML kód stránky
else:
    print(f"Chyba při stahování stránky: {response.status_code}")    
    print("Program byl úspěšně dokončen.")

with open("stranka.html", "w", encoding="utf-8") as f:
    f.write(response.text)