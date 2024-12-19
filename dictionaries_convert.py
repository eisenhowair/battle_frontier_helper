def raccourci_nom_type(nom_type: str):
    type_mapping = {
        "Electric": "Elec",
        "Psychic": "Psy",
        "Fighting": "Fight",
    }  # pour raccourcir les noms de types

    type_name = type_mapping.get(
        nom_type, nom_type
    )  # Si la valeur n'est pas dans le dictionnaire, elle reste inchangée

    return type_name


pokemon_type_colors = {
    "Normal": "#C1C2C1",  #
    "Fighting": "#FFAC59",  #
    "Flying": "#ADD2F5",  #
    "Poison": "#B884DD",  #
    "Ground": "#B88E6F",  #
    "Rock": "#CBC7AD",  #
    "Bug": "#B8C26A",  #
    "Ghost": "#A284A2",  #
    "Steel": "#98C2D1",  #
    "Fire": "#EF7374",  #
    "Water": "#74ACF5",  #
    "Grass": "#82C274",  #
    "Electric": "#FCD659",  #
    "Psychic": "#F584A8",  #
    "Ice": "#81DFF7",  #
    "Dragon": "#8D98EC",
    "Dark": "#998B8C",
    "Fairy": "#EF70EF",
}
get_type_by_color = lambda color: next(
    (
        type_name
        for type_name, type_color in pokemon_type_colors.items()
        if type_color.lower() == color.lower()
    ),
    None,
)

type_translation = {
    "Normal": "Normal",
    "Fighting": "Combat",
    "Flying": "Vol",
    "Poison": "Poison",
    "Ground": "Sol",
    "Rock": "Roche",
    "Bug": "Insecte",
    "Ghost": "Spectre",
    "Steel": "Acier",
    "Fire": "Feu",
    "Water": "Eau",
    "Grass": "Plante",
    "Electric": "Électrik",
    "Psychic": "Psy",
    "Ice": "Glace",
    "Dragon": "Dragon",
    "Dark": "Ténèbres",
    "Fairy": "Fée",
}


def translate_type_from_fr_to_en(fr_type):
    if isinstance(fr_type, list):
        # Si c'est une liste, traduire chaque type
        return [
            next(
                (
                    type_en
                    for type_en, type_fr in type_translation.items()
                    if type_fr.lower() == t.lower()
                ),
                None,
            )
            for t in fr_type
        ]
    else:
        # Si c'est une chaîne unique, garder le comportement actuel
        return next(
            (
                type_en
                for type_en, type_fr in type_translation.items()
                if type_fr.lower() == fr_type.lower()
            ),
            None,
        )


category_from_type = {
    "Normal": "Physical",
    "Fighting": "Physical",
    "Flying": "Physical",
    "Poison": "Physical",
    "Ground": "Physical",
    "Rock": "Physical",
    "Bug": "Physical",
    "Ghost": "Physical",
    "Steel": "Physical",
    "Fire": "Special",
    "Water": "Special",
    "Grass": "Special",
    "Electric": "Special",
    "Psychic": "Special",
    "Ice": "Special",
    "Dragon": "Special",
    "Dark": "Special",
    "Fairy": "Special",
}
