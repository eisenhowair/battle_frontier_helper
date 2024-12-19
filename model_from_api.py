import json
from bs4 import BeautifulSoup
from tqdm import tqdm
import re
import requests
from unidecode import unidecode
import pandas as pd
from dictionaries_convert import *

from concurrent.futures import ThreadPoolExecutor, as_completed


def get_html_from_json(content):

    json_content = content.json()
    html_content = json_content["parse"]["text"]["*"]
    return html_content


def get_move_info(move_name: str):
    """
    Récupère la puissance (Power), la précision (Accuracy) et la catégorie (Category)
    d'une attaque Pokémon sur Bulbapedia.

    Args:
        move_name (str): Le nom de l'attaque Pokémon.

    Returns:
        dict: Contenant 'Power', 'Accuracy' et 'Category' de l'attaque.
    """

    if move_name == "Softboiled":
        move_name = "Soft-Boiled"

    url = f"https://bulbapedia.bulbagarden.net/w/api.php?action=parse&format=json&page={move_name}_(move)&section=0"

    try:
        # Requête GET pour récupérer la page
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception(f"Erreur: Page non trouvée pour l'attaque '{move_name}'.")

        # Extraire le contenu HTML
        html_content = get_html_from_json(response)
        soup = BeautifulSoup(html_content, "html.parser")

        # Rechercher tous les tableaux dans la page
        tables = soup.find_all("table")

        stats = {"Power": None, "Accuracy": None, "Category": None}

        # Parcourir chaque tableau pour trouver les valeurs de "Power", "Accuracy" et "Category"
        for table in tables:
            for row in table.find_all("tr"):
                header = row.find("th")
                value = row.find("td")

                if header and value:
                    header_text = header.get_text(strip=True)
                    value_text = value.get_text(strip=True)

                    if "Power" in header_text:
                        power_match = re.search(r"(\d+)", value_text)
                        stats["Power"] = power_match.group(1) if power_match else None

                    elif "Accuracy" in header_text:
                        accuracy_match = re.search(r"(\d+)%?", value_text)
                        stats["Accuracy"] = (
                            accuracy_match.group(1) if accuracy_match else None
                        )

                    # fetch the "modern" category, so won't work in a 3rd gen context for the phys/special part
                    elif "Category" in header_text:
                        category = value.get_text(strip=True)
                        stats["Category"] = category

        if stats["Power"] or stats["Accuracy"] or stats["Category"]:
            return stats
        else:
            raise ValueError(
                f"Statistiques 'Power', 'Accuracy' ou 'Category' non trouvées pour le move {move_name}."
            )

    except Exception as e:
        print(f"Erreur : {e}")
        return None


# Extraire la partie texte contenant les informations
def traite_reponse(json_response):

    soup = BeautifulSoup(get_html_from_json(json_response), "html.parser")
    spans = soup.find_all("span", style=lambda s: s and "display:inline-block;" in s)

    if len(spans) == 0:
        return -1

    types_data = []

    # Parcourir les spans avec tqdm pour afficher une barre de progression
    for idx, span in enumerate(tqdm(spans, desc="Processing spans")):
        if (
            idx < 19
        ):  # parce que pour certains pokemons il récupère aussi les faiblesses des formes Méga
            try:
                table = span.find("table")
                if not table:
                    # print(f"Ignoré (table non trouvée dans span à l'indice {idx})")
                    continue
                # print(table)

                # Extraire la couleur de fond de la table
                style = table.get("style", "")
                color_match = re.search(r"background:\s*(#?[0-9A-Fa-f]{6})", style)
                if not color_match:
                    continue
                color = color_match.group(1)

                # Trouver le nom du type dans l'élément a
                a_tag = span.find("a", title=lambda s: s and "type)" in s)
                if not a_tag:
                    continue
                type_name = a_tag.get_text().strip()

                # Trouver le multiplicateur de dégâts dans le second td
                tds = span.find_all("td")
                if len(tds) < 2:
                    # print(f"Ignoré (multiplicateur non trouvé dans span à l'indice {idx})")
                    continue
                damage_text = tds[1].get_text().strip()

                # Convertir le multiplicateur de dégâts en float
                if "½" in damage_text:
                    damage = 0.5
                elif "¼" in damage_text:
                    damage = 0.25
                elif "x" in damage_text:
                    damage = float(damage_text.replace("x", ""))
                elif "×" in damage_text:
                    damage = float(damage_text.replace("×", ""))
                else:
                    damage = float(damage_text)

                # Ajouter les données à la liste
                types_data.append(
                    {"name": type_name, "damage_multiplier": damage, "color": color}
                )

            except Exception as e:
                print(f"Erreur à l'indice {idx} : {e}")

    # Afficher les résultats
    return json.dumps(types_data, indent=4, ensure_ascii=False)


def get_weakness(name: str, num_section: int = 15):

    url = f"https://bulbapedia.bulbagarden.net/w/api.php?action=parse&format=json&page={name}_(Pok%C3%A9mon)&section={num_section}"

    try:
        # Make a GET request to the API endpoint using requests.get()
        response = requests.get(url)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            return traite_reponse(response)
        else:
            print("Error:", response.status_code)
            return None
    except requests.exceptions.RequestException as e:

        # Handle any network-related errors or exceptions
        print("Error:", e)
        return None


from typing import Dict, List, Tuple, Union


def translate_name(name_fr: str) -> Union[Tuple[str, List[str]], str]:
    """
    Traduit le nom français d'un Pokémon en anglais et récupère ses types.

    Args:
        name_fr (str): Le nom français du Pokémon

    Returns:
        Union[Tuple[str, List[str]], str]: Un tuple contenant le nom anglais et la liste des types,
        ou un message d'erreur si la requête échoue
    """
    name_fr = unidecode(name_fr)  # pour normaliser le nom et enlever les accents
    url = f"https://tyradex.vercel.app/api/v1/pokemon/{name_fr}"

    try:
        # Faire une requête GET à l'API
        response = requests.get(url)

        # Vérifier si la requête a réussi
        if response.status_code == 200:
            # Convertir la réponse JSON en dictionnaire Python
            pokemon_data = response.json()

            # Extraire le nom anglais et les types
            english_name = pokemon_data.get("name", {}).get("en")
            types = [type_info["name"] for type_info in pokemon_data.get("types", [])]

            if english_name and types:
                return english_name, types
            else:
                return f"Erreur : Données incomplètes pour '{name_fr}'."
        else:
            return f"Erreur : Impossible de récupérer les informations pour '{name_fr}'. Code d'erreur : {response.status_code}"

    except requests.exceptions.RequestException as e:
        return f"Erreur de connexion : {str(e)}"


def traite_sets(html_response: str, pkmn_name: str = "Suicune"):
    """
    Traite plusieurs sets de mouvements (moves) pour un Pokémon spécifique.
    :param html_response: Le contenu HTML à analyser.
    :param pkmn_name: Le nom du Pokémon (par exemple, "Latios").
    :return: Une liste d'objets contenant les informations des movesets (moves, nature, evs et object).
    """
    if html_response is None:
        local_html_path = "battle_frontier_sets.html"
        with open(local_html_path, "r", encoding="utf-8") as fichier:
            html_response = fichier.read()
    soup = BeautifulSoup(html_response, "html.parser")

    sets = []

    # Rechercher tous les éléments <tr> qui contiennent des sets
    set_rows = soup.find_all("tr", style=lambda s: s and "text-align:center" in s)

    for set_row in set_rows:
        # Liste pour stocker les mouvements du set actuel
        moves = []
        evs = []
        nature = ""
        held_object = ""

        # Rechercher le nom du Pokémon dans la ligne
        pokemon_element = set_row.find("a", title=lambda t: t and "(Pokémon)" in t)

        if pokemon_element:
            pokemon_name = ""  # Initialise la variable
            if pokemon_element.get("title"):  # Si on trouve un attribut title
                pokemon_name = pokemon_element.get(
                    "title"
                )  # On récupère la valeur de l'attribut title

            elif pokemon_element.find("img"):  # Si on trouve une image
                img_element = pokemon_element.find("img")
                if img_element.get("alt"):  # Si l'image a un attribut alt
                    pokemon_name = img_element.get(
                        "alt"
                    )  # on récupère la valeur de l'attribut alt

            pokemon_name = (
                pokemon_name.replace("(Pokémon)", "").strip().lower()
            )  # On enleve (Pokémon) et on met en minuscule.

            if pkmn_name.lower() == pokemon_name:
                # Rechercher tous les éléments <th> qui contiennent les mouvements
                move_elements = set_row.find_all("th")
                for move_element in move_elements:
                    # Extraire le nom du mouvement
                    move_name = move_element.get_text(strip=True)
                    move_name = re.sub(r"([^ -])([A-Z])", r"\1 \2", move_name)
                    if (
                        move_name == "Return"
                    ):  # comme uniquement la Factory nous intéresse
                        move_name = "Frustration"
                    # pour rajouter un espace lorsque les mots sont collés

                    # Extraire la couleur de fond (background)
                    background_color = (
                        move_element.get("style", "")
                        .split("background:")[-1]
                        .split(";")[0]
                        .strip()
                    )
                    # Ajouter le mouvement à la liste du set actuel
                    if move_name:  # Vérifier que le mouvement n'est pas vide
                        moves.append(
                            {
                                "move_name": move_name,
                                "background_color": background_color,
                            }
                        )

                        # print(move_name)

                all_tds = set_row.find_all("td")
                if len(all_tds) >= 4:
                    fourth_td = all_tds[
                        3
                    ]  # Index 3 car les listes Python commencent à 0
                    item_text = fourth_td.get_text(strip=True)
                    held_object = item_text
                else:
                    print("Moins de 4 colonnes dans cette ligne.")

                # Extraire la nature et les EVs
                td_elements = set_row.find_all("td")
                for i, td_element in enumerate(td_elements):
                    if i == len(td_elements) - 7:  # La nature est le 7e td avant la fin
                        nature = td_element.get_text(strip=True)
                    elif i > len(td_elements) - 7:  # Les EVs sont les 6 derniers TDs
                        ev = td_element.get_text(strip=True)
                        evs.append(int(ev) if ev != "-" else 0)

                # Ajouter le set de mouvements à la liste des sets
                if moves:
                    stat_line = find_level_100_stats(
                        species_name=pkmn_name,
                        move1=moves[0]["move_name"],
                        move2=moves[1]["move_name"],
                        move3=moves[2]["move_name"],
                        move4=moves[3]["move_name"],
                    )
                    sets.append(
                        {
                            "stats": stat_line,
                            "moves": moves,
                            "nature": nature,
                            "evs": evs,
                            "held_object": held_object,
                        }
                    )
    return sets


def get_sets(pkmn_name: str, num_set: int = -1, mode: str = "api"):

    if mode == "api":
        url = f"https://bulbapedia.bulbagarden.net/w/api.php?action=parse&format=json&page=List_of_Battle_Frontier_Pok%C3%A9mon_in_Generation_III"

        # Faire une requête GET à l'API
        response = requests.get(url)

        # Vérifier si la requête a réussi
        if response.status_code == 200:
            # Convertir la réponse JSON en dictionnaire Python
            sets_data = traite_sets(
                html_response=get_html_from_json(response), pkmn_name=pkmn_name
            )
        else:
            return f"Erreur : Impossible de récupérer les sets. Code d'erreur : {response.status_code}"

    elif mode == "local":

        sets_data = traite_sets(html_response=None, pkmn_name=pkmn_name)

    return sets_data


def find_valid_section(name: str, sections_to_try: list):
    """
    Lance plusieurs appels à get_weakness en parallèle pour tester plusieurs sections.
    Retourne la première réponse valide.
    """
    with ThreadPoolExecutor() as executor:
        # Créer un dictionnaire {future: num_section} pour suivre chaque tâche
        futures = {
            executor.submit(get_weakness, name, section): section
            for section in sections_to_try
        }

        for future in as_completed(futures):
            result = future.result()
            if result != -1:  # Si une réponse valide est trouvée
                # print(f"Section {futures[future]} valide!")
                return result

    print("Aucune section valide trouvée.")
    return -1


def get_complete_infos(name_fr: str, num_section: int = 10):

    name_en = translate_name(name_fr)
    # print(f"Nom anglais: {name_en}\n")

    type_sensitivity = get_weakness(name_en)
    while type_sensitivity == -1:
        # print(f"Not found in section {num_section}\n")
        num_section += 1
        # print(f"Now looking in section {num_section}...\n")
        type_sensitivity = get_weakness(name=name_en, num_section=num_section)
    all_sets = get_sets(pkmn_name=name_en)

    return json.loads(type_sensitivity), all_sets, name_en, name_fr


def get_complete_infos_thread(name_fr: str):

    name_en, types = translate_name(name_fr)
    print(f"Nom anglais: {name_en}\n")
    print(types)
    print(type(types))

    sections_to_test = range(10, 21)  # Tester les sections de 12 à 19

    type_sensitivity = find_valid_section(name_en, sections_to_test)

    all_sets = get_sets(pkmn_name=name_en)

    return json.loads(type_sensitivity), all_sets, name_en, name_fr, types


def find_level_100_stats(species_name, move1, move2, move3, move4):
    # Charger le fichier Excel
    file_path = "EmeraldBattleFrontierComplete.xlsx"
    df = pd.read_excel(file_path)

    # Filtrer les lignes où la colonne "Species" correspond au nom donné
    filtered_df = df[df["Species"] == species_name]

    # Vérifier si les 4 mouvements correspondent
    filtered_df = filtered_df[
        (filtered_df["Move 1"] == move1)
        & (filtered_df["Move 2"] == move2)
        & (filtered_df["Move 3"] == move3)
        & (filtered_df["Move 4"] == move4)
    ]

    # Si une ligne correspond, retourner la valeur de "Level 100 stats"
    if not filtered_df.empty:
        brut_stat_list = filtered_df.iloc[0]["Level 100 stats"]
        stats_list = list(map(int, brut_stat_list.split("/")))
        return stats_list

    else:
        return None  # Aucune correspondance trouvée


def main():

    name = input("Entrez nom:\n")

    weaknesses, builds, _, _, types = get_complete_infos_thread(name_fr=name)
    print(type(weaknesses))
    # print(get_move_info(name))
    # print(*builds, sep="\n")


if __name__ == "__main__":
    main()
