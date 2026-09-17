# 📊 Projet 5 : Pipeline ETL pour analyse des ventes

## 📝 Description du projet

Ce projet met en place un **pipeline ETL complet** pour une entreprise e-commerce souhaitant analyser ses données de vente. Il centralise des données issues de plusieurs sources dans un **entrepôt de données** (data warehouse) pour permettre des analyses décisionnelles.

## 🎯 Contexte métier

Une entreprise de e-commerce veut identifier :
- Les produits les plus performants
- Les périodes de forte activité
- Les tendances émergentes

Pour cela, elle doit centraliser ses données (ventes, produits, clients) dans un entrepôt de données.

## ⚙️ Étapes du pipeline

1. **Extract** - Récupérer les données depuis plusieurs sources (CSV, API REST, base relationnelle)
2. **Transform** - Nettoyer, enrichir, agréger les données (Pandas)
3. **Load** - Charger dans un entrepôt de données avec un schéma en étoile
4. **Orchestrate** - Automatiser avec Apache Airflow
5. **Monitor** - Surveiller les performances avec Prometheus et Grafana

## 🛠️ Technologies utilisées

**Langage**: Python 3
**Extraction**: Pandas, Requests
**Transformation**: Pandas
**Entrepôt**: Redshift local (émulateur PostgreSQL 16)
**Orchestration**: Apache Airflow (LocalExecutor)
**Monitoring**: Prometheus + Grafana + StatsD exporter
**Conteneurisation**: Docker + Docker Compose

