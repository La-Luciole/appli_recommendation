"""
Méthode 1 : Déploiement via Azure CLI
1. Ouvrir un terminal et se positionner dans le dossier de la fonction Azure
2. Se connecter à Azure (Si Azure CLI déjà configuré)
    az login --use-device-code 
    => ouvir le navigateur et entrer le code fourni
3. Déployer la fonction sur Azure
    func azure functionapp publish recommandation-de-contenu --python

Méthode 2 : Déploiement via le dépôt Git d'Azure

Vérification après déploiement :
Après le déploiement, tester la fonction en appelant l'URL de l'API :
    curl -X GET "https://recommandation-de-contenu.azurewebsites.net/api/recommend?user_id={user_id}&code={api_key}"
    Ou directement dans votre navigateur :
    "https://recommandation-de-contenu.azurewebsites.net/api/recommend?user_id={user_id}&code={api_key}"
"""

# 1. Imports
import logging
import json
import os
import io
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Force Matplotlib à utiliser un backend sans interface graphique
import matplotlib.pyplot as plt
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import azure.functions as func

# 2. Définition de l'app et décorateur
app = func.FunctionApp()

# 3. Récupération des variables d'environnement
CLICK_SAMPLE_PATH = os.getenv('CLICK_SAMPLE_PATH')
RECOMMANDATIONS_PATH = os.getenv('RECOMMANDATIONS_PATH')
EMBEDDINGS_PATH = os.getenv('EMBEDDINGS_PATH')
GRAPHS_SAS_URL = os.getenv("GRAPHS_SAS_URL")
CONTAINER_NAME = "graphs"

logging.info(f"CLICK_SAMPLE_PATH: {CLICK_SAMPLE_PATH}")
logging.info(f"RECOMMANDATIONS_PATH: {RECOMMANDATIONS_PATH}")
logging.info(f"EMBEDDINGS_PATH: {EMBEDDINGS_PATH}")
logging.info(f"GRAPHS_SAS_URL: {GRAPHS_SAS_URL}")


# 4. Fonctions auxiliaires pour récupérer un fichier depuis Azure Blob Storage et charger les données

# Fonction pour télécharger un fichier depuis Blob Storage dans la mémoire en utilisant une URL SAS
def download_blob_to_memory(url):
    blob_client = BlobClient.from_blob_url(url)
    download_stream = blob_client.download_blob()
    return download_stream.readall()

# Fonction pour charger les données en DataFrame
def load_data():
    logging.info("Début du téléchargement des fichiers depuis Blob Storage")
    
    try:
        # Télécharger les fichiers directement depuis Blob Storage dans la mémoire
        df_clicks_sample_data = download_blob_to_memory(CLICK_SAMPLE_PATH)
        logging.info("df_clicks_sample téléchargé avec succès")
        logging.info(f"Taille de df_clicks_sample_data : {len(df_clicks_sample_data)} octets")
        logging.info(f"Premiers octets de df_clicks_sample_data : {df_clicks_sample_data[:100]}")

        df_recommandations_data = download_blob_to_memory(RECOMMANDATIONS_PATH)
        logging.info("df_recommandations téléchargé avec succès")
        logging.info(f"Taille de df_recommandations_data : {len(df_recommandations_data)} octets")
        logging.info(f"Premiers octets de df_recommandations_data : {df_recommandations_data[:100]}")

        embeddings_data = download_blob_to_memory(EMBEDDINGS_PATH)
        logging.info("embeddings_data téléchargé avec succès")
        logging.info(f"Taille des embeddings téléchargés : {len(embeddings_data)} octets")
        logging.info(f"Premiers octets des embeddings : {embeddings_data[:10]}")

        if not df_clicks_sample_data or not df_recommandations_data or not embeddings_data:
            logging.error("Erreur : Un ou plusieurs fichiers n'ont pas été téléchargés correctement")
            return func.HttpResponse(
                json.dumps({"error": "Un ou plusieurs fichiers n'ont pas été téléchargés correctement"}),
                status_code=500,
                mimetype="application/json"
            )
        else :
            logging.info("Données téléchargées. Chargement des fichiers...")

        # Charger les embeddings depuis la mémoire
        try:
            embeddings_2D = np.load(io.BytesIO(embeddings_data), allow_pickle=True)
            logging.info(f"Embeddings chargés. Type : {type(embeddings_2D)}, Dimensions : {embeddings_2D.shape if hasattr(embeddings_2D, 'shape') else 'N/A'}")
        except ValueError as e:
            logging.error(f"Erreur lors du chargement des embeddings : {e}")

        # Charger les autres fichiers CSV et JSON depuis la mémoire
        try:
            df_clicks_sample = pd.read_csv(io.BytesIO(df_clicks_sample_data), sep=',', low_memory=False)
            logging.info("df_clicks_sample chargé avec succès")
            logging.info(f"df_clicks_sample info: {df_clicks_sample.info()}")  # Ajout du log pour df_clicks_sample
            logging.info(f"df_clicks_sample shape: {df_clicks_sample.shape}")  # Ajout du log pour la forme de df_clicks_sample
            logging.info(f"Exemples d'user_id : {df_clicks_sample['user_id'].unique()[:10]}")

            # Vérifier si l'user_id 42 existe dans df_clicks_sample
            logging.info(f"Existe-t-il un user_id 42 dans df_clicks_sample ? {42 in df_clicks_sample['user_id'].values}")
            
            # Afficher les lignes correspondant à user_id 42
            logging.info(f"Lignes correspondant à user_id 42 dans df_clicks_sample:\n{df_clicks_sample[df_clicks_sample['user_id'] == 42]}")
            
        except Exception as e:
            logging.error(f"Erreur lors du chargement de df_clicks_sample : {e}")

        try:
            df_recommandations = pd.read_json(io.BytesIO(df_recommandations_data))
            logging.info("df_recommandations chargé avec succès")
            logging.info(f"df_recommandations info: {df_recommandations.info()}")  # Ajout du log pour df_recommandations
            logging.info(f"df_recommandations shape: {df_recommandations.shape}")  # Ajout du log pour la forme de df_recommandations
            logging.info(f"Exemples d'user_id : {df_recommandations['user_id'].unique()[:10]}")
        except Exception as e:
            logging.error(f"Erreur lors du chargement de df_recommandations : {e}")

        logging.info("Fichiers chargés avec succès.")

    except Exception as e:
        logging.error(f"Erreur lors du chargement des données: {e}")
        return func.HttpResponse(
            json.dumps({"error": "Erreur lors du chargement des données"}),
            status_code=500,
            mimetype="application/json"
        )

    if not df_clicks_sample_data or not df_recommandations_data or not embeddings_data:
        logging.error("Erreur : Un ou plusieurs fichiers n'ont pas été téléchargés correctement")
    else :
        logging.info("Données téléchargées. Chargement des fichiers...")

    return df_clicks_sample, df_recommandations, embeddings_2D

# 5. Fonction main avec décorateur (Fonction principale de l'Azure Function)
@app.route(route="recommend")
@app.function_name(name="recommend_articles")
def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Requête reçue pour récupérer des recommandations utilisateur.")

    # Récupérer la chaîne de connexion depuis les variables d'environnement
    connection_string = os.getenv("AzureWebJobsStorage")
    if connection_string is None:
        raise ValueError("La chaîne de connexion est manquante ou incorrecte")
    # Initialiser le client BlobServiceClient
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)

    try:
        # Récupérer le paramètre 'user_id' de la requête
        user_id_str = req.params.get('user_id')

        if user_id_str is None:
            return func.HttpResponse("Paramètre 'user_id' manquant.", status_code=400)

        if user_id_str is None:
            return func.HttpResponse("Paramètre 'user_id' manquant.", status_code=400)

        try:
            user_id = int(user_id_str)  # Conversion explicite
            logging.info(f"User ID reçu : {user_id} (type: {type(user_id)})")
        except (TypeError, ValueError):
            logging.warning(f"user_id invalide : {user_id_str}")
            return func.HttpResponse(
                json.dumps({'message': f"user_id invalide : {user_id_str}"}),
                status_code=400,
                mimetype="application/json"
            )

        # Charger les données nécessaires depuis le Blob Storage
        df_clicks_sample, df_recommandations, embeddings_2D = load_data()
        
        # Appeler les fonctions pour générer les résultats
        user_history, last_article = get_user_history(user_id, df_clicks_sample)
        if not user_history:
            return func.HttpResponse(
                json.dumps({"message": f"Aucun historique trouvé pour l'utilisateur {user_id}."}),
                status_code=404,
                mimetype="application/json"
            )

        reco_ids, last_article, scores = get_recommendations(user_id, df_clicks_sample, df_recommandations)
        
        # Générer un graphique des embeddings
        graph_buffer = plot_user_embeddings(user_id, df_clicks_sample, df_recommandations, embeddings_2D)
        
        # Sauvegarder le graphique dans le Blob Storage
        blob_service_client = BlobServiceClient.from_connection_string(os.getenv("AzureWebJobsStorage"))
        graph_blob_client = blob_service_client.get_blob_client(container=CONTAINER_NAME, blob=f"{user_id}_graph.png")
        graph_blob_client.upload_blob(graph_buffer.read(), overwrite=True)
        
        # Définir l'URL de base du graph sans le SAS Token
        base_url = "https://dashboardsaea6.blob.core.windows.net/graphs"
        # Extraire la partie SAS Token de l'URL
        sas_token = GRAPHS_SAS_URL.split('?')[1]
        
        # Construire la réponse JSON
        response_data = {
            "user_id": user_id,
            "user_history": user_history,
            "last_article": last_article,
            "recommendations": reco_ids,
            "scores": scores,
            "graph_url": f"{base_url}/{user_id}_graph.png?{sas_token}"
        }
        
        return func.HttpResponse(json.dumps(response_data), mimetype="application/json", status_code=200)
    
    except Exception as e:
        logging.error(f"Erreur inattendue : {e}")
        return func.HttpResponse("Erreur interne du serveur.", status_code=500)

# 6. Autres fonctions

# Fonction pour récupérer l'historique d'un utilisateur et l'id du dernier article consulté
def get_user_history(user_id, df_clicks_sample):
    logging.info(f"Recherche de l'historique pour l'utilisateur {user_id}.")

    # Ajout de debug pour les types
    logging.info(f"Type de `user_id` reçu : {type(user_id)}")
    logging.info(f"Type de `df_clicks_sample['user_id']` : {df_clicks_sample['user_id'].dtype}")
    
    if user_id not in df_clicks_sample['user_id'].unique():
        logging.warning(f"Utilisateur {user_id} non trouvé dans df_clicks_sample.")
        return [], None  # Retourne une liste vide et None
        
    user_clicks = df_clicks_sample[df_clicks_sample['user_id'] == user_id]
    if user_clicks.empty:
        logging.warning(f"L'utilisateur {user_id} n'a pas d'historique de clics.")
        return [], None
    
    user_history = user_clicks['click_article_id'].unique().tolist()
    last_article = user_history[-1] if user_history else None

    logging.info(f"Historique trouvé pour l'utilisateur {user_id}: {user_history}")
    
    return user_history, last_article

# Fonction de recommandation basée sur le contenu
def get_recommendations(user_id, df_clicks_sample, df_recommandations, top_n=5):
    logging.info(f"Récupération des recommandations pour l'utilisateur {user_id}.")

    user_history, last_article = get_user_history(user_id, df_clicks_sample)
    if not user_history:
        return [], None, []
    logging.info(f"Historique utilisateur {user_id}: {user_history}")
    
    # Récupération des recommandations pré-calculées
    user_recommendations = df_recommandations[df_recommandations['user_id'] == user_id]
    if user_recommendations.empty:
        logging.error(f"Aucune recommandation trouvée pour l'utilisateur {user_id}.")
        raise ValueError("Aucune recommandation trouvée pour cet utilisateur.")
    
    reco_ids = user_recommendations['article_id'].tolist()[:top_n]
    scores = user_recommendations['similarity_score'].tolist()[:top_n]

    logging.info(f"Recommandations générées pour l'utilisateur {user_id}: {reco_ids} avec scores {scores}")
    
    return reco_ids, last_article, scores

# Fonction pour la visualisation des embeddings
def plot_user_embeddings(user_id, df_clicks_sample, df_recommandations, embeddings_2D):
    logging.info(f"Création de la visualisation des embeddings pour l'utilisateur {user_id}.")
    user_history, last_article = get_user_history(user_id, df_clicks_sample)
    reco_ids, _, scores = get_recommendations(user_id, df_clicks_sample, df_recommandations)

    logging.info(f"Historique de l'utilisateur {user_id}: {user_history}, Recommandations: {reco_ids}")

    fig, axes = plt.subplots(1, 2, figsize=(15, 6))
    fig.suptitle(f"Visualisation des Embeddings et Recommandations pour l'utilisateur {user_id}", fontsize=14, fontweight='bold')

    all_points = embeddings_2D
    user_history_points = embeddings_2D[user_history]
    last_point = embeddings_2D[last_article] if last_article is not None else None
    reco_points = embeddings_2D[reco_ids]

    # Graphique 1 : Vue globale
    ax = axes[0]
    ax.scatter(all_points[:, 0], all_points[:, 1], s=5, color='gray', alpha=0.3, label="Tous les articles")
    ax.scatter(user_history_points[:, 0], user_history_points[:, 1], color='blue', label="Articles consultés", s=50, alpha=0.6)
    if last_point is not None:
        ax.scatter(last_point[0], last_point[1], color='green', label='Dernier article consulté', s=150, edgecolors='black')
    ax.scatter(reco_points[:, 0], reco_points[:, 1], color='orange', label='Recommandations', s=50, edgecolors='black')
    ax.set_title("Vue globale")
    ax.set_xlabel("Composante 1")
    ax.set_ylabel("Composante 2")
    ax.axhline(0, color='black', linewidth=0.5)
    ax.axvline(0, color='black', linewidth=0.5)
    ax.legend()
    ax.grid(True)

    # Graphique 2 : Zoom sur recommandations
    ax_zoom = axes[1]
    if last_point is not None:
        ax_zoom.scatter(last_point[0], last_point[1], color='green', label='Dernier article consulté', s=100, edgecolors='black')
    ax_zoom.scatter(reco_points[:, 0], reco_points[:, 1], color='orange', label='Recommandations', s=100, edgecolors='black')
    if last_point is not None:
        for i, (x, y) in enumerate(reco_points):
            ax_zoom.plot([last_point[0], x], [last_point[1], y], color='black', linestyle="dashed", alpha=0.5)
            ax_zoom.annotate(f'{scores[i]:.2f}', (x, y), textcoords="offset points", xytext=(5,5), ha='center')

    points_to_consider = [last_point] + list(reco_points) if last_point is not None else list(reco_points)
    x_coords, y_coords = zip(*points_to_consider)
    x_min, x_max = min(x_coords), max(x_coords)
    y_min, y_max = min(y_coords), max(y_coords)
    padding_x = 0.1 * (x_max - x_min)
    padding_y = 0.1 * (y_max - y_min)
    ax_zoom.set_xlim(x_min - padding_x, x_max + padding_x)
    ax_zoom.set_ylim(y_min - padding_y, y_max + padding_y)

    ax_zoom.set_title("Zoom sur le dernier article et ses recommandations")
    ax_zoom.set_xlabel("Composante 1")
    ax_zoom.set_ylabel("Composante 2")
    ax_zoom.axhline(0, color='black', linewidth=0.5)
    ax_zoom.axvline(0, color='black', linewidth=0.5)
    ax_zoom.legend()
    ax_zoom.grid(True)

    plt.tight_layout()

    # Sauvegarder l'image dans un objet en mémoire pour la réponse
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)  # Revenir au début du buffer
    plt.close(fig)
    return buf
