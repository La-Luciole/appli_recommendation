
import streamlit as st
import requests
import json
import os
from dotenv import load_dotenv

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

# Récupérer la clé API
api_key = os.getenv('AZURE_API_KEY')

print("Répertoire de travail actuel:", os.getcwd())
print("Fichiers dans ce répertoire:", os.listdir())

# Fonction pour obtenir les recommandations depuis l'API
def get_recommendations(user_id,api_key):
    # URL de l'API avec la clé de fonction Azure
    url = f"https://recommandation-de-contenu.azurewebsites.net/api/recommend?user_id={user_id}&code={api_key}"

    try:
        response = requests.get(url)

        # Vérifie si la requête a réussi (statut 200)
        if response.status_code == 200:
            # Parse la réponse JSON
            data = response.json()
            return data
        else:
            # Si la requête échoue
            st.error(f"Erreur lors de la requête: {response.status_code}")
            return None

    except requests.exceptions.RequestException as e:
        st.error(f"Erreur de connexion: {e}")
        return None

# Fonction pour afficher les numéros d'articles suivis de l'icône dans des colonnes
def display_article_icons(article_ids):
    image_path = os.path.join(os.getcwd(), 'icone_article.png')

    # Créer une ligne de colonnes pour afficher les articles côte à côte
    cols = st.columns(5)  # Crée 5 colonnes
    
    # Afficher les numéros d'articles suivis de l'icône dans chaque colonne
    for i, article_id in enumerate(article_ids):
        with cols[i]:
            st.write(f"Article {article_id}")
            st.image(image_path, width=100)

# Titre de l'application
st.title("Recommandation de Contenu")

# Initialiser la session d'état pour garder l'ID de l'utilisateur
if 'user_id' not in st.session_state:
    st.session_state.user_id = None

# Demander l'ID de l'utilisateur
if st.session_state.user_id is None:
    user_id = st.number_input("Entrez votre identifiant utilisateur", min_value=1, step=1, value=None)  # Pas de valeur par défaut
else:
    user_id = st.session_state.user_id

# Si l'utilisateur saisit un ID, le stocker dans le session_state
if user_id and user_id != st.session_state.user_id:
    st.session_state.user_id = user_id
    st.session_state.recommendations_displayed = False  # État pour ne pas afficher les anciennes recommandations

# Si les recommandations ne sont pas encore affichées et que l'ID utilisateur est défini
if st.session_state.user_id and not st.session_state.get('recommendations_displayed', False):
    # Obtenir les recommandations
    data = get_recommendations(st.session_state.user_id,api_key=api_key)

    if data:
        # Afficher l'identifiant de l'utilisateur
        st.write(f"Votre identifiant est : {data['user_id']}")
        # Afficher le dernier article lu de l'utilisateur
        st.subheader(f"Votre dernier article lu :")
        # Afficher l'ID de l'article
        st.write(f"Article {data['last_article']}")
        # Afficher l'icône de l'article avec l'image locale
        st.image(os.path.join(os.getcwd(), 'icone_article.png'), width=100)

        # Afficher le texte pour les recommandations similaires
        st.subheader("Articles similaires recommandés :")
        # Afficher les icônes des articles recommandés côte à côte
        display_article_icons(data['recommendations'])
        # Marquer les recommandations comme affichées
        st.session_state.recommendations_displayed = True

        st.subheader("Visualisation des recommandations")
        graph_url = data.get('graph_url')  # Récupérer l'URL de l'image depuis la réponse

        if graph_url:
            # Afficher l'image depuis l'URL dans Streamlit
            st.image(graph_url, caption="Graphique des embeddings et recommandations", use_container_width=True)


        # Marquer les recommandations comme affichées
        st.session_state.recommendations_displayed = True

# Ajouter un bouton pour recommencer avec un nouvel identifiant
if st.button('Recommencer avec un nouvel identifiant'):
    # Réinitialiser l'ID utilisateur dans session_state
    st.session_state.user_id = None
    st.session_state.recommendations_displayed = False  # Réinitialiser l'état des recommandations
    st.rerun()  # Recharger l'application pour recommencer
