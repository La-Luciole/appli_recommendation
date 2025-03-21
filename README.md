# appli_recommendation
## Projet 10 : Réaliser une application de recommandation de contenu

### Scénario de la mission
Une start-up veut encourager la lecture en recommandant des contenus pertinents pour ses utilisateurs.  
Vous êtes en pleine construction d’un premier MVP qui prendra la forme d’une application.  
Dans un premier temps, vous souhaitez tester une solution de recommandation d’articles et de livres à des particuliers.  

Comme vous ne disposez pas à ce jour de données utilisateurs, vous allez utiliser des données disponibles en ligne pour développer votre MVP :  
https://www.kaggle.com/datasets/gspmoreira/news-portal-user-interactions-by-globocom#clicks_sample.csv

Ces données représentent les interactions des utilisateurs avec les articles disponibles.  
Elles contiennent des informations sur les articles (par exemple le nombre de mots dans l’article), ainsi que les informations sur les sessions des utilisateurs (par exemple heures de début et de fin) et les interactions des utilisateurs avec les articles (sur quel article l’utilisateur a-t-il cliqué lors de sa session ?).

Dans une logique de MVP, vous avez identifié la fonctionnalité la plus critique pour lancer votre application : 

"En tant qu’utilisateur de l’application, je vais recevoir une sélection de cinq articles."

Vous avez également identifié que la prise en compte de l’ajout de nouveaux utilisateurs et de nouveaux articles dans l’architecture cible de votre produit est déterminante.

Vous allez utiliser une architecture serverless dans le cloud avec Azure Functions.  
Il faudra pour cela créer une API pour développer puis exposer le système de recommandation.  
Pour faire le lien entre l’application et le système de recommandation, vous devez créer une Azure Functions.

Pour finir, vous développerez une interface qui liste les id des users et affiche les résultats des 5 suggestions d’articles, suite à appel de l’Azure Functions.

### Objectifs du projet
- Développer une première version de votre système de recommandation sous forme d’Azure Functions;
- Réaliser une application simple de gestion du système de recommandation (interface d’affichage d’une liste d’id utilisateurs, d’appel Azure functions pour l’id choisi, et d’affichage des 5 articles recommandés)
- Stocker les scripts développés dans un dossier GitHub ;
- Synthétiser vos premières réflexions sur :
    - L’architecture technique et la description fonctionnelle de votre application à date, et le système de recommandation,
    - L’architecture cible pour pouvoir prendre en compte l’ajout de nouveaux utilisateurs ou de nouveaux articles.
