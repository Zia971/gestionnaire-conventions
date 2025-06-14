"""
Gestionnaire de Conventions - Application Streamlit
Version : 1.0
Auteur : Assistant IA
Description : Application professionnelle de suivi des conventions avec alertes automatiques
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json

# Configuration de la page
st.set_page_config(
    page_title="Gestionnaire de Conventions",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé pour les couleurs professionnelles
st.markdown("""<style>

    .status-ok { color: #10B981; font-weight: bold; }
    .status-warning { color: #F59E0B; font-weight: bold; }
    .status-urgent { color: #EF4444; font-weight: bold; }
    .status-info { color: #3B82F6; font-weight: bold; }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 0.5rem;
        color: white;
        text-align: center;
    }
    .alert-box {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        border-left: 4px solid;
    }
    .alert-urgent { 
        background-color: #FEF2F2; 
        border-color: #EF4444; 
        color: #991B1B; 
    }
    .alert-warning { 
        background-color: #FFFBEB; 
        border-color: #F59E0B; 
        color: #92400E; 
    }
    .alert-ok { 
        background-color: #F0FDF4; 
        border-color: #10B981; 
        color: #065F46; 
    }
</style>

""", unsafe_allow_html=True)

# Fonction pour initialiser les données de démonstration
@st.cache_data
def load_demo_data():
    """Charge les données de démonstration des conventions"""
    data = {
        'Numero_Operation': ['001', '002', '003', '004', '005'],
        'Operation': [
            'Construction Résidence Soleil',
            'Réhabilitation Quartier Vert', 
            'Logements sociaux Cité Bleue',
            'Rénovation Centre Ville',
            'Parc Écologique Municipal'
        ],
        'Nom_Convention': [
            'Convention de financement ANRU',
            'Subvention État',
            'Aide européenne FEDER',
            'Aide Région Infrastructure', 
            'Subvention Environnement'
        ],
        'Financeur': [
            'Banque des Territoires',
            'Agence Nationale Habitat',
            'Union Européenne',
            'Conseil Régional',
            'ADEME'
        ],
        'Montant_Euro': [2500000, 1800000, 3200000, 950000, 750000],
        'Date_Debut': [
            '2023-04-01', '2023-06-01', '2023-09-15', 
            '2024-01-15', '2024-03-01'
        ],
        'Date_Fin': [
            '2026-03-31', '2027-05-31', '2028-09-14',
            '2025-12-31', '2026-02-28'
        ],
        'Statut': [
            'En cours', 'En attente', 'Validée', 
            'En cours', 'En cours'
        ],
        'Prorogation': ['Non', 'Oui', 'Oui', 'Non', 'Non'],
        'Urgence': ['OK', 'À surveiller', 'OK', 'Urgent', 'À surveiller']
    }
    
    df = pd.DataFrame(data)
    df['Date_Debut'] = pd.to_datetime(df['Date_Debut'])
    df['Date_Fin'] = pd.to_datetime(df['Date_Fin'])
    return df

# Fonction de calcul des rappels
def calculer_rappels(date_fin):
    """Calcule les dates de rappel (-6, -3, -1 mois)"""
    rappel_6 = date_fin - timedelta(days=180)  # ~6 mois
    rappel_3 = date_fin - timedelta(days=90)   # ~3 mois  
    rappel_1 = date_fin - timedelta(days=30)   # ~1 mois
    return rappel_6, rappel_3, rappel_1

def determiner_urgence(date_fin):
    """Détermine le niveau d'urgence selon la date de fin"""
    aujourd_hui = datetime.now()
    jours_restants = (date_fin - aujourd_hui).days
    
    if jours_restants < 0:
        return "Dépassée", "urgent"
    elif jours_restants <= 30:
        return "Urgent", "urgent"
    elif jours_restants <= 90:
        return "À surveiller", "warning"
    else:
        return "OK", "ok"

# Fonction de formatage des montants
def format_montant(montant):
    """Formate les montants en euros avec séparateurs"""
    return f"{montant:,.0f} €".replace(",", " ")

# Initialisation des données
if 'conventions_data' not in st.session_state:
    st.session_state.conventions_data = load_demo_data()

# Sidebar - Navigation
st.sidebar.title("🏢 Gestionnaire de Conventions")
st.sidebar.markdown("---")

page = st.sidebar.selectbox(
    "Navigation",
    ["🏠 Tableau de Bord", "📋 Gestion des Conventions", "➕ Ajouter Convention", 
     "🚨 Alertes & Rappels", "📊 Rapports & Statistiques", "⚙️ Configuration"]
)

# Page Tableau de Bord
if page == "🏠 Tableau de Bord":
    st.title("📊 Tableau de Bord - Suivi des Conventions")
    
    df = st.session_state.conventions_data
    
    # Métriques principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="📋 Total Conventions",
            value=len(df),
            delta=f"+{len(df[df['Statut'] == 'En cours'])} en cours"
        )
    
    with col2:
        montant_total = df['Montant_Euro'].sum()
        st.metric(
            label="💰 Montant Total", 
            value=format_montant(montant_total),
            delta=f"{len(df[df['Urgence'] == 'OK'])} validées"
        )
    
    with col3:
        urgentes = len(df[df['Urgence'] == 'Urgent'])
        st.metric(
            label="🚨 Conventions Urgentes",
            value=urgentes,
            delta=f"-{urgentes} à traiter" if urgentes > 0 else "Aucune urgence"
        )
    
    with col4:
        prorogations = len(df[df['Prorogation'] == 'Oui'])
        st.metric(
            label="🔄 Prorogations",
            value=prorogations,
            delta=f"{prorogations}/{len(df)} conventions"
        )
    
    st.markdown("---")
    
    # Graphiques
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Répartition par Statut")
        fig_statut = px.pie(
            df, names='Statut', 
            color_discrete_map={
                'En cours': '#3B82F6',
                'En attente': '#F59E0B', 
                'Validée': '#10B981'
            }
        )
        fig_statut.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_statut, use_container_width=True)
    
    with col2:
        st.subheader("💰 Montants par Financeur")
        fig_montant = px.bar(
            df, x='Financeur', y='Montant_Euro',
            color='Urgence',
            color_discrete_map={
                'OK': '#10B981',
                'À surveiller': '#F59E0B',
                'Urgent': '#EF4444'
            }
        )
        fig_montant.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_montant, use_container_width=True)
    
    # Alertes récentes
    st.subheader("🔔 Alertes Récentes")
    for _, conv in df.iterrows():
        if conv['Urgence'] == 'Urgent':
            st.markdown(f"""
            
                🚨 {conv['Operation']}
                Échéance : {conv['Date_Fin'].strftime('%d/%m/%Y')} - 
                Montant : {format_montant(conv['Montant_Euro'])}
            
            """, unsafe_allow_html=True)
        elif conv['Urgence'] == 'À surveiller':
            st.markdown(f"""
            
                ⚠️ {conv['Operation']}
                Échéance : {conv['Date_Fin'].strftime('%d/%m/%Y')} - 
                Montant : {format_montant(conv['Montant_Euro'])}
            
            """, unsafe_allow_html=True)

# Page Gestion des Conventions
elif page == "📋 Gestion des Conventions":
    st.title("📋 Gestion des Conventions")
    
    df = st.session_state.conventions_data
    
    # Filtres
    col1, col2, col3 = st.columns(3)
    
    with col1:
        filtre_statut = st.selectbox(
            "Filtrer par Statut",
            ["Tous"] + list(df['Statut'].unique())
        )
    
    with col2:
        filtre_urgence = st.selectbox(
            "Filtrer par Urgence", 
            ["Tous"] + list(df['Urgence'].unique())
        )
    
    with col3:
        filtre_financeur = st.selectbox(
            "Filtrer par Financeur",
            ["Tous"] + list(df['Financeur'].unique())
        )
    
    # Application des filtres
    df_filtered = df.copy()
    if filtre_statut != "Tous":
        df_filtered = df_filtered[df_filtered['Statut'] == filtre_statut]
    if filtre_urgence != "Tous":
        df_filtered = df_filtered[df_filtered['Urgence'] == filtre_urgence]
    if filtre_financeur != "Tous":
        df_filtered = df_filtered[df_filtered['Financeur'] == filtre_financeur]
    
    # Recherche
    recherche = st.text_input("🔍 Rechercher une convention")
    if recherche:
        mask = df_filtered.apply(lambda x: x.astype(str).str.contains(recherche, case=False, na=False)).any(axis=1)
        df_filtered = df_filtered[mask]
    
    # Affichage du tableau
    st.subheader(f"📋 Conventions ({len(df_filtered)} résultats)")
    
    # Configuration des colonnes pour l'affichage
    df_display = df_filtered.copy()
    df_display['Montant_Euro'] = df_display['Montant_Euro'].apply(format_montant)
    df_display['Date_Debut'] = df_display['Date_Debut'].dt.strftime('%d/%m/%Y')
    df_display['Date_Fin'] = df_display['Date_Fin'].dt.strftime('%d/%m/%Y')
    
    st.dataframe(
        df_display,
        use_container_width=True,
        hide_index=True
    )
    
    # Actions sur les conventions
    st.subheader("⚙️ Actions")
    
    if st.button("📥 Exporter en CSV"):
        csv = df_filtered.to_csv(index=False)
        st.download_button(
            label="💾 Télécharger CSV",
            data=csv,
            file_name="conventions_export.csv",
            mime="text/csv"
        )

# Page Ajouter Convention
elif page == "➕ Ajouter Convention":
    st.title("➕ Ajouter une Nouvelle Convention")
    
    with st.form("nouvelle_convention"):
        col1, col2 = st.columns(2)
        
        with col1:
            numero = st.text_input("Numéro d'Opération *")
            operation = st.text_input("Nom de l'Opération *")
            convention = st.text_input("Nom de la Convention *")
            financeur = st.selectbox(
                "Financeur *",
                ["Banque des Territoires", "Agence Nationale Habitat", 
                 "Union Européenne", "Conseil Régional", "ADEME", "Autre"]
            )
            if financeur == "Autre":
                financeur = st.text_input("Préciser le financeur")
        
        with col2:
            montant = st.number_input("Montant (€) *", min_value=0, step=1000)
            date_debut = st.date_input("Date de Début *")
            date_fin = st.date_input("Date de Fin *")
            statut = st.selectbox("Statut *", ["En cours", "En attente", "Validée"])
            prorogation = st.selectbox("Prorogation", ["Non", "Oui"])
        
        submitted = st.form_submit_button("✅ Ajouter la Convention")
        
        if submitted:
            if numero and operation and convention and financeur and montant:
                nouvelle_ligne = {
                    'Numero_Operation': numero,
                    'Operation': operation,
                    'Nom_Convention': convention,
                    'Financeur': financeur,
                    'Montant_Euro': montant,
                    'Date_Debut': pd.to_datetime(date_debut),
                    'Date_Fin': pd.to_datetime(date_fin),
                    'Statut': statut,
                    'Prorogation': prorogation,
                    'Urgence': determiner_urgence(pd.to_datetime(date_fin))[0]
                }
                
                # Ajout à la session
                st.session_state.conventions_data = pd.concat([
                    st.session_state.conventions_data,
                    pd.DataFrame([nouvelle_ligne])
                ], ignore_index=True)
                
                st.success("✅ Convention ajoutée avec succès!")
                st.rerun()
            else:
                st.error("❌ Veuillez remplir tous les champs obligatoires")

# Page Alertes & Rappels
elif page == "🚨 Alertes & Rappels":
    st.title("🚨 Alertes & Rappels")
    
    df = st.session_state.conventions_data
    
    # Calcul des alertes
    alertes_urgentes = df[df['Urgence'] == 'Urgent']
    alertes_surveillance = df[df['Urgence'] == 'À surveiller']
    
    # Affichage des alertes urgentes
    if len(alertes_urgentes) > 0:
        st.subheader("🚨 Conventions Urgentes")
        for _, conv in alertes_urgentes.iterrows():
            col1, col2, col3 = st.columns([3, 2, 2])
            with col1:
                st.markdown(f"**{conv['Operation']}**")
                st.caption(f"Financeur: {conv['Financeur']}")
            with col2:
                st.markdown(f"💰 {format_montant(conv['Montant_Euro'])}")
                st.caption(f"Échéance: {conv['Date_Fin'].strftime('%d/%m/%Y')}")
            with col3:
                if st.button(f"📋 Voir détails", key=f"urgent_{conv['Numero_Operation']}"):
                    st.info("Détails de la convention...")
            st.markdown("---")
    
    # Affichage des conventions à surveiller
    if len(alertes_surveillance) > 0:
        st.subheader("⚠️ Conventions à Surveiller")
        for _, conv in alertes_surveillance.iterrows():
            col1, col2, col3 = st.columns([3, 2, 2])
            with col1:
                st.markdown(f"**{conv['Operation']}**")
                st.caption(f"Financeur: {conv['Financeur']}")
            with col2:
                st.markdown(f"💰 {format_montant(conv['Montant_Euro'])}")
                st.caption(f"Échéance: {conv['Date_Fin'].strftime('%d/%m/%Y')}")
            with col3:
                if st.button(f"📋 Voir détails", key=f"watch_details_{conv['Numero_Operation']}"):
                    st.info("Détails de la convention...")
            st.markdown("---")
    
    # Configuration des alertes
    st.subheader("⚙️ Configuration des Alertes")
    
    col1, col2 = st.columns(2)
    with col1:
        rappel_1_mois = st.checkbox("Rappel à 1 mois", value=True)
        rappel_3_mois = st.checkbox("Rappel à 3 mois", value=True)
    with col2:
        rappel_6_mois = st.checkbox("Rappel à 6 mois", value=True)
        email_alerts = st.checkbox("Alertes par email", value=False)
    
    if st.button("💾 Sauvegarder Configuration"):
        st.success("Configuration sauvegardée!")

# Page Rapports & Statistiques  
elif page == "📊 Rapports & Statistiques":
    st.title("📊 Rapports & Statistiques")
    
    df = st.session_state.conventions_data
    
    # Métriques avancées
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📋 Total Conventions", len(df))
    with col2:
        st.metric("💰 Montant Total", format_montant(df['Montant_Euro'].sum()))
    with col3:
        st.metric("📈 Montant Moyen", format_montant(df['Montant_Euro'].mean()))
    with col4:
        duree_moyenne = (df['Date_Fin'] - df['Date_Debut']).dt.days.mean()
        st.metric("📅 Durée Moyenne", f"{duree_moyenne:.0f} jours")
    
    # Graphiques avancés
    st.subheader("📈 Évolution des Montants")
    
    # Graphique temporel
    df_temp = df.copy()
    df_temp['Annee_Debut'] = df_temp['Date_Debut'].dt.year
    evolution = df_temp.groupby('Annee_Debut')['Montant_Euro'].sum().reset_index()
    
    fig_evolution = px.line(
        evolution, x='Annee_Debut', y='Montant_Euro',
        title="Évolution des montants par année"
    )
    st.plotly_chart(fig_evolution, use_container_width=True)
    
    # Analyse par financeur
    st.subheader("💼 Analyse par Financeur")
    
    col1, col2 = st.columns(2)
    
    with col1:
        financeur_stats = df.groupby('Financeur').agg({
            'Montant_Euro': ['sum', 'count', 'mean']
        }).round(0)
        financeur_stats.columns = ['Montant Total', 'Nb Conventions', 'Montant Moyen']
        st.dataframe(financeur_stats, use_container_width=True)
    
    with col2:
        fig_financeur = px.treemap(
            df, path=['Financeur'], values='Montant_Euro',
            title="Répartition des montants par financeur"
        )
        st.plotly_chart(fig_financeur, use_container_width=True)

# Page Configuration
elif page == "⚙️ Configuration":
    st.title("⚙️ Configuration")
    
    # Paramètres généraux
    st.subheader("🔧 Paramètres Généraux")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.selectbox("Langue", ["Français", "Anglais"])
        st.selectbox("Format de date", ["DD/MM/YYYY", "MM/DD/YYYY", "YYYY-MM-DD"])
    
    with col2:
        st.selectbox("Devise", ["EUR (€)", "USD ($)", "GBP (£)"])
        st.number_input("Seuil alerte (jours)", value=30, min_value=1, max_value=365)
    
    # Sauvegarde et restauration
    st.subheader("💾 Sauvegarde des Données")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📥 Exporter toutes les données"):
            data_json = st.session_state.conventions_data.to_json(orient='records', date_format='iso')
            st.download_button(
                label="💾 Télécharger JSON",
                data=data_json,
                file_name="conventions_backup.json",
                mime="application/json"
            )
    
    with col2:
        uploaded_file = st.file_uploader("📤 Importer des données", type=['json', 'csv'])
        if uploaded_file is not None:
            if st.button("🔄 Restaurer les données"):
                try:
                    if uploaded_file.name.endswith('.json'):
                        data = pd.read_json(uploaded_file)
                    else:
                        data = pd.read_csv(uploaded_file)
                    
                    st.session_state.conventions_data = data
                    st.success("✅ Données restaurées avec succès!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Erreur lors de l'import: {e}")
    
    # Réinitialisation
    st.subheader("🔄 Réinitialisation")
    
    if st.button("🗑️ Réinitialiser aux données de démonstration", type="secondary"):
        if st.button("⚠️ Confirmer la réinitialisation"):
            st.session_state.conventions_data = load_demo_data()
            st.success("✅ Données réinitialisées!")
            st.rerun()

# Footer
st.markdown("---")
st.markdown("""

    📋 Gestionnaire de Conventions - Version 1.0
    Développé avec ❤️ par Assistant IA | Powered by Streamlit

""", unsafe_allow_html=True)
