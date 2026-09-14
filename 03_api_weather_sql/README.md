# 🌤️ Projet 3 : Ingestion de Données API Météo & Stockage SQL

## 📝 Description du projet
Ce projet consiste à concevoir un pipeline de données automatisé pour collecter les prévisions météorologiques de plusieurs destinations touristiques. Les données brutes sont récupérées en temps réel depuis une API externe(OpenWeather), nettoyées, puis stockées de manière structurée dans une base de données relationnelle.

## ⚙️ Objectifs techniques & Étapes à réaliser
1. **Extraction de données (API REST) :** Connexion sécurisée à l'API OpenWeather à l'aide d'une clé d'accès et récupération des flux au format **JSON**.
2. **Transformation & Qualité (Python) :** Nettoyage des données extraites, traitement des valeurs manquantes, normalisation des formats (conversion des températures, gestion des timestamps) à l'aide de Python.
3. **Modélisation & Chargement (PostgreSQL) :** Conception du schéma physique des tables météo et insertion efficace des données nettoyées.
4. **Conteneurisation & Orchestration (Futur) :** Isolation du script via **Docker** et planification des extractions quotidiennes avec **Apache Airflow**.

## 🛠️ Technologies cibles
* **Langage :** Python 3 (`requests`, `psycopg3` ou `SQLAlchemy`)
* **Source des données :** OpenWeather API
* **Stockage :** PostgreSQL
* **Infrastructure :** Docker, Apache Airflow
