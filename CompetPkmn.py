from model_from_api import get_move_info
import concurrent.futures

from dictionaries_convert import *


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
            return Move(
                name=move["move_name"],
                bg_color=move["background_color"],
                type_category_dict=category_from_type,
            )

        for build in builds:
            # Paralléliser la création des objets Move pour chaque build
            with concurrent.futures.ThreadPoolExecutor() as executor:
                build["moves"] = list(executor.map(create_move, build["moves"]))

        self.builds = builds


class Move:
    def __init__(self, name, bg_color, type_category_dict):
        self.name = name
        self.bg_color = bg_color
        self.type = get_type_by_color(bg_color)
        # print(f"{self.name} est de type {self.bg_color}")

        move_stats = get_move_info(name)
        self.power = move_stats["Power"]
        self.accuracy = move_stats["Accuracy"]
        if move_stats["Category"] == "Status":
            self.category = "Status"
        else:
            self.category = type_category_dict[self.type]

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
