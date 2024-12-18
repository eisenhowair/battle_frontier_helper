from model_from_api import get_move_info
import concurrent.futures

pokemon_type_colors = {
    "Normal": "#9FA19F",
    "Fighting": "#FF8000",
    "Flying": "#81B9EF",
    "Poison": "#9141CB",
    "Ground": "#915121",
    "Rock": "#AFA981",
    "Bug": "#91A119",
    "Ghost": "#704170",
    "Steel": "#60A1B8",
    "Fire": "#E62829",
    "Water": "#2980EF",
    "Grass": "#3FA129",
    "Electric": "#FAC000",
    "Psychic": "#EF4179",
    "Ice": "#3DCEF3",
    "Dragon": "#5060E1",
    "Dark": "#624D4E",
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


class CompetPkmn:
    def __init__(
        self,
        name_fr: str,
        name_en: str,
        builds,
        weaknesses,
        build_index: int = 0,
    ):

        self.name_fr = name_fr
        self.name_en = name_en
        self.weaknesses = weaknesses
        self.build_index = build_index
        self.init_builds(builds)

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
        self.power, self.accuracy, self.category = get_move_info(name)

    def getBgColor(self):
        return self.bg_color

    def getName(self):
        return self.name
