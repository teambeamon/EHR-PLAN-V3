# Solution Complète pour EHR-PLAN-V3

## Problèmes Identifiés et Résolus

### 🔴 Problème 1: Erreur 500 sur la page d'accueil
**Cause:** La page d'accueil (`/`) essaie de récupérer les salles via `/api/salles`, mais la table `salles` n'existait pas dans la base de données.

**Solution:** ✅ Modifié `api/index.py` pour créer TOUTES les tables nécessaires au démarrage:
- `users` - Utilisateurs
- `sessions` - Sessions de connexion
- `salles` - Salles
- `équipes` - Équipes
- `matchs` - Matchs

### 🔴 Problème 2: Impossible de se connecter
**Cause:** Même problème - sans les tables, le système d'authentification ne pouvait pas fonctionner.

**Solution:** ✅ Le default admin user `admin/admin123` est maintenant automatiquement créé si la table users est vide.

### 🔴 Problème 3: Nom de la base de données inconnu
**Cause:** Le code utilisait `TURSO_URL` mais le nom exact n'était pas documenté.

**Solution:** ✅ Documenté clairement: **Utilisez `ehr-plan-db` comme nom de base de données**

### 🔴 Problème 4: Conflit de fichiers requirements.txt
**Cause:** Il y avait un `requirements.txt` à la racine ET dans `api/`, ce qui pouvait confondre Vercel.

**Solution:** ✅ Supprimé le `requirements.txt` à la racine. Seul `api/requirements.txt` est utilisé.

---

## 📋 Configuration Requise

### 1. Base de données Turso

1. Allez sur https://turso.tech/ et connectez-vous
2. **Créer une nouvelle base de données** avec le nom exact: **`ehr-plan-db`**
   - Cliquez sur "New Database"
   - Nom: `ehr-plan-db`
   - Région: Choisissez la plus proche de vous
3. **Récupérer le token d'authentification:**
   - Allez dans votre base de données
   - Cliquez sur "Settings" (⚙️)
   - Allez dans "Auth Tokens"
   - Cliquez sur "Create new token"
   - Copiez le token généré

**URL de la base:** `libsql://ehr-plan-db.turso.io`

---

### 2. Variables d'Environnement sur Vercel

Allez dans: https://vercel.com/dashboard → Votre projet → Settings → Environment Variables

Ajoutez ces 4 variables (TOUTES REQUISES):

| Nom | Valeur | Type |
|-----|--------|------|
| `TURSO_URL` | `libsql://ehr-plan-db.turso.io` | Private |
| `TURSO_AUTH_TOKEN` | `votre-token-turso-copié-étape-3` | Private |
| `NEXT_PUBLIC_TURSO_URL` | `libsql://ehr-plan-db.turso.io` | Public |
| `NEXT_PUBLIC_TURSO_AUTH_TOKEN` | `votre-token-turso-copié-étape-3` | Public |

> ⚠️ **IMPORTANT:** Remplacez `votre-token-turso-copié-étape-3` par le token réel que vous avez copié.

---

### 3. Redéployer sur Vercel

1. Dans Vercel, allez dans l'onglet **Deployments**
2. Cliquez sur **Redeploy** (en haut à droite)
3. Attendez que le déploiement se termine (2-5 minutes)
4. Une fois terminé, cliquez sur le lien du déploiement

---

## 🧪 Test de Fonctionnement

### Accès:
- **Page d'accueil:** `https://votre-projet.vercel.app/`
- **Page de connexion:** `https://votre-projet.vercel.app/login`
- **Page admin:** `https://votre-projet.vercel.app/admin`

### Identifiants par défaut:
- **Utilisateur:** `admin`
- **Mot de passe:** `admin123`

### Fonctions à tester:
1. ✅ Page d'accueil charge sans erreur 500
2. ✅ Connexion avec admin/admin123
3. ✅ Accès à la page admin après connexion
4. ✅ Réinitialisation du mot de passe (bouton "Mot de passe oublié ?")
5. ✅ Déconnexion

---

## 🔧 Si ça ne marche toujours pas

### Vérification 1: Les tables sont-elles créées ?
1. Allez sur https://turso.tech/
2. Sélectionnez votre base `ehr-plan-db`
3. Cliquez sur "Shell" ou "Query"
4. Exécutez: `SELECT name FROM sqlite_master WHERE type='table';`
5. **Résultat attendu:** Vous devriez voir: `users, sessions, salles, équipes, matchs`

### Vérification 2: Le default user existe ?
Exécutez dans le shell Turso:
```sql
SELECT * FROM users;
```
**Résultat attendu:** Une ligne avec `username=admin, role=admin`

### Vérification 3: Les logs Vercel
1. Dans Vercel, allez dans le déploiement
2. Cliquez sur le déploiement le plus récent
3. Allez dans l'onglet **Logs**
4. Cherchez des erreurs comme:
   - `Missing TURSO_URL` → Variables d'environnement non configurées
   - `DB Error` → Problème de connexion à Turso
   - `500` → Erreur serveur

### Vérification 4: Tester l'API directement
Ouvrez votre navigateur et testez:
- `https://votre-projet.vercel.app/api/salles` → Devrait retourner `{"salles": [...]}`
- `https://votre-projet.vercel.app/api/me` → Devrait retourner une erreur (pas de token)

---

## 🚨 Problèmes Courants et Solutions

### Problème: "Missing TURSO_URL or TURSO_AUTH_TOKEN"
**Solution:** Vérifiez que les 4 variables d'environnement sont bien configurées dans Vercel (voir section 2).

### Problème: "Invalid credentials" avec admin/admin123
**Solution:** 
1. Vérifiez que le default user a été créé (Vérification 2)
2. Si la table users est vide, c'est que l'initialisation a échoué
3. **Solution:** Supprimez et recréez la base de données, puis redéployez

### Problème: Erreur 500 sur la page d'accueil
**Solution:** 
1. Vérifiez que la table `salles` existe (Vérification 1)
2. Si elle n'existe pas, attendez que le déploiement soit terminé et rafraîchissez
3. L'initialisation se fait automatiquement au premier appel API

### Problème: La page admin redirige vers login en boucle
**Solution:** 
1. Connectez-vous d'abord via `/login`
2. Vérifiez que vous avez bien le token dans localStorage:
   - Ouvrez DevTools (F12)
   - Allez dans Application > Local Storage
   - Vérifiez `ehr_session_token` existe

---

## 💡 Astuce: Reset Complet

Si vous voulez tout effacer et recommencer à zéro:

### 1. Supprimer sur Vercel
- Allez dans https://vercel.com/dashboard
- Sélectionnez le projet EHR-PLAN-V3
- Settings → Delete Project

### 2. Supprimer sur Turso
- Allez dans https://turso.tech/
- Sélectionnez `ehr-plan-db`
- Cliquez sur les trois points → Delete

### 3. Supprimer sur GitHub (optionnel)
- Allez dans https://github.com/teambeamon/EHR-PLAN-V3
- Settings → Delete repository

### 4. Recommencer
1. Créez un nouveau dépôt GitHub (ex: `ehr-plan-prod`)
2. Poussez ce code:
```bash
cd /Users/neobeamon/MistralProjects/ehr-plan-v3
git remote set-url origin https://github.com/teambeamon/ehr-plan-prod.git
git push -u origin main --force
```
3. Suivez ce guide depuis le début

---

## 📊 Structure des Tables

### users
```sql
id INTEGER PRIMARY KEY AUTOINCREMENT
username TEXT UNIQUE NOT NULL
hashed_password TEXT NOT NULL
email TEXT
role TEXT DEFAULT 'user'
created_at TEXT DEFAULT CURRENT_TIMESTAMP
```

### sessions
```sql
token TEXT PRIMARY KEY
user_id INTEGER NOT NULL
-expires_at TEXT NOT NULL
created_at TEXT DEFAULT CURRENT_TIMESTAMP
FOREIGN KEY (user_id) REFERENCES users(id)
```

### salles
```sql
id INTEGER PRIMARY KEY AUTOINCREMENT
nom TEXT NOT NULL
capacite INTEGER DEFAULT 0
type TEXT DEFAULT 'Standard'
```

### équipes
```sql
id INTEGER PRIMARY KEY AUTOINCREMENT
nom TEXT NOT NULL
logo TEXT
```

### matchs
```sql
id INTEGER PRIMARY KEY AUTOINCREMENT
salle_id INTEGER NOT NULL
équipe1_id INTEGER
équipe2_id INTEGER
date TEXT NOT NULL
statut TEXT DEFAULT 'programmé'
gagnant_id INTEGER
FOREIGN KEY (salle_id) REFERENCES salles(id)
FOREIGN KEY (équipe1_id) REFERENCES équipes(id)
FOREIGN KEY (équipe2_id) REFERENCES équipes(id)
FOREIGN KEY (gagnant_id) REFERENCES équipes(id)
```

---

## ✅ Résumé des Fichiers Modifiés

1. **`api/index.py`** - Ajout de la création de toutes les tables + données d'exemple
2. **`.env.example`** - Documentation claire du nom de la base de données
3. **`requirements.txt` (supprimé)** - Évitait la confusion avec Vercel

---

## 🎯 Prochaines Étapes

Une fois que tout fonctionne:
1. Changez le mot de passe admin dans l'interface de réinitialisation
2. Ajoutez d'autres utilisateurs via l'interface admin
3. Configurez un domaine personnalisé sur Vercel
4. Activez HTTPS automatique

---

**Besoin d'aide ?** Vérifiez d'abord les sections de vérification ci-dessus, puis consultez les logs Vercel.
