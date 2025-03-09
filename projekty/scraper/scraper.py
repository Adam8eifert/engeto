"""
projekt_3.py: třetí projekt do Engeto Online Python Akademie

autor: Adam Seifert
email: seifert.promotion@gmail.com
upraveno pro zpracování detailní stránky obce
"""
import sys
import csv
import requests
from bs4 import BeautifulSoup
import time
import re

def zkontroluj_argumenty():
    """
    Zkontroluje správnost vstupních argumentů programu.
    
    Returns:
        tuple: dvojice (url, vystupni_soubor) pokud jsou argumenty v pořádku
    """
    if len(sys.argv) != 3:
        print("ERROR: Program vyžaduje přesně 2 argumenty!")
        print("Použití: python scraper.py <url_adresa> <vystupni_soubor.csv>")
        sys.exit(1)
    
    url = sys.argv[1]
    vystupni_soubor = sys.argv[2]
    
    # Kontrola, zda URL začíná správně - nyní akceptuje i www variantu
    if not (url.startswith("https://volby.cz/pls/ps2017nss/") or url.startswith("https://www.volby.cz/pls/ps2017nss/")):
        print("ERROR: URL adresa musí být z webu volby.cz!")
        sys.exit(1)
        
    # Kontrola, zda výstupní soubor má příponu .csv
    if not vystupni_soubor.endswith(".csv"):
        print("ERROR: Výstupní soubor musí mít příponu .csv!")
        sys.exit(1)
        
    return url, vystupni_soubor

def je_detailni_stranka(url):
    """
    Zjistí, zda je zadaná URL adresa detailní stránkou obce.
    
    Args:
        url (str): URL adresa stránky
        
    Returns:
        bool: True pokud jde o detailní stránku obce, False pokud jde o přehledovou stránku
    """
    return '&xobec=' in url

def ziskej_kod_a_nazev_obce_z_url(url):
    """
    Získá kód a název obce z detailní URL adresy.
    
    Args:
        url (str): URL adresa detailní stránky obce
        
    Returns:
        tuple: (kod_obce, nazev_obce, url)
    """
    try:
        # Získáme kód obce z URL
        kod_obce_match = re.search(r'xobec=(\d+)', url)
        if kod_obce_match:
            kod_obce = kod_obce_match.group(1)
        else:
            kod_obce = "NEZNAMY"
        
        # Stáhneme stránku a získáme název obce z titulku
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Zkusíme najít název obce v nadpisu
        h3_tag = soup.find('h3')
        if h3_tag:
            nazev_obce = h3_tag.text.strip().split(':')[-1].strip()
        else:
            # Zkusíme alternativní způsob
            title_tag = soup.find('title')
            if title_tag:
                nazev_obce = title_tag.text.strip().split('-')[-1].strip()
            else:
                nazev_obce = "Neznámá obec"
        
        return kod_obce, nazev_obce, url
        
    except Exception as e:
        print(f"ERROR: Nepodařilo se získat informace o obci z URL: {e}")
        sys.exit(1)

def ziskej_odkazy_obci(url):
    """
    Získá odkazy na jednotlivé obce z přehledové stránky.
    
    Args:
        url (str): URL adresa přehledové stránky volebních výsledků
        
    Returns:
        dict: slovník s kódy obcí jako klíči a názvy obcí a odkazy jako hodnotami
    """
    # Pokud jde o detailní stránku obce, vrátíme informace pro tuto obec
    if je_detailni_stranka(url):
        kod_obce, nazev_obce, odkaz_url = ziskej_kod_a_nazev_obce_z_url(url)
        obce = {
            kod_obce: {
                'nazev': nazev_obce,
                'url': odkaz_url
            }
        }
        return obce
    
    # Jinak pokračujeme standardně s přehledovou stránkou
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
    print(f"Stahuji data pro obec {obec_info['nazev']} z: {url}")
    
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Nepodařilo se stáhnout data pro obec {obec_info['nazev']}: {e}")
        return None
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Získáme základní údaje o volbách v obci
    zakladni_udaje = {}
    
    # Najdeme tabulku s volebními údaji - hledáme podle textu "Voliči v seznamu"
    for table in soup.find_all('table'):
        if "Voliči v seznamu" in table.text:
            rows = table.find_all('tr')
            for row in rows:
                headers = row.find_all('th')
                cells = row.find_all('td')
                
                if len(cells) >= 3 and any("Voliči v seznamu" in h.text for h in headers):
                    zakladni_udaje['registrovani'] = cells[0].text.strip().replace('\xa0', '')
                    zakladni_udaje['vydane_obalky'] = cells[1].text.strip().replace('\xa0', '')
                    zakladni_udaje['platne_hlasy'] = cells[2].text.strip().replace('\xa0', '')
                    break
    
    # Najdeme údaje o stranách
    strany = {}
    for table in soup.find_all('table'):
        # Hledáme tabulky s výsledky stran - ty mají charakteristický formát
        rows = table.find_all('tr')
        for row in rows:
            cells = row.find_all('td')
            # Hledáme řádky, kde první buňka obsahuje číslo (číslo strany)
            if len(cells) >= 3 and cells[0].text.strip() and cells[0].text.strip().isdigit():
                try:
                    cislo_strany = cells[0].text.strip()
                    nazev_strany = cells[1].text.strip()
                    hlasy = cells[2].text.strip().replace('\xa0', '')
                    
                    if nazev_strany and hlasy:
                        strany[nazev_strany] = hlasy
                except Exception as e:
                    print(f"Chyba při zpracování strany: {e}")
    
    # Sestavíme kompletní výsledek
    vysledek = {
        'kod': kod_obce,
        'nazev': obec_info['nazev'],
        'registrovani': zakladni_udaje.get('registrovani', ''),
        'vydane_obalky': zakladni_udaje.get('vydane_obalky', ''),
        'platne_hlasy': zakladni_udaje.get('platne_hlasy', ''),
        'strany': strany
    }
    
    # Debug: vypíšeme základní výsledky
    print(f"Registrovaní voliči: {vysledek['registrovani']}")
    print(f"Vydané obálky: {vysledek['vydane_obalky']}")
    print(f"Platné hlasy: {vysledek['platne_hlasy']}")
    print(f"Počet stran: {len(strany)}")
    
    return vysledek


def uloz_do_csv(obce_data, vystupni_soubor):
    """
    Uloží získaná data do CSV souboru optimalizovaného pro Excel a odpovídající požadovanému formátu.

    Args:
        obce_data (list): Seznam slovníků s daty obcí.
        vystupni_soubor (str): Název výstupního CSV souboru.
    """
    if not obce_data:
        print("ERROR: Žádná data k uložení!")
        return False

    try:
        # Seznam všech politických stran (pro hlavičku CSV)
        vsechny_strany = set()
        for obec in obce_data:
            vsechny_strany.update(obec.get('strany', {}).keys())
        vsechny_strany = sorted(vsechny_strany)

        # Připravíme hlavičku v češtině
        header = ['Kód obce', 'Název obce', 'Voliči v seznamu', 'Vydané obálky', 'Platné hlasy']
        header.extend(vsechny_strany)

        # Otevřeme soubor s kódováním utf-8-sig (Excel-friendly)
        with open(vystupni_soubor, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(header)

            for obec in obce_data:
                row = [
                    obec['kod'],
                    obec['nazev'],
                    obec['registrovani'].replace('\xa0', '').replace(' ', ''),  # Odstraníme mezery v číslech
                    obec['vydane_obalky'].replace('\xa0', '').replace(' ', ''),
                    obec['platne_hlasy'].replace('\xa0', '').replace(' ', '')
                ]
                
                # Přidáme hlasy pro jednotlivé strany, pokud nejsou, dáme 0
                for strana in vsechny_strany:
                    row.append(obec.get('strany', {}).get(strana, '0').replace('\xa0', '').replace(' ', ''))
                
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
        print(f"Zpracovávám obec {counter}/{len(obce)}: {obec_info['nazev']} ({kod_obce})")
        
        obec_data = ziskej_data_obce(kod_obce, obec_info)
        if obec_data:
            obce_data.append(obec_data)
        
        # Krátké zpoždění mezi požadavky, abychom nezahltili server
        time.sleep(0.1)
    
    # Uložíme data do CSV
    uloz_do_csv(obce_data, vystupni_soubor)

if __name__ == "__main__":
    main()