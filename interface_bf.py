import streamlit as st
from recup_weakness import get_complete_infos
from CompetPkmn import CompetPkmn

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


def display_weakness_tags(weaknesses):
    """Affiche les faiblesses sous forme de tags colorés."""
    cols_per_row = 4
    rows = [
        weaknesses[i : i + cols_per_row]
        for i in range(0, len(weaknesses), cols_per_row)
    ]

    for row in rows:
        cols = st.columns(len(row))
        for col, weakness in zip(cols, row):
            with col:
                st.markdown(
                    f"""
                    <div style="background-color: {weakness['color']}; 
                                border-radius: 10px; 
                                padding: 3px; 
                                margin-bottom: 3px; 
                                text-align: justify;">
                        <strong style="font-size: 14px;">{weakness['name']} x{weakness['damage_multiplier']}</strong>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


def format_stat(
    evs,
    stats,
    first_label="EVs",
    second_label="Stats",
    additional_lists=None,
    additional_labels=None,
):
    # Labels des statistiques
    stat_labels = ["", "HP", "Atk", "Def", "SpA", "SpDef", "SpD"]

    # Formater les EV avec des couleurs
    formatted_evs = format_evs(evs)

    # Insérer les labels dans les listes
    evs_with_label = [first_label] + evs  # Ajouter la légende aux EV
    stats_with_label = [second_label] + stats  # Ajouter la légende aux stats

    # Vérifier que les listes ont la même longueur
    if len(evs_with_label) != len(stats_with_label) or (
        additional_lists and any(len(lst) != len(stats) for lst in additional_lists)
    ):
        raise ValueError("Les listes doivent avoir la même longueur.")

    # Créer la première ligne : noms des stats
    first_line = "<tr><th>" + "</th><th>".join(stat_labels) + "</th></tr>"

    # Créer la deuxième ligne : EV formatés avec la légende
    formatted_evs_with_label = [first_label] + formatted_evs.split(
        ", "
    )  # Ajouter la légende
    second_line = "<tr><td>" + "</td><td>".join(formatted_evs_with_label) + "</td></tr>"

    # Créer la troisième ligne : stats avec la légende
    third_line = (
        "<tr><td>" + "</td><td>".join(map(str, stats_with_label)) + "</td></tr>"
    )

    # Créer les lignes supplémentaires dynamiquement avec une boucle for
    additional_lines = ""
    if additional_lists:
        for i, additional_list in enumerate(additional_lists):
            # Ajouter une légende pour chaque liste supplémentaire
            label = additional_labels[i]
            additional_list_with_label = [label] + additional_list
            additional_lines += (
                "<tr><td>"
                + "</td><td>".join(map(str, additional_list_with_label))
                + "</td></tr>"
            )

    # Retourner le HTML final
    return f"<table style='font-size:14px'>{first_line}{second_line}{third_line}{additional_lines}</table>"


# Fonction pour formater les EV (déjà fournie)
def format_evs(evs):
    ev_labels = ["HP", "Atk", "Def", "SpA", "SpDef", "Spd"]
    formatted_evs = []
    for label, value in zip(ev_labels, evs):
        if value > 0 and value < 252:
            # Brun pour les valeurs > 0
            formatted_evs.append(f"<span style='color: #FFC000;'>{value}</span>")
        elif value == 252:
            # Rouge pour 252
            formatted_evs.append(f"<span style='color: red;'>{value}</span>")
        else:
            # Par défaut (noir) pour 0
            formatted_evs.append(f"{value}")
    return ", ".join(formatted_evs)


if "poke1" not in st.session_state:
    st.session_state.poke1 = None
if "poke2" not in st.session_state:
    st.session_state.poke2 = None


# le tableau des faiblesses
def fetch_info_pkmn(pkmn_name: str, num_pkmn: int):
    st.markdown('<div class="vertical-align">', unsafe_allow_html=True)
    if st.button(label="Go", use_container_width=True, key=f"button{num_pkmn}"):
        try:
            weaknesses, builds, name_en, name_fr = get_complete_infos(name_fr=pkmn_name)
            poke = CompetPkmn(
                name_fr=name_fr,
                name_en=name_en,
                builds=builds,
                weaknesses=weaknesses,
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
            <div style="background-color: {move['background_color']}; 
                        border-radius: 5px; 
                        padding: 8px; 
                        margin-bottom: 5px; 
                        text-align: center; 
                        color: white;">
                <strong>{move['move_name']}</strong>
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


input_col, _, col2, _, col3 = st.columns([0.23, 0.03, 0.23, 0.01, 0.22])

# Sidebar : Affichage conditionnel des builds
with st.sidebar:
    st.header("Builds")
    if st.session_state.poke1:
        poke1 = st.session_state.poke1
        # Générer les noms des builds dynamiquement (Build 1, Build 2, etc.)
        build_options = [f"{poke1.name_en} {i + 1}" for i in range(len(poke1.builds))]
        selected_build_name = st.radio(
            "Sélectionnez un build",
            build_options,
            index=poke1.build_index,
        )
        # Convertir le nom sélectionné en index numérique
        st.session_state.poke1.build_index = build_options.index(selected_build_name)

    if st.session_state.poke2:
        poke2 = st.session_state.poke2  # type: CompetPkmn
        build_options = [f"{poke2.name_en} {i + 1}" for i in range(len(poke2.builds))]
        selected_build_name = st.radio(
            "Sélectionnez un build",
            build_options,
            index=poke2.build_index,
        )
        # Convertir le nom sélectionné en index numérique
        st.session_state.poke2.build_index = build_options.index(selected_build_name)
    else:
        st.write("Aucun build disponible.")

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
        weaknesses = st.session_state.poke1.weaknesses
        st.write("**Faiblesses :**")
        display_weakness_tags(weaknesses=weaknesses)

    input_col_inner2, button_col2 = st.columns([0.7, 0.3])
    with input_col_inner2:
        pkmn_name2 = st.text_input(
            placeholder="...", label="Entrez un nom", key="input_field2"
        )

    with button_col2:
        fetch_info_pkmn(pkmn_name=pkmn_name2, num_pkmn=2)

    if st.session_state.poke2:
        weaknesses = st.session_state.poke2.weaknesses
        st.write("**Faiblesses :**")
        display_weakness_tags(weaknesses=weaknesses)

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
