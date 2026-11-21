# Routes API — Pol-eat-heck

## Conventions, codes et objets partagés

### Conventions

- **Format des échanges :** Toutes les données envoyées et reçues sont au format `application/json`.
- **Format des dates :**
  - `Date` : format `YYYY-MM-DD` (ex. `"2026-11-18"`).
  - `DateTime` : format `YYYY-MM-DDTHH:MM:SSZ` (ex. `"2026-11-18T12:00:00Z"`).
- **Authentification :** Les routes protégées attendent un en-tête HTTP `Authorization: Bearer <security_token>` (JWT obtenu via `/login` ou `/register`). La vérification du statut de blocage (`is_blocked`) est effectuée en base à chaque requête protégée afin qu'un blocage administrateur prenne effet immédiatement.
- **Alignement Base de Données et Schémas de réponse :** Les noms des champs respectent les colonnes définies dans la conception de base de donnée. Des schémas Pydantic sont utilisés pour formater les relations imbriquées (`products` et `menus` au lieu de `order_products`, `order_menus` et `menu_products`) et inclure les libellés historiques dans les commandes.
- **Suppression logique:** Les produits et menus ne sont pas supprimés physiquement de la base afin de préserver l'historique des commandes passées. Leur attribut `is_deleted` passe à `true`.

---

### Règles métier globales

1. **Commandabilité d'un produit :** Un produit ne peut être commandé que si `is_available == true`, `is_deleted == false` et que son `stock` couvre la quantité demandée.
2. **Validité et commandabilité d'un menu :**
   - Un menu est permanent lorsque `end_date` est `null`, limité à un seul jour lorsque `start_date == end_date`, ou valide sur un intervalle entre `start_date` et `end_date`.
   - Lors d'une commande (`POST /orders`), la validité du menu est vérifiée par rapport à la date de retrait (`pickup_date`) : on doit avoir `start_date <= pickup_date` et (`end_date is null` ou `pickup_date <= end_date`).
   - Un menu n'est commandable que si `is_available == true`, `is_deleted == false`, qu'il est valide à la date `pickup_date`, et que tous les produits qui le composent sont disponibles, non supprimés et en stock suffisant.
3. **Agrégation et gestion atomique des stocks :**
   - Lors de `POST /orders`, le back-end agrège les quantités nécessaires par `product_id` (en additionnant les produits commandés à l'unité et ceux inclus dans les menus commandés) avant de vérifier le stock disponible.
   - La vérification des stocks, la création de la commande et la décrémentation des stocks s'exécutent dans une transaction SQLite atomique.
   - Lorsqu'une commande passe au statut `cancelled`, les stocks de tous les produits concernés (à l'unité et via les menus) sont réincrémentés. En revanche, le passage au statut `no_show` ne réincrémente pas les stocks (marchandise considérée comme préparée ou perdue).

---

### Codes de réponse

| Code | Signification | Cas d'usage dans l'application |
| :--- | :--- | :--- |
| **200** | **OK** | Requête réussie avec données retournées (`GET`, `PUT`, `PATCH`, `POST /login`). |
| **201** | **Created** | Ressource créée avec succès en base de données (`POST`). |
| **204** | **No Content** | Opération réussie sans corps de réponse (`DELETE`, changement de mot de passe). |
| **400** | **Bad Request** | Règle métier non respectée (stock insuffisant, produit/menu indisponible ou hors période de validité, jour de fermeture, date passée, commande vide, transition de statut interdite, ancien mot de passe erroné). |
| **401** | **Unauthorized** | Token manquant, invalide ou expiré, ou identifiants de connexion incorrects. |
| **403** | **Forbidden** | Accès refusé : rôle administrateur requis ou compte utilisateur bloqué (`is_blocked: true`). |
| **404** | **Not Found** | Ressource introuvable en base de données (identifiant `{id}` inexistant). |
| **409** | **Conflict** | Conflit d'unicité en base (nom d'utilisateur déjà pris, catégorie existante, jour de fermeture déjà enregistré). |
| **422** | **Unprocessable Entity** | Erreur de validation de schéma FastAPI/Pydantic (champ obligatoire manquant, mauvais type de donnée, valeur `null` interdite ou contrainte de borne non respectée : `price < 0`, `stock < 0`, `quantity < 1`). |

---

### Objets partagés

#### **User**
```json
{
  "id": "int",
  "username": "string",
  "role": "string ('standard' | 'admin')",
  "is_blocked": "bool",
  "created_at": "DateTime"
}
```

#### **UserRegistered** *(retourné uniquement à l'inscription)*
```json
{
  "token": "string",
  "user": {
    "id": "int",
    "username": "string",
    "role": "string ('standard')",
    "is_blocked": "bool",
    "created_at": "DateTime"
  },
  "generated_password": "string"
}
```

#### **Category**
```json
{
  "id": "int",
  "name": "string"
}
```

#### **Product**
```json
{
  "id": "int",
  "category_id": "int | null",
  "name": "string",
  "description": "string | null",
  "price": "float",
  "stock": "int",
  "is_available": "bool",
  "is_deleted": "bool"
}
```

#### **MenuProductItem** *(liaison produit/quantité dans un menu)*
```json
{
  "product_id": "int",
  "quantity": "int"
}
```

#### **Menu**
```json
{
  "id": "int",
  "name": "string",
  "description": "string | null",
  "price": "float",
  "start_date": "Date",
  "end_date": "Date | null",
  "is_available": "bool",
  "is_deleted": "bool",
  "available_stock": "int",
  "products": [
    {
      "product_id": "int",
      "quantity": "int"
    }
  ]
}
```
> *Note : `available_stock` est un champ calculé indiquant le nombre maximal de menus commandables selon les stocks et la disponibilité de ses produits constitutifs (`0` si un produit composant est épuisé, indisponible ou supprimé).*

#### **ClosureDay**
```json
{
  "id": "int",
  "closure_date": "Date",
  "reason": "string | null"
}
```

#### **OrderCreate** *(payload envoyé par le client pour passer commande)*
```json
{
  "pickup_date": "Date",
  "products": [
    {
      "product_id": "int",
      "quantity": "int"
    }
  ],
  "menus": [
    {
      "menu_id": "int",
      "quantity": "int"
    }
  ]
}
```

#### **Order** *(commande complète retournée par le serveur)*
```json
{
  "id": "int",
  "user_id": "int",
  "created_at": "DateTime",
  "pickup_date": "Date",
  "status": "string ('pending' | 'completed' | 'cancelled' | 'no_show')",
  "products": [
    {
      "id": "int",
      "product_id": "int",
      "product_name": "string",
      "quantity": "int",
      "unit_price": "float"
    }
  ],
  "menus": [
    {
      "id": "int",
      "menu_id": "int",
      "menu_name": "string",
      "quantity": "int",
      "unit_price": "float"
    }
  ]
}
```
> *Note : `product_name` et `menu_name` sont résolus côté serveur afin que l'historique reste lisible même si l'article est ensuite passé à `is_deleted: true`.*

#### **ErrorResponse** *(format standard des erreurs FastAPI)*
```json
{
  "detail": "string"
}
```

---

## Routes sans authentification

### GET /products

Récupère la liste des produits actifs (`is_deleted == false`).

| **Client request** | |
| :--- | :--- |
| URL | `/products` |
| Method | `GET` |
| Authorization | Aucune |
| Content-Type | Aucun |
| Body | Aucun |

| **Server response** | |
| :--- | :--- |
| Content-Type | `application/json` |
| Body | `[Product]` |
| Success Code | `200 OK` |
| Error Codes | Aucun (renvoie `[]` si aucun produit actif) |

---

### GET /menus

Récupère la liste des menus actifs (`is_deleted == false`) avec leur composition et leur `available_stock`.

| **Client request** | |
| :--- | :--- |
| URL | `/menus` |
| Method | `GET` |
| Authorization | Aucune |
| Content-Type | Aucun |
| Body | Aucun |

| **Server response** | |
| :--- | :--- |
| Content-Type | `application/json` |
| Body | `[Menu]` |
| Success Code | `200 OK` |
| Error Codes | Aucun (renvoie `[]` si aucun menu actif) |

---

### GET /categories

Récupère l'ensemble des catégories de produits.

| **Client request** | |
| :--- | :--- |
| URL | `/categories` |
| Method | `GET` |
| Authorization | Aucune |
| Content-Type | Aucun |
| Body | Aucun |

| **Server response** | |
| :--- | :--- |
| Content-Type | `application/json` |
| Body | `[Category]` |
| Success Code | `200 OK` |
| Error Codes | Aucun (renvoie `[]` si aucune catégorie) |

---

### GET /closures

Récupère la liste des jours de fermeture enregistrés.

| **Client request** | |
| :--- | :--- |
| URL | `/closures` |
| Method | `GET` |
| Authorization | Aucune |
| Content-Type | Aucun |
| Body | Aucun |

| **Server response** | |
| :--- | :--- |
| Content-Type | `application/json` |
| Body | `[ClosureDay]` |
| Success Code | `200 OK` |
| Error Codes | Aucun (renvoie `[]` si aucune fermeture) |

---

## Authentification et profil utilisateur

### POST /register

Crée un compte utilisateur avec le rôle `standard`, génère un mot de passe aléatoire unique (transmis une seule fois) et connecte l'utilisateur.

| **Client request** | |
| :--- | :--- |
| URL | `/register` |
| Method | `POST` |
| Authorization | Aucune |
| Content-Type | `application/json` |
| Body | `{ "username": "string" }` |

| **Server response** | |
| :--- | :--- |
| Content-Type | `application/json` |
| Body | `UserRegistered` |
| Success Code | `201 Created` |
| Error Codes | `409 Conflict` (nom d'utilisateur déjà existant)<br>`422 Unprocessable Entity` (champ `username` manquant ou vide) |

---

### POST /login

Authentifie un utilisateur (`standard` ou `admin`) et retourne un jeton JWT.

| **Client request** | |
| :--- | :--- |
| URL | `/login` |
| Method | `POST` |
| Authorization | Aucune |
| Content-Type | `application/json` |
| Body | `{ "username": "string", "password": "string" }` |

| **Server response** | |
| :--- | :--- |
| Content-Type | `application/json` |
| Body | `{ "token": "string", "user": User }` |
| Success Code | `200 OK` |
| Error Codes | `401 Unauthorized` (identifiant ou mot de passe incorrect)<br>`403 Forbidden` (compte bloqué par un administrateur)<br>`422 Unprocessable Entity` (format de requête invalide) |

---

### GET /users/me

Permet au front-end de récupérer les informations et le rôle de l'utilisateur actuellement connecté à partir de son token.

| **Client request** | |
| :--- | :--- |
| URL | `/users/me` |
| Method | `GET` |
| Authorization | `Bearer <security_token>` |
| Content-Type | Aucun |
| Body | Aucun |

| **Server response** | |
| :--- | :--- |
| Content-Type | `application/json` |
| Body | `User` |
| Success Code | `200 OK` |
| Error Codes | `401 Unauthorized` (token absent, invalide ou expiré)<br>`403 Forbidden` (compte bloqué) |

---

### PATCH /users/password

Permet à un utilisateur connecté de modifier son propre mot de passe.

| **Client request** | |
| :--- | :--- |
| URL | `/users/password` |
| Method | `PATCH` |
| Authorization | `Bearer <security_token>` |
| Content-Type | `application/json` |
| Body | `{ "old_password": "string", "new_password": "string" }` |

| **Server response** | |
| :--- | :--- |
| Content-Type | Aucun |
| Body | Aucun |
| Success Code | `204 No Content` |
| Error Codes | `400 Bad Request` (ancien mot de passe incorrect ou nouveau mot de passe trop court)<br>`401 Unauthorized` (token invalide ou expiré)<br>`403 Forbidden` (compte bloqué)<br>`422 Unprocessable Entity` (champs manquants) |

---

## Commandes de l'utilisateur

### POST /orders

Crée une réservation de produits et/ou menus pour une date de retrait (`pickup_date`) donnée. Vérifie la disponibilité, la période de validité des menus à `pickup_date`, l'absence de fermeture à `pickup_date`, et décrémente les stocks de manière atomique.

| **Client request** | |
| :--- | :--- |
| URL | `/orders` |
| Method | `POST` |
| Authorization | `Bearer <security_token>` |
| Content-Type | `application/json` |
| Body | `OrderCreate` |

| **Server response** | |
| :--- | :--- |
| Content-Type | `application/json` |
| Body | `Order` |
| Success Code | `201 Created` |
| Error Codes | `400 Bad Request` (commande vide, `pickup_date` dans le passé, `pickup_date` sur un jour de fermeture, stock agrégé insuffisant, produit/menu indisponible ou supprimé, menu hors période de validité à la date `pickup_date`)<br>`401 Unauthorized` (non authentifié)<br>`403 Forbidden` (compte bloqué)<br>`404 Not Found` (un `product_id` ou `menu_id` n'existe pas)<br>`422 Unprocessable Entity` (format JSON/date invalide ou `quantity < 1`) |

---

### GET /orders

Récupère l'historique des commandes de l'utilisateur actuellement connecté.

| **Client request** | |
| :--- | :--- |
| URL | `/orders` |
| Method | `GET` |
| Authorization | `Bearer <security_token>` |
| Content-Type | Aucun |
| Body | Aucun |

| **Server response** | |
| :--- | :--- |
| Content-Type | `application/json` |
| Body | `[Order]` |
| Success Code | `200 OK` |
| Error Codes | `401 Unauthorized` (token absent ou invalide)<br>`403 Forbidden` (compte bloqué) |

---

## Gestion des produits (Admin)

### POST /products

Ajoute un nouveau produit au catalogue.

| **Client request** | |
| :--- | :--- |
| URL | `/products` |
| Method | `POST` |
| Authorization | `Bearer <security_token>` (Admin) |
| Content-Type | `application/json` |
| Body | `{ "name": "string", "description": "string \| null", "price": "float", "stock": "int", "category_id": "int \| null", "is_available": "bool" }` |

| **Server response** | |
| :--- | :--- |
| Content-Type | `application/json` |
| Body | `Product` |
| Success Code | `201 Created` |
| Error Codes | `401 Unauthorized` (non authentifié)<br>`403 Forbidden` (droits administrateur requis)<br>`404 Not Found` (`category_id` inexistant)<br>`422 Unprocessable Entity` (données invalides, `price < 0` ou `stock < 0`) |

---

### PUT /products/{id}

Met à jour un produit existant (nom, description, prix, stock, disponibilité, catégorie, ou suppression logique via `is_deleted`). Tous les champs de l'objet doivent être transmis.

| **Client request** | |
| :--- | :--- |
| URL | `/products/{id}` |
| Method | `PUT` |
| Authorization | `Bearer <security_token>` (Admin) |
| Content-Type | `application/json` |
| Body | `{ "name": "string", "description": "string \| null", "price": "float", "stock": "int", "category_id": "int \| null", "is_available": "bool", "is_deleted": "bool" }` |

| **Server response** | |
| :--- | :--- |
| Content-Type | `application/json` |
| Body | `Product` |
| Success Code | `200 OK` |
| Error Codes | `400 Bad Request` (tentative de passer `is_deleted` à `true` alors que le produit est encore inclus dans un menu actif)<br>`401 Unauthorized` (non authentifié)<br>`403 Forbidden` (droits administrateur requis)<br>`404 Not Found` (produit `{id}` ou `category_id` introuvable)<br>`422 Unprocessable Entity` (données invalides, `price < 0` ou `stock < 0`) |

---

## Gestion des catégories (Admin)

### POST /categories

Crée une nouvelle catégorie de produits.

| **Client request** | |
| :--- | :--- |
| URL | `/categories` |
| Method | `POST` |
| Authorization | `Bearer <security_token>` (Admin) |
| Content-Type | `application/json` |
| Body | `{ "name": "string" }` |

| **Server response** | |
| :--- | :--- |
| Content-Type | `application/json` |
| Body | `Category` |
| Success Code | `201 Created` |
| Error Codes | `401 Unauthorized` (non authentifié)<br>`403 Forbidden` (droits administrateur requis)<br>`409 Conflict` (une catégorie porte déjà ce nom)<br>`422 Unprocessable Entity` (champ `name` manquant ou vide) |

---

### PUT /categories/{id}

Renomme une catégorie existante.

| **Client request** | |
| :--- | :--- |
| URL | `/categories/{id}` |
| Method | `PUT` |
| Authorization | `Bearer <security_token>` (Admin) |
| Content-Type | `application/json` |
| Body | `{ "name": "string" }` |

| **Server response** | |
| :--- | :--- |
| Content-Type | `application/json` |
| Body | `Category` |
| Success Code | `200 OK` |
| Error Codes | `401 Unauthorized` (non authentifié)<br>`403 Forbidden` (droits administrateur requis)<br>`404 Not Found` (catégorie `{id}` introuvable)<br>`409 Conflict` (nom de catégorie déjà utilisé)<br>`422 Unprocessable Entity` (données invalides) |

---

## Gestion des menus (Admin)

### POST /menus

Crée un nouveau menu composé d'un ou plusieurs produits avec leurs quantités et sa période de validité. Si `start_date` est omis dans la requête, la date du jour (UTC) est appliquée par défaut ; `start_date` ne peut pas valoir `null`.

| **Client request** | |
| :--- | :--- |
| URL | `/menus` |
| Method | `POST` |
| Authorization | `Bearer <security_token>` (Admin) |
| Content-Type | `application/json` |
| Body | `{ "name": "string", "description": "string \| null", "price": "float", "start_date": "Date (optionnel)", "end_date": "Date \| null", "is_available": "bool", "products": [MenuProductItem] }` |

| **Server response** | |
| :--- | :--- |
| Content-Type | `application/json` |
| Body | `Menu` |
| Success Code | `201 Created` |
| Error Codes | `400 Bad Request` (`end_date` non nulle antérieure à `start_date`, liste `products` vide, ou inclusion d'un produit supprimé `is_deleted: true`)<br>`401 Unauthorized` (non authentifié)<br>`403 Forbidden` (droits administrateur requis)<br>`404 Not Found` (un `product_id` de la liste n'existe pas)<br>`422 Unprocessable Entity` (données invalides, `start_date: null`, `price < 0` ou `quantity < 1`) |

---

### PUT /menus/{id}

Met à jour un menu existant, sa composition, ses dates de validité ou sa suppression logique (`is_deleted`).

| **Client request** | |
| :--- | :--- |
| URL | `/menus/{id}` |
| Method | `PUT` |
| Authorization | `Bearer <security_token>` (Admin) |
| Content-Type | `application/json` |
| Body | `{ "name": "string", "description": "string \| null", "price": "float", "start_date": "Date", "end_date": "Date \| null", "is_available": "bool", "is_deleted": "bool", "products": [MenuProductItem] }` |

| **Server response** | |
| :--- | :--- |
| Content-Type | `application/json` |
| Body | `Menu` |
| Success Code | `200 OK` |
| Error Codes | `400 Bad Request` (`end_date` non nulle antérieure à `start_date`, liste `products` vide, ou inclusion d'un produit supprimé `is_deleted: true`)<br>`401 Unauthorized` (non authentifié)<br>`403 Forbidden` (droits administrateur requis)<br>`404 Not Found` (menu `{id}` ou `product_id` introuvable)<br>`422 Unprocessable Entity` (données invalides, `start_date: null`, `price < 0` ou `quantity < 1`) |

---

## Gestion des jours de fermeture (Admin)

### POST /closures

Déclare un jour précis de fermeture de l'établissement.

| **Client request** | |
| :--- | :--- |
| URL | `/closures` |
| Method | `POST` |
| Authorization | `Bearer <security_token>` (Admin) |
| Content-Type | `application/json` |
| Body | `{ "closure_date": "Date", "reason": "string \| null" }` |

| **Server response** | |
| :--- | :--- |
| Content-Type | `application/json` |
| Body | `ClosureDay` |
| Success Code | `201 Created` |
| Error Codes | `400 Bad Request` (tentative d'enregistrer une date de fermeture dans le passé)<br>`401 Unauthorized` (non authentifié)<br>`403 Forbidden` (droits administrateur requis)<br>`409 Conflict` (cette date est déjà enregistrée comme jour de fermeture)<br>`422 Unprocessable Entity` (format de date invalide) |

---

### DELETE /closures/{id}

Supprime un jour de fermeture précédemment enregistré.

| **Client request** | |
| :--- | :--- |
| URL | `/closures/{id}` |
| Method | `DELETE` |
| Authorization | `Bearer <security_token>` (Admin) |
| Content-Type | Aucun |
| Body | Aucun |

| **Server response** | |
| :--- | :--- |
| Content-Type | Aucun |
| Body | Aucun |
| Success Code | `204 No Content` |
| Error Codes | `401 Unauthorized` (non authentifié)<br>`403 Forbidden` (droits administrateur requis)<br>`404 Not Found` (jour de fermeture `{id}` introuvable) |

---

## Gestion des utilisateurs et commandes (Admin)

### GET /users

Récupère la liste complète des comptes utilisateurs (permet à l'administrateur de consulter les inscrits et leur statut de blocage).

| **Client request** | |
| :--- | :--- |
| URL | `/users` |
| Method | `GET` |
| Authorization | `Bearer <security_token>` (Admin) |
| Content-Type | Aucun |
| Body | Aucun |

| **Server response** | |
| :--- | :--- |
| Content-Type | `application/json` |
| Body | `[User]` |
| Success Code | `200 OK` |
| Error Codes | `401 Unauthorized` (non authentifié)<br>`403 Forbidden` (droits administrateur requis) |

---

### PATCH /users/{id}/block

Bloque ou débloque un compte utilisateur (ex. en cas de commandes `no_show` répétées).

| **Client request** | |
| :--- | :--- |
| URL | `/users/{id}/block` |
| Method | `PATCH` |
| Authorization | `Bearer <security_token>` (Admin) |
| Content-Type | `application/json` |
| Body | `{ "is_blocked": "bool" }` |

| **Server response** | |
| :--- | :--- |
| Content-Type | `application/json` |
| Body | `User` |
| Success Code | `200 OK` |
| Error Codes | `400 Bad Request` (tentative d'un administrateur de bloquer son propre compte)<br>`401 Unauthorized` (non authentifié)<br>`403 Forbidden` (droits administrateur requis)<br>`404 Not Found` (utilisateur `{id}` introuvable)<br>`422 Unprocessable Entity` (champ `is_blocked` manquant ou non booléen) |

---

### GET /admin/orders

Récupère l'ensemble des commandes passées par tous les utilisateurs (filtrable optionnellement par date de retrait, statut ou identifiant utilisateur).

| **Client request** | |
| :--- | :--- |
| URL | `/admin/orders` *(query params optionnels : `?pickup_date=YYYY-MM-DD&status=pending&user_id=1`)* |
| Method | `GET` |
| Authorization | `Bearer <security_token>` (Admin) |
| Content-Type | Aucun |
| Body | Aucun |

| **Server response** | |
| :--- | :--- |
| Content-Type | `application/json` |
| Body | `[Order]` |
| Success Code | `200 OK` |
| Error Codes | `401 Unauthorized` (non authentifié)<br>`403 Forbidden` (droits administrateur requis)<br>`422 Unprocessable Entity` (paramètre de filtre invalide) |

---

### PATCH /orders/{id}/status

Met à jour l'état d'avancement d'une commande (`pending`, `completed`, `cancelled`, `no_show`). En cas de passage à `cancelled`, le back-end réincrémente les stocks ; en cas de passage à `no_show`, les stocks ne sont pas modifiés. Les statuts `completed`, `cancelled` et `no_show` sont des états terminaux.

| **Client request** | |
| :--- | :--- |
| URL | `/orders/{id}/status` |
| Method | `PATCH` |
| Authorization | `Bearer <security_token>` (Admin) |
| Content-Type | `application/json` |
| Body | `{ "status": "string ('pending' \| 'completed' \| 'cancelled' \| 'no_show')" }` |

| **Server response** | |
| :--- | :--- |
| Content-Type | `application/json` |
| Body | `Order` |
| Success Code | `200 OK` |
| Error Codes | `400 Bad Request` (transition de statut invalide : tentative de modifier une commande déjà `completed`, `cancelled` ou `no_show`)<br>`401 Unauthorized` (non authentifié)<br>`403 Forbidden` (droits administrateur requis)<br>`404 Not Found` (commande `{id}` introuvable)<br>`422 Unprocessable Entity` (valeur de `status` non reconnue) |