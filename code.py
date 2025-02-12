import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
from streamlit_option_menu import option_menu
import plotly.graph_objects as go

# Configuration de la page
st.set_page_config(
    page_title="Gestion des Cotisations",
    page_icon="💰",
    layout="wide"
)

# Initialisation des données dans la session state
if 'cotisations' not in st.session_state:
    st.session_state.cotisations = pd.DataFrame(columns=['Date', 'Membre', 'Mois', 'Montant'])
if 'depenses' not in st.session_state:
    st.session_state.depenses = pd.DataFrame(columns=['Date', 'Type', 'Description', 'Montant'])

# Charger la liste des membres
try:
    membres_df = pd.read_csv("Fidele intendant - Feuille 1.csv", encoding='utf-8')
    # Afficher les noms des colonnes pour le débogage
    print("Colonnes dans le fichier:", membres_df.columns.tolist())
    
    # Trouver la colonne qui contient les noms (première colonne)
    nom_colonne = membres_df.columns[0]
    liste_membres = membres_df[nom_colonne].dropna().tolist()
except Exception as e:
    st.error(f"Erreur lors de la lecture du fichier: {str(e)}")
    liste_membres = []  # Liste vide en cas d'erreur

# Styles CSS personnalisés
st.markdown("""
    <style>
    .main {
        padding: 20px;
    }
    .stButton > button {
        width: 100%;
        margin-top: 10px;
    }
    .stat-box {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# Menu de navigation
selected = option_menu(
    menu_title=None,
    options=["📝 Entrées", "📊 Tableau de Bord"],
    icons=["pencil-square", "bar-chart-fill"],
    default_index=0,
    orientation="horizontal",
)

if selected == "📝 Entrées":
    st.title("📝 Gestion des Entrées")
    
    # Création de deux colonnes
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💰 Nouvelle Cotisation")
        with st.form("form_cotisation"):
            if liste_membres:
                membre = st.selectbox("Membre", liste_membres)
            else:
                st.error("Impossible de charger la liste des membres")
                membre = st.text_input("Membre")
                
            mois = st.selectbox("Mois", ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", 
                                       "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"])
            montant = st.number_input("Montant (FCFA)", min_value=0)
            submit_cotisation = st.form_submit_button("Enregistrer la cotisation")
            
            if submit_cotisation:
                nouvelle_cotisation = pd.DataFrame({
                    'Date': [datetime.now()],
                    'Membre': [membre],
                    'Mois': [mois],
                    'Montant': [montant]
                })
                st.session_state.cotisations = pd.concat([st.session_state.cotisations, nouvelle_cotisation], ignore_index=True)
                st.success("✅ Cotisation enregistrée avec succès!")
    
    with col2:
        st.subheader("📋 Nouvelle Dépense")
        with st.form("form_depense"):
            type_depense = st.selectbox("Type de dépense", ["Dédicace nouveau-né", "Décès", "Mariage"])
            description = st.text_area("Description")
            montant_depense = st.number_input("Montant (FCFA)", min_value=0, key="depense_montant")
            submit_depense = st.form_submit_button("Enregistrer la dépense")
            
            if submit_depense:
                nouvelle_depense = pd.DataFrame({
                    'Date': [datetime.now()],
                    'Type': [type_depense],
                    'Description': [description],
                    'Montant': [montant_depense]
                })
                st.session_state.depenses = pd.concat([st.session_state.depenses, nouvelle_depense], ignore_index=True)
                st.success("✅ Dépense enregistrée avec succès!")

elif selected == "📊 Tableau de Bord":
    st.title("📊 Tableau de Bord")
    
    # Calcul des statistiques
    total_cotisations = st.session_state.cotisations['Montant'].sum()
    total_depenses = st.session_state.depenses['Montant'].sum()
    solde = total_cotisations - total_depenses
    
    # Affichage des statistiques dans des colonnes
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
            <div class="stat-box">
                <h3>Total Cotisations</h3>
                <h2 style="color: green;">💰 {:,.0f} FCFA</h2>
            </div>
        """.format(total_cotisations), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class="stat-box">
                <h3>Total Dépenses</h3>
                <h2 style="color: red;">📉 {:,.0f} FCFA</h2>
            </div>
        """.format(total_depenses), unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
            <div class="stat-box">
                <h3>Solde</h3>
                <h2 style="color: {};">💳 {:,.0f} FCFA</h2>
            </div>
        """.format('green' if solde >= 0 else 'red', solde), unsafe_allow_html=True)
    
    # Graphiques
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Cotisations par Mois")
        if not st.session_state.cotisations.empty:
            cotisations_par_mois = st.session_state.cotisations.groupby('Mois')['Montant'].sum().reset_index()
            fig = px.bar(cotisations_par_mois, x='Mois', y='Montant',
                        title="Cotisations par Mois",
                        labels={'Montant': 'Montant (FCFA)'})
            st.plotly_chart(fig)
        else:
            st.info("Aucune cotisation enregistrée pour le moment")
    
    with col2:
        st.subheader("📊 Répartition des Dépenses")
        if not st.session_state.depenses.empty:
            depenses_par_type = st.session_state.depenses.groupby('Type')['Montant'].sum()
            fig = px.pie(values=depenses_par_type.values, 
                        names=depenses_par_type.index,
                        title="Répartition des Dépenses par Type")
            st.plotly_chart(fig)
        else:
            st.info("Aucune dépense enregistrée pour le moment")
    
    # Tableaux détaillés
    st.subheader("📑 Dernières Cotisations")
    if not st.session_state.cotisations.empty:
        st.dataframe(st.session_state.cotisations.sort_values('Date', ascending=False))
    else:
        st.info("Aucune cotisation enregistrée")
    
    st.subheader("📑 Dernières Dépenses")
    if not st.session_state.depenses.empty:
        st.dataframe(st.session_state.depenses.sort_values('Date', ascending=False))
    else:
        st.info("Aucune dépense enregistrée")