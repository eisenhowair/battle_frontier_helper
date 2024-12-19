import streamlit as st


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
                        <strong style="font-size: 14px;">{raccourci_nom_type(weakness['name'])} x{weakness['damage_multiplier']}</strong>
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
