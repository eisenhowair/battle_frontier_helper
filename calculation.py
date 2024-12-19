import streamlit as st
from CompetPkmn import CompetPkmn, Move


def display_side_build(num_poke: int, inverted: bool = False):
    if num_poke == 1:
        current_build_moves = st.session_state.poke1.current_build(info_voulue="moves")
    else:
        current_build_moves = st.session_state.poke2.current_build(info_voulue="moves")

    for move in current_build_moves:
        low_roll = high_roll = "-"

        if st.session_state.poke1 and st.session_state.poke2:
            low_roll, high_roll = damage_calculation(
                move=move,
                pkmn_attacking=st.session_state.poke1,
                pkmn_target=st.session_state.poke2,
            )

        name_element = f'<div style="flex: 0 0 30%; text-align: left;"><strong>{move.getName()}</strong></div>'
        power_element = f'<div style="flex: 0 0 15%; text-align: center;"><strong>{move.getPower() if move.getPower() != "None" else "-"}</strong></div>'
        damage_element = f'<div style="flex: 0 0 25%; text-align: {"left" if inverted else "right"}; color:black;"><strong>{low_roll if st.session_state.poke1 and st.session_state.poke2 else "-"} - {high_roll if st.session_state.poke1 and st.session_state.poke2 else "-"}</strong></div>'

        content = (
            damage_element + power_element + name_element
            if inverted
            else name_element + power_element + damage_element
        )

        html_content = f'<div style="background-color: {move.getBgColor()}; border-radius: 5px; padding: 8px; margin-bottom: 5px; text-align: center; color: white;"><div style="display: flex; width: 100%; justify-content: space-between; align-items: center;">{content}</div></div>'

        st.markdown(html_content, unsafe_allow_html=True)


def find_weakness_by_name(items_list, name_to_find):

    filtered = list(filter(lambda x: x["name"] == name_to_find, items_list))
    return filtered[0] if filtered else None


def display_calc_tab():

    build_left, _, build_right = st.columns([0.3, 0.2, 0.30])

    if st.session_state.poke1 and st.session_state.poke2:
        with build_left:
            display_side_build(1, inverted=False)

        with build_right:
            display_side_build(2, inverted=True)
    else:
        st.write("No builds to show. Please choose two Pokémon in the Build tab.")


def scale_to_opp_hp_percent(dmg_to_scale, opponent_hp):

    return round(100 * dmg_to_scale / opponent_hp, 2)  # produit en croix


def damage_calculation(
    move: Move, pkmn_attacking: CompetPkmn, pkmn_target: CompetPkmn, **modificateurs
):

    attacking_build_stats = pkmn_attacking.current_build(info_voulue="stats")
    defending_build_stats = pkmn_target.current_build(info_voulue="stats")
    move_power = float(move.getPower()) if move.getPower() is not None else 0
    move_type = move.getType()
    opponent_hp = defending_build_stats[0]

    weather = screen = double_dmg = burn = stab = expert_belt = tinted_lens = berry = (
        faiblesse_coeff
    ) = 1

    sensitivity = find_weakness_by_name(
        items_list=pkmn_target.weaknesses, name_to_find=move_type
    )

    faiblesse_coeff = sensitivity["damage_multiplier"]

    if move.getCategory() == "Physical":
        A_D_ratio = attacking_build_stats[1] / defending_build_stats[2]

    elif move.getCategory() == "Special":
        A_D_ratio = attacking_build_stats[3] / defending_build_stats[4]
    else:
        return 0, 0
    damage = ((2 * 100 / 5 + 2) * move_power * A_D_ratio) / 50

    if (
        "Burn" in modificateurs
        and modificateurs["Burn"]
        and move.getCategory() == "Physical"
    ):
        burn = 0.5

    if (
        "Protect" in modificateurs
        and modificateurs["Protect"]
        and move.getCategory() == "Physical"
    ):
        screen = 0.5

    if (
        "Light Screen" in modificateurs
        and modificateurs["Light Screen"]
        and move.getCategory() == "Special"
    ):
        screen = 0.5
    if "Rain" in modificateurs and modificateurs["Rain"]:
        if move_type == "Water":
            weather = 1.5
        elif move_type == "Fire" or move.getName() == "Solar Beam":
            weather *= 0.5

    if "Sunlight" in modificateurs and modificateurs["Sunlight"]:
        if move_type == "Fire":
            weather = 1.5
        elif move_type == "Water":
            weather = 0.5

    if "DoubleDmg" in modificateurs and modificateurs["DoubleDmg"]:
        double_dmg = 2

    if move_type in pkmn_attacking.type:
        stab = 1.5
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

    if "Berry" in modificateurs and modificateurs["Berry"]:
        berry = 0.5

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
    print(
        "A/D ratio =",
        A_D_ratio,
        "weather =",
        weather,
        "screen =",
        screen,
        "double_dmg =",
        double_dmg,
        "burn =",
        burn,
        "stab =",
        stab,
        "expert_belt =",
        expert_belt,
        "tinted_lens =",
        tinted_lens,
        "berry =",
        berry,
        "faiblesse_coeff =",
        faiblesse_coeff,
    )

    return scale_to_opp_hp_percent(
        final_damage * 0.85, opponent_hp
    ), scale_to_opp_hp_percent(final_damage, opponent_hp)
