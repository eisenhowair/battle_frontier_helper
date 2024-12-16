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
        self.builds = builds
        self.weaknesses = weaknesses
        self.build_index = build_index

    def change_build(self, num_build: int):
        self.build_index = num_build

    def current_build(self, info_voulue: str):
        return self.builds[self.build_index][info_voulue]
