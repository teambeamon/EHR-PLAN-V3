# 🎯 EHR-PLAN-V3 - Guide de Déploiement Corrigé

## 📋 Résumé des Corrections Appliquées

### ✅ Problèmes identifiés et résolus :

| N° | Problème | Solution | Statut |
|---|----------|----------|--------|
| 1 | `requirements.txt` à la racine au lieu de `api/` | Déplacé vers `api/requirements.txt` | ✅ |
| 2 | Pas de `__init__.py` dans `api/` | Créé `api/__init__.py` | ✅ |
| 3 | Variables d'environnement incohérentes | Standardisé sur `TURSO_URL` + `TURSO_AUTH_TOKEN` | ✅ |
| 4 | Pas de serveur dev pour le backend | Créé `api/dev_server.py` | ✅ |
| 5 | Pas de rewrites Next.js pour le dev | Ajouté dans `next.config.js` | ✅ |
| 6 | Pas de script pour lancer le backend | Ajouté `dev:api` et `dev:full` | ✅ |
| 7 | `vercel.json` routes non optimales | Simplifié et optimisé | ✅ |
| 8 | Pas de `.vercelignore` | Créé avec exclusions appropriées | ✅ |

---

## 📁 Structure du Projet (après corrections)

```
ehr-plan-v3/
├── api/
│   ├── __init__.py              # ✅ NOUVEAU: Package init
│   ├── index.py                # Backend: Vercel Serverless Function
│   ├── dev_server.py           # ✅ NOUVEAU: Serveur dev local
│   └── requirements.txt        # ✅ CORRIGÉ: Déplacé ici
├── app/
│   ├── page.tsx
│   ├── salles/page.tsx
│   ├── matches/page.tsx
│   ├── classements/page.tsx
│   └── admin/page.tsx
├── components/
│   └── Navbar.tsx
├── public/
├── .env.example
├── .gitignore
├── .vercelignore               # ✅ NOUVEAU
├── next.config.js             # ✅ MODIFIÉ: Rewrites ajoutées
├── vercel.json                # ✅ MODIFIÉ: Routes simplifiées
├── package.json               # ✅ MODIFIÉ: Scripts ajoutés
└── tailwind.config.ts
```

---

## 🚀 Étapes de Déploiement sur Vercel

### 1️⃣ Préparation locale

```bash
cd /Users/neobeamon/MistralProjects/ehr-plan-v3

# Installe les dépendances Node.js
npm install

# Installe les dépendances Python (pour le dev local)
pip install requests
```

### 2️⃣ Test en local (optionnel mais recommandé)

**Terminal 1** - Lance le backend local :
```bash
npm run dev:api
# ou
python api/dev_server.py
```
→ Serveur disponible sur `http://localhost:8000`

**Terminal 2** - Lance le frontend :
```bash
npm run dev
```
→ Frontend disponible sur `http://localhost:3000`

**Vérifie** :
- ✅ `http://localhost:3000` charge correctement
- ✅ `http://localhost:3000/api/salles` retourne des données (proxyfié vers localhost:8000)
- ✅ `http://localhost:3000/salles` affiche la liste des salles

**OU** lance tout en une seule commande :
```bash
npm run dev:full
```
*(Nécessite `npm install concurrently` au préalable)*

### 3️⃣ Déploiement sur Vercel

1. **Commit et push** :
```bash
git add .
git commit -m "Fix Vercel deployment: move requirements.txt to api/, add __init__.py, add dev_server"
git push origin main
```

2. **Sur vercel.com** :
   - Va sur https://vercel.com/dashboard
   - Clique sur "Add New" → "Project"
   - Sélectionne le dépôt `teambeamon/EHR-PLAN-V3`
   - **Root Directory** : `.` (la racine)
   - **Framework Preset** : Next.js
   - Clique sur **Deploy**

3. **Configure les variables d'environnement** *(OBLIGATOIRE)* :

   | Variable | Valeur | Type | Où |
   |----------|--------|------|-----|
   | `TURSO_URL` | `libsql://votre-db.turso.io` | Private | Backend |
   | `TURSO_AUTH_TOKEN` | `votre-token-turso` | Private | Backend |
   | `NEXT_PUBLIC_TURSO_URL` | `libsql://votre-db.turso.io` | Public | Frontend |
   | `NEXT_PUBLIC_TURSO_AUTH_TOKEN` | `votre-token-turso` | Public | Frontend |
   | `NEXT_PUBLIC_ADMIN_PASSWORD` | `admin123` (ou autre) | Public | Frontend |

   > ⚠️ **Important** :
   > - `TURSO_URL` et `NEXT_PUBLIC_TURSO_URL` doivent avoir la **même valeur**
   > - `TURSO_AUTH_TOKEN` et `NEXT_PUBLIC_TURSO_AUTH_TOKEN` doivent avoir la **même valeur**
   > - Pour la sécurité, utilisez un token Turso avec des permissions restreintes

4. **Redéploie** :
   - Après avoir ajouté les variables, cliquez sur "Redeploy"

5. **Vérifie** :
   - ✅ L'application est sur `https://ehr-plan-v3.vercel.app`
   - ✅ La page d'accueil charge
   - ✅ `/salles` affiche les salles
   - ✅ `/matches` affiche les matchs
   - ✅ `/classements` affiche les classements
   - ✅ `/admin` permet de se connecter (mot de passe: `NEXT_PUBLIC_ADMIN_PASSWORD`)

---

## 🔧 Configuration de la Base de Données Turso

### 1. Créer la base de données

1. Allez sur https://turso.tech/ et connectez-vous
2. Cliquez sur "New Database"
3. Donnez un nom (ex: `ehr-plan-v3`)
4. Sélectionnez une région proche de vous

### 2. Exécuter le schéma SQL

Dans le **Shell Turso** de votre base de données, exécutez :

```sql
-- Créer les tables
CREATE TABLE salles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT NOT NULL,
    capacite INTEGER DEFAULT 0,
    type TEXT DEFAULT 'Standard'
);

CREATE TABLE equipes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT NOT NULL,
    logo TEXT
);

CREATE TABLE matchs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    salle_id INTEGER NOT NULL,
    équipe1_id INTEGER,
    équipe2_id INTEGER,
    date TEXT NOT NULL,
    statut TEXT DEFAULT 'programmé',
    gagnant_id INTEGER,
    FOREIGN KEY (salle_id) REFERENCES salles(id),
    FOREIGN KEY (équipe1_id) REFERENCES équipes(id),
    FOREIGN KEY (équipe2_id) REFERENCES équipes(id),
    FOREIGN KEY (gagnant_id) REFERENCES équipes(id)
);

-- Ajouter des données de test
INSERT INTO salles (nom, capacite, type) VALUES ('Salle A', 20, 'Compétition');
INSERT INTO salles (nom, capacite, type) VALUES ('Salle B', 15, 'Entraînement');
INSERT INTO salles (nom, capacite, type) VALUES ('Salle C', 25, 'Compétition');

INSERT INTO équipes (nom) VALUES ('Équipe Rouge');
INSERT INTO équipes (nom) VALUES ('Équipe Bleue');
INSERT INTO équipes (nom) VALUES ('Équipe Verte');

INSERT INTO matchs (salle_id, équipe1_id, équipe2_id, date, statut) 
VALUES (1, 1, 2, datetime('now', '+1 day'), 'programmé');

INSERT INTO matchs (salle_id, équipe1_id, équipe2_id, date, statut) 
VALUES (2, 2, 3, datetime('now', '+2 days'), 'programmé');
```

### 3. Récupérer l'URL et le token

- **URL** : `libsql://votre-db-name.turso.io`
- **Token** : Dans **Settings** → **Auth Tokens** → **Create new token**

---

## 🐛 Résolution des Problèmes Courants

### ❌ Problème : "ModuleNotFoundError: No module named 'requests'"

**Cause** : `requirements.txt` était à la racine, pas dans `api/`

**Solution** : ✅ **Déjà corrigé** - `requirements.txt` est maintenant dans `api/`

---

### ❌ Problème : "404 Not Found" sur `/api/salles` en production

**Causes possibles** :
1. Backend Python non déployé
2. Variables d'environnement manquantes
3. Route mal configurée

**Solutions** :
1. Vérifiez dans Vercel → Deployments → cliquez sur le dernier déploiement → onglet "Functions"
2. Vérifiez que `api/index.py` s'est bien déployé
3. Vérifiez les variables d'environnement (voir section ci-dessus)
4. Vérifiez que `vercel.json` pointe bien vers `api/index.py`

---

### ❌ Problème : "500 Internal Server Error" sur les routes API

**Causes possibles** :
1. Variables d'environnement `TURSO_URL` ou `TURSO_AUTH_TOKEN` manquantes
2. URL Turso incorrecte
3. Token Turso invalide

**Solution** :
- Vérifiez les logs dans Vercel → Deployments → cliquez sur le déploiement → onglet "Logs"
- Vérifiez que `TURSO_URL` et `TURSO_AUTH_TOKEN` sont bien configurées
- Testez votre token Turso avec :
  ```bash
  curl -H "Authorization: Bearer VOTRE_TOKEN" \
    https://votre-db.turso.io/v2/sql \
    -X POST \
    -d '{"query": "SELECT 1"}'
  ```

---

### ❌ Problème : Les images/logos ne s'affichent pas

**Cause** : Le frontend utilise des URLs absolues pour les logos

**Solution** : Utilisez des URLs relative ou hébergez les images sur un service comme Imgur

---

### ❌ Problème : En développement local, `/api/salles` retourne 404

**Cause** : Le backend local n'est pas lancé

**Solution** :
```bash
# Terminal 1
npm run dev:api

# Terminal 2
npm run dev
```

Ou en une seule commande :
```bash
npm run dev:full
```

---

## 📊 Vérification Post-Déploiement

### ✅ Frontend
- [ ] La page charge sur `https://ehr-plan-v3.vercel.app`
- [ ] Le design est correct (Tailwind CSS)
- [ ] Le dark mode fonctionne
- [ ] La barre de navigation est visible

### ✅ Backend
- [ ] `GET /api/salles` retourne `{salles: [...]}`
- [ ] `GET /api/matchs` retourne `{matchs: [...]}`
- [ ] `GET /api/classements` retourne `{classements: [...]}`
- [ ] `POST /api/salles` crée une salle
- [ ] `POST /api/matchs` crée un match

### ✅ Base de données
- [ ] Les données sont persistées entre les requêtes
- [ ] Pas d'erreurs de connexion à Turso

---

## 🎓 Bonnes Pratiques

### 1. Variables d'environnement

**En production (Vercel)** :
- Utilisez toujours des **variables privées** pour les tokens sensibles
- Pour le frontend, utilisez le préfixe `NEXT_PUBLIC_`
- Pour le backend, utilisez des noms sans préfixe

**En développement local** :
- Créez un fichier `.env.local` à la racine
- Copiez les valeurs depuis `.env.example` et adaptez

### 2. Développement

**Toujours tester en local avant de déployer** :
```bash
npm run dev:full
```

**Vérifier les logs** :
- Vercel → Deployments → cliquez sur le déploiement → onglet "Logs"
- Filtrez par "Python" ou "Serverless Function"

### 3. Sécurité

- Ne jamais committer `.env` ou `.env.local` dans Git
- Utilisez des tokens Turso avec des permissions restreintes
- Changez le mot de passe admin par défaut (`admin123`)

---

## 📚 Ressources

- [Documentation Vercel](https://vercel.com/docs)
- [Vercel Serverless Functions](https://vercel.com/docs/concepts/functions)
- [Turso Database](https://turso.tech/)
- [Python HTTP Server](https://docs.python.org/3/library/http.server.html)

---

## 📞 Support

Si vous avez des problèmes :

1. **Vérifiez les logs de déploiement** dans Vercel
2. **Vérifiez les variables d'environnement** dans Vercel Settings
3. **Testez en local** avec `npm run dev:full`
4. **Vérifiez votre base de données Turso** avec le shell en ligne

---

**Statut** : ✅ Prêt pour le déploiement  
**Date** : 2026-09-19  
**Version** : 1.1 (Configuration Vercel corrigée)