import streamlit as st
from CompetPkmn import CompetPkmn, Move


def display_side_build(num_poke: int):
    if num_poke == 1:
        current_build_moves = st.session_state.poke1.current_build(info_voulue="moves")
    else:
        current_build_moves = st.session_state.poke2.current_build(info_voulue="moves")

    for move in current_build_moves:
        st.markdown(
            f"""
            <div style="background-color: {move.getBgColor()}; 
                        border-radius: 5px; 
                        padding: 8px; 
                        margin-bottom: 5px; 
                        text-align: center; 
                        color: white;">
                <table style="width: 100%; text-align: center; table-layout: fixed; border-collapse: collapse; border: none;">
                    <tr style="border: none;">
                        <td style="width: 40%; text-align: left; border: none;"><strong>{move.getName()}</strong></td>
                        <td style="width: 20%; text-align: right; border: none;"><strong>{move.getPower()}</strong></td>
                        <td style="width: 40%; text-align: left; border: none; padding-left: 15px;">Votre texte ici</td>
                    </tr>
                </table>
            </div>
            """,
            unsafe_allow_html=True,
        )


def find_weakness_by_name(items_list, name_to_find):
    print(name_to_find)
    for item in items_list:
        print(item)
    filtered = list(filter(lambda x: x["name"] == name_to_find, items_list))
    return filtered[0] if filtered else None


def display_calc_tab():

    build_left, calc_column, build_right = st.columns([0.23, 0.3, 0.23])
    nbr_build_valide = 0

    if st.session_state.poke1:
        nbr_build_valide += 1
        with build_left:
            display_side_build(1)
    if st.session_state.poke2:
        nbr_build_valide += 1
        with build_right:
            display_side_build(2)

    if nbr_build_valide == 2:
        with calc_column:
            for move in st.session_state.poke1.current_build(info_voulue="moves"):
                st.write(
                    damage_calculation(
                        move=move,
                        pkmn_attacking=st.session_state.poke1,
                        pkmn_target=st.session_state.poke2,
                    )
                )


def damage_calculation(
    move: Move, pkmn_attacking: CompetPkmn, pkmn_target: CompetPkmn, **modificateurs
):

    attacking_build_stats = pkmn_attacking.current_build(info_voulue="stats")
    defending_build_stats = pkmn_target.current_build(info_voulue="stats")
    move_power = float(move.getPower()) if move.getPower() is not None else 0
    move_type = move.getType()
    weather = screen = double_dmg = burn = stab = expert_belt = tinted_lens = berry = (
        faiblesse_coeff
    ) = 1
    if move.getCategory() == "Physical":
        A_D_ratio = attacking_build_stats[1] / defending_build_stats[2]
    elif move.getCategory() == "Special":
        A_D_ratio = attacking_build_stats[3] / defending_build_stats[5]
    else:
        return 0

    damage = ((2 * 100 / 5 + 2) * move_power * A_D_ratio) / 50
    if modificateurs.get("Burn", True) and move.getCategory() == "Physical":
        burn = 0.5
    if modificateurs.get("Protect", True) and move.getCategory() == "Physical":
        screen = 0.5
    if modificateurs.get("Light Screen", True) and move.getCategory() == "Special":
        screen = 0.5
    if modificateurs.get("Rain", True):
        if move_type == "Water":
            weather = 1.5
        elif move_type == "Fire" or move.getName() == "Solar Beam":
            weather *= 0.5
    if modificateurs.get("Sunlight", True):
        if move_type == "Fire":
            weather = 1.5
        elif move_type == "Water":
            weather = 0.5
    if modificateurs.get("DoubleDmg", True):
        double_dmg = 2
    if move_type in pkmn_attacking.type:
        stab = 1.5
    # print(f"{pkmn_target.weaknesses} \n{move_type}")
    sensitivity = find_weakness_by_name(
        items_list=pkmn_target.weaknesses, name_to_find=move_type
    )
    # print(f"sensitivity:{sensitivity}")
    faiblesse_coeff = sensitivity["damage_multiplier"]
    if (
        pkmn_attacking.current_build(info_voulue="held_object") == "Expert Belt"
        and faiblesse_coeff > 1
    ):
        expert_belt = 1.2
    if (
        pkmn_attacking.current_build(info_voulue="held_object") == "Tinted Lens"
        and faiblesse_coeff < 1
    ):
        tinted_lens = 2

    # le cas des berry est encore à implémenter

    final_damage = (
        damage
        * weather
        * screen
        * double_dmg
        * burn
        * stab
        * expert_belt
        * tinted_lens
        * berry
        * faiblesse_coeff
    )

    return final_damage * 0.85, final_damage
