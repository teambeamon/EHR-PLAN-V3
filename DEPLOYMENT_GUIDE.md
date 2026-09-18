# Guide de déploiement complet pour EHR-PLAN-V3

## 📋 Résumé

J'ai recréé **complètement** votre projet EHR Plan avec une structure propre et fonctionnelle.

**Problèmes résolus :**
- ✅ Erreurs de syntaxe JSX (Unexpected token 'div')
- ✅ Fichiers manquants (layout.tsx, Navbar.tsx)
- ✅ Configuration vercel.json incorrecte
- ✅ Problèmes de cache Vercel
- ✅ Large files dans Git (node_modules)
- ✅ Problèmes de nom de repo (majuscules)

---

## 🎯 Étapes à suivre pour déployer

### Étape 1: Vérifier le dépôt GitHub

Votre code est maintenant sur : https://github.com/teambeamon/EHR-PLAN-V3

Commit : `08e2383a7229880eeba519efe5ec71076e6938d9`

---

### Étape 2: Configurer la base de données Turso

1. Allez sur https://turso.tech/ et connectez-vous
2. **Créer une nouvelle base de données** (ex: `ehr-plan-db`)
3. **Exécuter ces commandes SQL** dans le shell Turso :

```sql
-- Créer les tables
CREATE TABLE salles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT NOT NULL,
    capacite INTEGER DEFAULT 0,
    type TEXT DEFAULT 'Standard'
);

CREATE TABLE équipes (
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

-- Ajouter quelques données de test
INSERT INTO salles (nom, capacite, type) VALUES ('Salle A', 20, 'Compétition');
INSERT INTO salles (nom, capacite, type) VALUES ('Salle B', 15, 'Entraînement');
INSERT INTO équipes (nom) VALUES ('Équipe Rouge');
INSERT INTO équipes (nom) VALUES ('Équipe Bleue');
INSERT INTO matchs (salle_id, équipe1_id, équipe2_id, date, statut) 
VALUES (1, 1, 2, datetime('now', '+1 day'), 'programmé');
```

4. **Récupérer l'URL et le token** de votre base de données
   - URL : `libsql://votre-db-name.turso.io`
   - Token : Dans Settings → Auth Tokens → Create new token

---

### Étape 3: Créer le projet sur Vercel

1. Allez sur https://vercel.com/dashboard
2. Cliquez sur **"Add New" → "Project"**
3. **Importer depuis GitHub** : Sélectionnez `teambeamon/EHR-PLAN-V3`
4. **Configurer le projet** :
   - Framework Preset : Next.js
   - Root Directory : (laisser vide)
   - Cliquez sur **Deploy**

---

### Étape 4: Configurer les variables d'environnement dans Vercel

Après le déploiement initial (qui va échouer), allez dans :

**Project Settings → Environment Variables**

Ajoutez ces variables :

| Nom | Valeur | Type |
|-----|--------|------|
| `NEXT_PUBLIC_TURSO_URL` | `libsql://votre-db-name.turso.io` | Public |
| `NEXT_PUBLIC_TURSO_AUTH_TOKEN` | `votre-token-turso` | Public |
| `TURSO_URL` | `libsql://votre-db-name.turso.io` | Private |
| `TURSO_AUTH_TOKEN` | `votre-token-turso` | Private |
| `NEXT_PUBLIC_ADMIN_PASSWORD` | `admin123` (ou changez-le) | Public |

> ⚠️ **Important** : Les variables `NEXT_PUBLIC_*` sont accessibles côté client. Pour plus de sécurité, utilisez des tokens Turso avec des permissions restreintes.

---

### Étape 5: Redéployer

1. Dans Vercel, allez dans **Deployments**
2. Cliquez sur **"Redeploy"** en haut à droite
3. Attendez que le build se termine (environ 2-5 minutes)

---

### Étape 6: Tester votre site

Une fois le déploiement terminé :
1. Cliquez sur le lien du déploiement (ex: `https://ehr-plan-v3.vercel.app`)
2. Testé ces pages :
   - `/` - Accueil
   - `/salles` - Liste des salles
   - `/matches` - Liste des matchs
   - `/classements` - Classements
   - `/admin` - Connexion admin (mot de passe : `admin123` ou celui que vous avez configuré)

---

## 🛠 Configuration pour le développement local (optionnel)

Si vous voulez travailler en local :

### 1. Cloner le dépôt
```bash
cd /Users/neobeamon/MistralProjects
git clone https://github.com/teambeamon/EHR-PLAN-V3.git
ehr-plan-v3
```

### 2. Installer les dépendances
```bash
cd ehr-plan-v3
npm install
```

### 3. Créer le fichier .env.local
```bash
cp .env.example .env.local
# Éditer avec vos valeurs Turso
```

### 4. Démarrer le serveur
```bash
npm run dev
```

Ouvrir http://localhost:3000

---

## 📁 Structure du projet

```
ehr-plan-v3/
├── app/
│   ├── admin/
│   │   └── page.tsx          # Page admin (avec authentification)
│   ├── classements/
│   │   └── page.tsx          # Page des classements
│   ├── matches/
│   │   └── page.tsx          # Page des matchs
│   ├── salles/
│   │   └── page.tsx          # Page des salles
│   ├── globals.css            # Styles globaux (Tailwind)
│   ├── layout.tsx             # Layout racine (REQUIS par Next.js 14)
│   └── page.tsx               # Page d'accueil
├── api/
│   ├── handler.py             # API Python pour Vercel
│   └── requirements.txt        # Dépendances Python
├── components/
│   └── Navbar.tsx             # Composant de navigation
├── public/
│   └── favicon.ico
├── .env.example               # Exemple de variables d'environnement
├── .gitignore                 # Fichiers à ignorer
├── next.config.js             # Configuration Next.js
├── package.json               # Dépendances Node.js
├── postcss.config.js          # Configuration PostCSS
├── tailwind.config.ts         # Configuration Tailwind
├── tsconfig.json              # Configuration TypeScript
├── vercel.json                # Configuration Vercel
└── README.md
```

---

## ⚠️ Problèmes courants et solutions

### Problème 1 : "Unexpected token 'div'. Expected jsx identifier"

**Cause :** Fichier JSX sans syntaxe valide ou layout manquant.

**Solution :** ✅ **Déjà résolu** dans ce projet :
- `app/layout.tsx` existe
- Tous les fichiers `.tsx` ont une syntaxe valide
- Chaque page retourne un composant React valide

---

### Problème 2 : "page.tsx doesn't have a root layout"

**Cause :** Le fichier `app/layout.tsx` est manquant.

**Solution :** ✅ **Déjà résolu** : `app/layout.tsx` est présent.

---

### Problème 3 : Erreur de validation vercel.json

**Cause :** Propriétés invalides dans vercel.json (cacheBust, nodeVersion, etc.)

**Solution :** ✅ **Déjà résolu** : Le fichier vercel.json est propre et valide.

---

### Problème 4 : "Build failed because of webpack errors"

**Cause :** Erreur de compilation Next.js.

**Solution :**
1. Vérifiez que tous les fichiers `.tsx` sont valides
2. Vérifiez que `app/layout.tsx` existe
3. Vérifiez que node_modules n'est pas dans Git (c'est le cas ici avec .gitignore)

---

### Problème 5 : "404 Not Found" après déploiement

**Cause :** Routes mal configurées ou déploiement incomplet.

**Solution :**
1. Vérifiez dans Vercel que le build s'est terminé avec succès
2. Vérifiez que vercel.json a les bonnes routes
3. Attendez quelques minutes et rafraîchissez

---

## 🔄 Si vous voulez tout effacer et recommencer

1. **Supprimer le projet Vercel** :
   - Allez dans Vercel Dashboard
   - Sélectionnez le projet EHR-PLAN-V3
   - Cliquez sur **Settings → Delete Project**

2. **Supprimer le dépôt GitHub** :
   - Allez sur https://github.com/teambeamon/EHR-PLAN-V3
   - Settings → Delete repository

3. **Recréer** :
   - Créez un nouveau repo sur GitHub (ex: `ehr-plan-prod`)
   - Poussez ce code :
   ```bash
   cd /Users/neobeamon/MistralProjects/ehr-plan-v3
git remote set-url origin https://github.com/teambeamon/ehr-plan-prod.git
git push -u origin main --force
   ```

---

## 🎉 Vous avez terminé !

Une fois toutes les étapes ci-dessus exécutées, votre site devrait être accessible et fonctionnel.

**URL finale :** `https://ehr-plan-v3.vercel.app` (ou le domaine personnalisé que vous avez configuré)

---

## 📞 Support

Si vous avez des problèmes :

1. **Vérifiez les logs de déploiement** dans Vercel
2. **Consultez le README.md** dans ce projet
3. **Vérifiez les variables d'environnement** dans Vercel
4. **Contactez-moi** avec le message d'erreur exact

---

*Ce guide et le code ont été générés par Mistral Vibe* 🚀
