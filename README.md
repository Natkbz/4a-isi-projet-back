# Pol-eat-heck — Back-end (`4a-isi-projet-back`)

API REST développée avec **FastAPI** et **SQLModel** pour **Pol-eat-heck**, l'application web de gestion de menus hebdomadaires et de réservation de produits.

---

## Équipe & Dépôts liés

- **Collaborateurs :** `@Natkbz` (Back-end), `@Tolram89` (Base de données), `@dcr29` (Front-end)
- **Enseignant / Encadrant :** `@esirem-chassel`
- **Base de données (SQLite / SQLModel) :** [4a-isi-projet-db](https://github.com/Tolram89/4a-isi-projet-db)
- **Front-end (HTML / CSS / JS) :** [4a-isi-projet-front](https://github.com/dcr29/4a-isi-projet-front)

---

## Stack technique

- **Langage :** Python 3
- **Framework Web / API :** FastAPI
- **ORM & Validation :** SQLModel / Pydantic
- **Base de données :** SQLite
- **Authentification :** Jetons JWT (`Authorization: Bearer <token>`) et hachage sécurisé des mots de passe

---

## Fonctionnalités principales de l'API

- **Catalogue public (sans authentification) :** consultation des produits actifs, des menus disponibles sur la période, des catégories et des jours de fermeture.
- **Authentification & Comptes :** inscription (`POST /register`) avec génération d'un mot de passe aléatoire unique transmis une seule fois, connexion (`POST /login`), consultation du profil (`GET /users/me`) et modification du mot de passe (`PATCH /users/password`).
- **Réservations & Commandes :** création de commandes (`POST /orders`) pour une date de retrait (`pickup_date`) avec vérification atomique des stocks, des jours de fermeture et des dates de validité des menus, plus suivi de l'historique (`GET /orders`).
- **Administration :** gestion complète du catalogue (produits, catégories, menus avec suppression logique `is_deleted`), déclaration des jours de fermeture, blocage de comptes utilisateurs (`is_blocked`) et suivi/mise à jour des statuts de commandes (`pending`, `completed`, `cancelled`, `no_show`).
- **Création des administrateurs :** effectuée exclusivement via un script en ligne de commande (CLI) sur le serveur.

---
