from model_from_api import get_move_info
import concurrent.futures

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


class CompetPkmn:
    def __init__(
        self,
        name_fr: str,
        name_en: str,
        builds,
        weaknesses,
        type_pkmn,
        build_index: int = 0,
    ):

        self.name_fr = name_fr
        self.name_en = name_en
        self.type = translate_type_from_fr_to_en(type_pkmn)
        self.weaknesses = weaknesses
        self.build_index = build_index
        self.init_builds(builds)

        # print(f"voici le type:{self.type}")
        # print(self.weaknesses)

    def change_build(self, num_build: int):
        self.build_index = num_build

    def current_build(self, info_voulue: str):
        return self.builds[self.build_index][info_voulue]

    def init_builds(self, builds):
        def create_move(move):
            """Facilite l'utilisation de threads"""
            return Move(name=move["move_name"], bg_color=move["background_color"])

        for build in builds:
            # Paralléliser la création des objets Move pour chaque build
            with concurrent.futures.ThreadPoolExecutor() as executor:
                build["moves"] = list(executor.map(create_move, build["moves"]))

        self.builds = builds


class Move:
    def __init__(
        self,
        name,
        bg_color,
    ):
        self.name = name
        self.bg_color = bg_color
        self.type = get_type_by_color(bg_color)
        # print(f"{self.name} est de type {self.bg_color}")

        move_stats = get_move_info(name)
        self.power = move_stats["Power"]
        self.accuracy = move_stats["Accuracy"]
        self.category = move_stats["Category"]

    def getBgColor(self):
        return self.bg_color

    def getName(self):
        return self.name

    def getPower(self):
        return self.power

    def getCategory(self):
        return self.category

    def getType(self):
        return self.type
