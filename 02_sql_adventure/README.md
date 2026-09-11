# 🗄️ Projet 2 : L'aventure SQL 

## 📝 Description
Conception, modélisation et requêtage d'une base de données relationnelle pour un système de gestion de bibliothèque (`library_db`). L'objectif est de valider la maîtrise du SQL avancé avec PostgreSQL.

## ⚙️ Caractéristiques techniques
1. **Schéma Relationnel (DDL) :** Tables `authors`, `books`, `borrowers(emprunteurs)`, et `borrowings(emprunts)` avec clés primaires et clés étrangères configurées en cascade (`ON DELETE CASCADE`).
2. **Jeu de données (DML) :** Insertion de données cohérentes pour valider les analyses temporelles (calculs basés sur des intervalles de jours).
3. **Requêtes Analytiques :** Utilisation de jointures multiples (`INNER JOIN`, `LEFT JOIN`), d'agrégations (`COUNT`, `GROUP BY`) et de filtres chronologiques.
4. **Optimisation :** Création d'index `B-Tree` stratégiques sur les clés étrangères et critères de filtres, et mise en place d'une vue (`view_active_borrowings`) pour simplifier les requêtes récurrentes.

## 🛠️ Technologies
* **SGBDR :** PostgreSQL
