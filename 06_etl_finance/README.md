# 📊 Projet 6 : Pipeline ETL financier multi-sources

Ce projet met en place un **pipeline ETL complet** pour une institution financière souhaitant consolider ses données de marché afin d'analyser des indicateurs clés de performance (KPI) : revenus, rentabilité, risques liés aux fluctuations du marché.

Le pipeline agrège **3 sources de données hétérogènes** (API boursière, fichier Excel interne, base SQL référentielle), applique des **transformations avancées** (moyennes mobiles, volatilité, rendements quotidiens) et charge le résultat dans un **data warehouse répresentée ici par PostgreSQL** modélisé en **schéma en étoile**.

Le tout est **orchestré par Apache Airflow** (exécution quotidienne) et **visualisé via Metabase** (dashboards analytiques).

## 🎯 Contexte métier
Une institution financière consolide ses données pour analyser les KPI : revenus, rentabilité, risques.

## 🏗️ Sources
 - **Yahoo Finance** (via `yfinance`) : prix boursiers
 - **Excel** : objectifs internes
 - **PostgreSQL** : référentiel entreprises

## 🛠️ Stack
 - Python 
 - pandas 
 - yfinance 
 - PostgreSQL 
 - Airflow 
 - Docker 
 - Metabase

## 🚀 Lancement
```bash
docker compose up -d