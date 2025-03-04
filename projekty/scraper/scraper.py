"""
projekt_3.py: třetí projekt do Engeto Online Python Akademie

autor: Adam Seifert
email: seifert.promotion@gmail.com
"""
import sys
import os
import csv
import requests
from bs4 import BeautifulSoup
import time

def zkontroluj_argumenty():
    """
    Zkontroluje správnost vstupních argumentů programu.
    
    Returns:
        tuple: dvojice (url, vystupni_soubor) pokud jsou argumenty v pořádku
    """
    if len(sys.argv) != 3:
        print("ERROR: Program vyžaduje přesně 2 argumenty!")
        print("Použití: python main.py <url_adresa> <vystupni_soubor.csv>")
        sys.exit(1)
    
    url = sys.argv[1]
    vystupni_soubor = sys.argv[2]
    
    # Kontrola, zda URL začíná správně
    if not url.startswith("https://volby.cz/pls/ps2017nss/"):
        print("ERROR: URL adresa musí být z webu volby.cz!")
        sys.exit(1)
        
    # Kontrola, zda výstupní soubor má příponu .csv
    if not vystupni_soubor.endswith(".csv"):
        print("ERROR: Výstupní soubor musí mít příponu .csv!")
        sys.exit(1)
        
    return url, vystupni_soubor

def ziskej_odkazy_obci(url):
    """
    Získá odkazy na jednotlivé obce z přehledové stránky.
    
    Args:
        url (str): URL adresa přehledové stránky volebních výsledků
        
    Returns:
        dict: slovník s kódy obcí jako klíči a názvy obcí a odkazy jako hodnotami
    """
    try:
        print(f"Stahuji data z: {url}")
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Nepodařilo se stáhnout přehledovou stránku: {e}")
        sys.exit(1)
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Hledáme všechny tabulky
    tables = soup.find_all('table')
    
    # Procházíme všechny řádky ve všech tabulkách a hledáme odkazy na obce
    obce = {}
    
    for table in tables:
        rows = table.find_all('tr')
        for row in rows:
            cells = row.find_all('td')
            if len(cells) >= 3:
                # Pokud obsahuje odkaz na obec
                odkaz = cells[0].find('a')
                if odkaz and cells[1].text.strip():
                    kod_obce = cells[0].text.strip()
                    nazev_obce = cells[1].text.strip()
                    
                    # Sestavíme kompletní URL
                    odkaz_href = odkaz.get('href')
                    odkaz_url = f"https://volby.cz/pls/ps2017nss/{odkaz_href}"
                    
                    obce[kod_obce] = {
                        'nazev': nazev_obce,
                        'url': odkaz_url
                    }
    
    if not obce:
        print("ERROR: Nepodařilo se najít žádné obce na zadané URL adrese!")
        sys.exit(1)
    
    return obce

def ziskej_data_obce(kod_obce, obec_info):
    """
    Získá volební data pro konkrétní obec.
    
    Args:
        kod_obce (str): Kód obce
        obec_info (dict): Informace o obci (název a URL)
        
    Returns:
        dict: Slovník s volebními daty pro danou obec
    """
    url = obec_info['url']
    
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Nepodařilo se stáhnout data pro obec {obec_info['nazev']}: {e}")
        return None
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Získáme základní údaje o volbách v obci
    zakladni_udaje = {}
    
    try:
        # Hledáme volební účast - registrované voliče, vydané obálky a platné hlasy
        tables = soup.find_all('table')
        
        for table in tables:
            headers = [header.text.strip() for header in table.find_all('th')]
            
            if 'Voliči v seznamu' in headers:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) >= 3:
                        zakladni_udaje['registrovani'] = cells[3].text.strip().replace('\xa0', '')
                        zakladni_udaje['vydane_obalky'] = cells[4].text.strip().replace('\xa0', '')
                        zakladni_udaje['platne_hlasy'] = cells[7].text.strip().replace('\xa0', '')
                        break
        
        # Hledáme výsledky jednotlivých stran
        strany = {}
        
        # Prohledáváme všechny tabulky se stranami
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all('td')
                # Pokud řádek obsahuje jméno strany a počet hlasů
                if len(cells) >= 2:
                    # Hledáme řádky, které obsahují název strany a počet hlasů
                    nazev_bunka = row.find('td', {'class': 'overflow_name'})
                    hlasy_bunka = row.find('td', {'class': 'text-right'})
                    
                    if nazev_bunka and hlasy_bunka:
                        nazev_strany = nazev_bunka.text.strip()
                        hlasy = hlasy_bunka.text.strip().replace('\xa0', '')
                        
                        if nazev_strany and hlasy:
                            strany[nazev_strany] = hlasy
    except Exception as e:
        print(f"ERROR: Nepodařilo se zpracovat data pro obec {obec_info['nazev']}: {e}")
        return None
    
    # Sestavíme kompletní výsledek
    vysledek = {
        'kod': kod_obce,
        'nazev': obec_info['nazev'],
        'registrovani': zakladni_udaje.get('registrovani', ''),
        'vydane_obalky': zakladni_udaje.get('vydane_obalky', ''),
        'platne_hlasy': zakladni_udaje.get('platne_hlasy', ''),
        'strany': strany
    }
    
    return vysledek

def uloz_do_csv(obce_data, vystupni_soubor):
    """
    Uloží získaná data do CSV souboru.
    
    Args:
        obce_data (list): Seznam slovníků s daty obcí
        vystupni_soubor (str): Název výstupního CSV souboru
    """
    if not obce_data:
        print("ERROR: Žádná data k uložení!")
        return False
    
    # Získáme seznam všech stran (pro hlavičku CSV)
    vsechny_strany = set()
    for obec in obce_data:
        for strana in obec.get('strany', {}).keys():
            vsechny_strany.add(strana)
    
    # Seřadíme strany abecedně
    vsechny_strany = sorted(list(vsechny_strany))
    
    # Připravíme hlavičku
    header = ['kod', 'nazev', 'registrovani', 'vydane_obalky', 'platne_hlasy'] + vsechny_strany
    
    try:
        with open(vystupni_soubor, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(header)
            
            for obec in obce_data:
                row = [
                    obec['kod'],
                    obec['nazev'],
                    obec['registrovani'],
                    obec['vydane_obalky'],
                    obec['platne_hlasy']
                ]
                
                # Přidáme hlasy pro jednotlivé strany
                for strana in vsechny_strany:
                    row.append(obec.get('strany', {}).get(strana, '0'))
                
                writer.writerow(row)
        
        print(f"Data byla úspěšně uložena do souboru: {vystupni_soubor}")
        return True
    
    except Exception as e:
        print(f"ERROR: Nepodařilo se uložit data do souboru {vystupni_soubor}: {e}")
        return False

def main():
    """
    Hlavní funkce programu.
    """
    # Zkontrolujeme argumenty
    url, vystupni_soubor = zkontroluj_argumenty()
    
    # Získáme odkazy na obce
    obce = ziskej_odkazy_obci(url)
    
    print(f"Nalezeno {len(obce)} obcí.")
    
    # Získáme data pro každou obec
    obce_data = []
    counter = 0
    
    for kod_obce, obec_info in obce.items():
        counter += 1
        print(f"Stahuji data pro obec {counter}/{len(obce)}: {obec_info['nazev']} ({kod_obce})")
        
        obec_data = ziskej_data_obce(kod_obce, obec_info)
        if obec_data:
            obce_data.append(obec_data)
        
        # Krátké zpoždění mezi požadavky, abychom nezahltili server
        time.sleep(0.1)
    
    # Uložíme data do CSV
    uloz_do_csv(obce_data, vystupni_soubor)
    
    print("Program byl úspěšně dokončen.")

if __name__ == "__main__":
    main()
