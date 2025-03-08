import sys
import requests
from bs4 import BeautifulSoup
import pandas as pd

BASE_URL = "https://www.volby.cz/pls/ps2017nss/"

def get_town_links(main_url):
    """Načte všechny odkazy na obce z dané stránky."""
    response = requests.get(main_url)
    soup = BeautifulSoup(response.text, "html.parser")
    table_links = soup.find_all("td", {"class": "cislo"})
    return [(link.a.text.strip(), BASE_URL + link.a["href"]) for link in table_links]

def get_town_results(town_url):
    """Scrapuje výsledky pro jednu obec."""
    response = requests.get(town_url)
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Název obce
    town_name = soup.find("h3").text.strip()
    
    # Počet voličů, vydané obálky, platné hlasy
    summary_table = soup.find_all("table")[0]
    tds = summary_table.find_all("td", {"class": "cislo"})
    voters, envelopes, valid_votes = tds[0].text.strip(), tds[1].text.strip(), tds[4].text.strip()
    
    # Strany a jejich hlasy
    parties_table = soup.find_all("table")[1]
    party_data = {}
    for row in parties_table.find_all("tr")[2:]:
        cols = row.find_all("td")
        if len(cols) >= 2:
            party_name = cols[1].text.strip()
            votes = cols[-1].text.strip()
            party_data[party_name] = votes
    
    return [town_name, voters, envelopes, valid_votes, party_data]

def main():
    if len(sys.argv) != 3:
        print("Použití: python main.py <URL_kraje> <výstupní_soubor.csv>")
        sys.exit(1)
    
    kraj_url, output_file = sys.argv[1], sys.argv[2]
    towns = get_town_links(kraj_url)
    
    all_parties = set()
    results = []
    
    for town_id, town_url in towns:
        town_name, voters, envelopes, valid_votes, party_data = get_town_results(town_url)
        all_parties.update(party_data.keys())
        results.append([town_id, town_name, voters, envelopes, valid_votes, party_data])
    
    # DataFrame s dynamickými sloupci pro strany
    columns = ["Kód obce", "Název obce", "Voliči", "Vydané obálky", "Platné hlasy"] + sorted(all_parties)
    df = pd.DataFrame(columns=columns)
    
    for town_id, town_name, voters, envelopes, valid_votes, party_data in results:
        row = {"Kód obce": town_id, "Název obce": town_name, "Voliči": voters, "Vydané obálky": envelopes, "Platné hlasy": valid_votes}
        row.update(party_data)
        df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)

    df.to_csv("vysledky.csv", sep=";", index=False, encoding="utf-8")
    print(f"✅ Výsledky uloženy do {output_file}")

if __name__ == "__main__":
    main()
