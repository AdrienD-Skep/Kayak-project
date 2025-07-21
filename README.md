# Plan Your Trip with Kayak

## Project Overview
Kayak est un moteur de recherche de voyages qui aide les utilisateurs à planifier leur prochain voyage au meilleur prix.

L’équipe marketing de Kayak souhaite aller plus loin en créant une application capable de recommander automatiquement les meilleures destinations et hôtels en fonction des conditions météorologiques et des caractéristiques des hébergements.


## Data Collection
- Géocodage des villes via l’API Nominatim d’OpenStreetMap (/search)
- Prévisions météo pour chaque ville via l’API OpenWeatherMap (/forecast) sur 5 jours à intervalles de 3 heures
- Développement d’une spider Scrapy pour extraire les 20 meilleurs hôtels par ville depuis Booking.com
- Extraction des données hôtelières : nom, URL, coordonnées, adresse, description, note utilisateur, nombre d’étoiles etc

## Weather Scoring
Pour chaque ville, on calcule un score météo basé sur 7 critères, chacun comparé à une valeur idéale (ex. 25 °C pour la température). Plus la différence est faible, plus la note est basse. Chaque critère est associé à un poids selon son importance : la pluie et la neige (poids=5) influencent davantage le score que la visibilité (poids=2). Le score final est la somme de ces notes normalisé, donc un résultat bas indique un temps favorable.

## Data Storage & ETL
Stockage initial des CSV bruts dans un bucket AWS S3

Processus ETL :
- Suppression des valeurs manquantes et des doublons
- Élimination des colonnes inutiles
- Conversion des types de données

Chargement final dans une base de données AWS RDS :
- Table cities : informations météo et géographiques
- Table hotels : détails des hôtels avec clé étrangère vers cities

## Application Features
- Identification automatique des 5 villes affichant les conditions météo les plus favorables
- Sélection et recommandation des 20 meilleurs hôtels pour chaque ville
- Affichage de détails complets pour chaque établissement
