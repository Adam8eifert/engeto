import sys
import csv
import requests
from bs4 import BeautifulSoup
import time
import re
import os

def zkontroluj_argumenty():
    """Kontrola vstupních argumentů"""
    if len(sys.argv) != 3:
        print("Chyba: Program vyžaduje 2 argumenty - URL a výstupní soubor!")
        print("Použití: python main.py <url> <výstup.csv>")
        sys.exit(1)

    url = sys.argv[1]
    vystup = sys.argv[2]

    if not any(url.startswith(base) for base in (
        "https://volby.cz/pls/ps2017nss/",
        "https://www.volby.cz/pls/ps2017nss/"
    )):
        print("Chyba: Neplatná URL adresa. Musí být z volby.cz!")
        sys.exit(1)

    if not vystup.endswith('.csv'):
        print("Chyba: Výstupní soubor musí mít příponu .csv!")
        sys.exit(1)

    return url, vystup

def nacti_stranky(url):
    """Načte obsah stránky s kontrolou chyb"""
    try:
        print(f"Stahuji hlavní stránku: {url}")
        response = requests.get(url)
        response.raise_for_status()
        return BeautifulSoup(response.text, 'html.parser')
    except Exception as e:
        print(f"Chyba při načítání stránky: {e}")
        sys.exit(1)

def najdi_obce(soup):
    """Hledá seznam obcí v HTML struktuře"""
    print("Hledám data obcí...")
    obce = {}
    
    for table in soup.find_all('table'):
        for row in table.find_all('tr'):
            cells = row.find_all('td')
            if len(cells) < 3:
                continue

            # Zpracování buněk s obcemi
            if cells[0].find('a') and cells[1].text.strip():
                kod = cells[0].text.strip()
                nazev = cells[1].text.strip()
                link = cells[0].find('a')['href']
                
                obce[kod] = {
                    'nazev': nazev,
                    'url': f"https://volby.cz/pls/ps2017nss/{link}"
                }
                print(f"Nalezena obec: {nazev} ({kod})")

    if not obce:
        print("Varování: Nebyly nalezeny žádné obce!")
        return None
    
    print(f"Celkem nalezeno obcí: {len(obce)}")
    return obce

def zpracuj_obec(obec_info):
    """Získává detailní data pro jednotlivou obec"""
    print(f"\nZpracovávám obec: {obec_info['nazev']}")
    try:
        response = requests.get(obec_info['url'])
        soup = BeautifulSoup(response.text, 'html.parser')
    except Exception as e:
        print(f"Chyba při načítání obce: {e}")
        return None

    # Získání základních údajů
    data = {
        'registrovani': '0',
        'vydane_obalky': '0', 
        'platne_hlasy': '0',
        'strany': {}
    }

    # Hledání tabulky s voliči
    for table in soup.find_all('table'):
        if "Voliči v seznamu" in table.text:
            for row in table.find_all('tr'):
                cells = row.find_all('td')
                if len(cells) >= 3:
                    data['registrovani'] = cells[0].text.replace('\xa0', '')
                    data['vydane_obalky'] = cells[1].text.replace('\xa0', '')
                    data['platne_hlasy'] = cells[2].text.replace('\xa0', '')
                    break

    # Hledání výsledků stran
    for table in soup.find_all('table'):
        for row in table.find_all('tr'):
            cells = row.find_all('td')
            if len(cells) >= 3 and cells[0].text.strip().isdigit():
                nazev_strany = cells[1].text.strip()
                hlasy = cells[2].text.replace('\xa0', '').strip()
                if nazev_strany and hlasy:
                    data['strany'][nazev_strany] = hlasy

    print(f"Data pro {obec_info['nazev']} úspěšně získána")
    return data

def uloz_data(obce_data, soubor):
    """Ukládá data do CSV formátu"""
    if not obce_data:
        print("Chyba: Žádná data k uložení!")
        return False

    try:
        # Příprava hlavičky
        vsechny_strany = set()
        for data in obce_data.values():
            vsechny_strany.update(data['strany'].keys())
        vsechny_strany = sorted(vsechny_strany)

        with open(soubor, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f, delimiter=';')
            header = ['Kód', 'Obec', 'Voliči', 'Obálky', 'Platné hlasy'] + vsechny_strany
            writer.writerow(header)

            for kod, data in obce_data.items():
                radek = [
                    kod,
                    data['nazev'],
                    data['registrovani'],
                    data['vydane_obalky'],
                    data['platne_hlasy']
                ]
                radek += [data['strany'].get(strana, '0') for strana in vsechny_strany]
                writer.writerow(radek)

        print(f"\nData úspěšně uložena do: {os.path.abspath(soubor)}")
        return True

    except Exception as e:
        print(f"Chyba při ukládání: {e}")
        return False

def main():
    url, vystup = zkontroluj_argumenty()
    soup = nacti_stranky(url)
    
    obce = najdi_obce(soup)
    if not obce:
        print("Konec programu - žádná data")
        sys.exit(1)

    results = {}
    celkem = len(obce)
    
    for i, (kod, info) in enumerate(obce.items(), 1):
        print(f"\n[{i}/{celkem}]", end=' ')
        data = zpracuj_obec(info)
        if data:
            results[kod] = {
                'nazev': info['nazev'],
                **data
            }
        time.sleep(0.2)

    if not uloz_data(results, vystup):
        sys.exit(1)

if __name__ == "__main__":
    main()