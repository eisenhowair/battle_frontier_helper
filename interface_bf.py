import streamlit as st
from model_from_api import get_complete_infos_thread
from CompetPkmn import CompetPkmn
from display import *
from calculation import *

st.set_page_config(layout="wide")
# st.title('Battle Frontier Builds')


# Custom CSS
st.markdown(
    """
    <style> 
        section[data-testid="stSidebar"] {
            width: 5vh !important; # Set the width to your desired value
        }
        .grid-container {
            display: grid;
            grid-template-columns: repeat(4, 1fr); /* 4 colonnes égales */
            gap: 5px; /* Espacement minimal entre les cartes */
        }
        .grid-item {
            background-color: #444; /* Couleur par défaut si rien n'est fourni */
            border-radius: 10px;
            padding: 5px;
            text-align: center;
            font-size: 14px;
            color: white;
        }
        .st-emotion-cache-ocqkz7 {
            gap: 0.5rem !important
        }
        .vertical-align {
            display: flex;
            align-items: center; /* Aligne verticalement les éléments */
            padding-top:3.7vh;
            padding-bottom:0;
            gap:0 !important
        }
        .st-emotion-cache-1ibsh2c {
        padding-right:1vh
        padding-left:3vh
        }
    </style>
    """,
    unsafe_allow_html=True,
)


def update_build_index_poke1():
    st.session_state.poke1.build_index = st.session_state.radio_poke1_index


def update_build_index_poke2():
    st.session_state.poke2.build_index = st.session_state.radio_poke2_index


if "poke1" not in st.session_state:
    st.session_state.poke1 = None
if "poke2" not in st.session_state:
    st.session_state.poke2 = None


# le tableau des faiblesses
def fetch_info_pkmn(pkmn_name: str, num_pkmn: int):
    st.markdown('<div class="vertical-align">', unsafe_allow_html=True)
    if st.button(label="Go", use_container_width=True, key=f"button{num_pkmn}"):
        try:
            weaknesses, builds, name_en, name_fr, types = get_complete_infos_thread(
                name_fr=pkmn_name
            )
            poke = CompetPkmn(
                name_fr=name_fr,
                name_en=name_en,
                builds=builds,
                weaknesses=weaknesses,
                type_pkmn=types,
            )
            if num_pkmn == 1:
                put_in_session(poke1=poke)
            elif num_pkmn == 2:
                put_in_session(poke2=poke)

            # Rerun pour actualiser la sidebar
            st.rerun()

        except KeyError:
            st.error(
                "Erreur rencontrée. Cela peut être dû à une erreur dans le nom tapé."
            )
    st.markdown("</div>", unsafe_allow_html=True)


def show_build(pkmn: CompetPkmn):

    st.header(f"{pkmn.name_en} {pkmn.build_index+1}")

    selected_build_moves = pkmn.current_build(info_voulue="moves")
    selected_build_evs = pkmn.current_build(info_voulue="evs")
    selected_build_stats = pkmn.current_build(info_voulue="stats")
    selected_build_nature = pkmn.current_build(info_voulue="nature")
    selected_build_item = pkmn.current_build(info_voulue="held_object")

    # Moves
    for move in selected_build_moves:
        st.markdown(
            f"""
            <div style="background-color: {move.getBgColor()}; 
                        border-radius: 5px; 
                        padding: 8px; 
                        margin-bottom: 5px; 
                        text-align: center; 
                        color: white;">
                <strong>{move.getName()}</strong>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Nature et EVs
    st.write("**Nature :**", selected_build_nature)

    # Formatage des EVs
    stats_formatted = format_stat(
        evs=selected_build_evs,
        stats=selected_build_stats,
        first_label="EVs",
        second_label="Stats",
    )
    st.markdown(f"{stats_formatted}", unsafe_allow_html=True)
    st.write("**Objet tenu :**", selected_build_item)


def put_in_session(poke1=None, poke2=None):

    if poke1 is not None:
        st.session_state.poke1 = poke1
    if poke2 is not None:
        st.session_state.poke2 = poke2


build_tab, calc_tab = st.tabs(["Build", "Calc"])

# Sidebar : Affichage conditionnel des builds
with st.sidebar:
    st.header("Builds")
    if st.session_state.poke1:
        poke1 = st.session_state.poke1
        # Générer les noms des builds dynamiquement (Build 1, Build 2, etc.)
        build_options = [f"{poke1.name_en} {i + 1}" for i in range(len(poke1.builds))]
        selected_build_index = st.radio(
            "Sélectionnez un build",
            options=range(len(build_options)),  # Retourne un index, pas une chaîne
            format_func=lambda x: build_options[
                x
            ],  # Affiche le nom du build via un formatteur
            index=poke1.build_index,
            key="radio_poke1_index",  # Clé unique
            on_change=update_build_index_poke1,  # Appel du callback
        )

    if st.session_state.poke2:
        poke2 = st.session_state.poke2  # type: CompetPkmn
        build_options = [f"{poke2.name_en} {i + 1}" for i in range(len(poke2.builds))]
        selected_build_index = st.radio(
            "Sélectionnez un build",
            options=range(len(build_options)),  # Retourne un index, pas une chaîne
            format_func=lambda x: build_options[x],  # Affiche le nom du build
            index=poke2.build_index,
            key="radio_poke2_index",  # Clé unique
            on_change=update_build_index_poke2,  # Appel du callback
        )
    else:
        st.write("Aucun build disponible.")

with build_tab:
    input_col, _, col2, _, col3 = st.columns([0.23, 0.03, 0.23, 0.01, 0.22])

    with input_col:
        input_col_inner, button_col = st.columns([0.7, 0.3])
        with input_col_inner:
            pkmn_name1 = st.text_input(
                placeholder="...", label="Entrez un nom", key="input_field"
            )

        with button_col:
            fetch_info_pkmn(pkmn_name=pkmn_name1, num_pkmn=1)

        # Affichage des faiblesses dans la colonne input_col
        if st.session_state.poke1:
            st.write("**Faiblesses :**")
            display_weakness_tags(weaknesses=st.session_state.poke1.weaknesses)

        input_col_inner2, button_col2 = st.columns([0.7, 0.3])
        with input_col_inner2:
            pkmn_name2 = st.text_input(
                placeholder="...", label="Entrez un nom", key="input_field2"
            )

        with button_col2:
            fetch_info_pkmn(pkmn_name=pkmn_name2, num_pkmn=2)

        if st.session_state.poke2:
            st.write("**Faiblesses :**")
            display_weakness_tags(weaknesses=st.session_state.poke2.weaknesses)

    # Colonne col2 : Affichage du build sélectionné
    with col2:
        if st.session_state.poke1:
            show_build(pkmn=st.session_state.poke1)

        else:
            st.write("Aucun build sélectionné.")

    with col3:
        if st.session_state.poke2:
            show_build(pkmn=st.session_state.poke2)

        else:
            st.write("Aucun build sélectionné.")

with calc_tab:
    display_calc_tab()
