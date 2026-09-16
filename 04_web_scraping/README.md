# 🕷️ Projet 4 : Web Scraping & Ingestion de données

## 📝 Description du projet

Ce projet a pour objectif de construire un pipeline complet de **collecte de données web**, allant de l'extraction HTML jusqu'au stockage dans une base NoSQL.

Les données sont extraites d'un site d'entraînement public (`books.toscrape.com`), nettoyées, normalisées, puis stockées dans **MongoDB** pour permettre des analyses.

## 🎯 Contexte métier

Une plateforme d'e-commerce souhaite analyser les avis de ses concurrents pour mieux comprendre les retours clients sur des produits similaires.

## ⚙️ Étapes réalisées

1. **Extraction Web (Scraping)**
   - Analyse de la structure HTML des pages catalogue et produit
   - Ciblage des éléments d'intérêt via sélecteurs CSS (`article.product_pod`, `p.price_color`, `p.star-rating`)
   - Pagination automatique (25 pages, 500 livres)

2. **Nettoyage & Transformation**
   - Extraction des valeurs numériques via regex (robuste à l'encodage)
   - Conversion des types (`float`, `int`)
   - Génération d'une clé métier unique (`book_id`)
   - Horodatage UTC (`scraped_at`) pour la traçabilité

3. **Persistance (MongoDB)**
   - Conception d'une collection de documents JSON-like
   - Index UNIQUE sur `book_id` pour empêcher les doublons
   - Index sur `price` et `rating` pour accélérer les requêtes

4. **Analyse**
   - Requêtes d'agrégation MongoDB (`$group`, `$avg`, `$sum`)
   - Top livres par prix, distribution des notes, statistiques

## 🛠️ Technologies utilisées

- **Langage** : Python 3
- **Scraping** : Requests + BeautifulSoup4 + lxml
- **Stockage** : MongoDB 7.0 (via Docker)
- **Driver MongoDB** : PyMongo
- **Configuration** : python-dotenv
- **Conteneurisation** : Docker + Docker Compose

