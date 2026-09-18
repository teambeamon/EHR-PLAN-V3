# EHR Plan V3

Système de gestion de planning pour EHR avec Next.js, Turso DB et Vercel.

## Structure du projet

- `app/` - Pages Next.js (App Router)
- `components/` - Composants React réutilisables
- `api/` - API Python pour Vercel
- `public/` - Fichiers statiques
- `vercel.json` - Configuration de déploiement Vercel

## Prérequis

- Node.js 18+ (pour Next.js)
- Python 3.9+ (pour l'API)
- Compte Vercel
- Base de données Turso

## Configuration initiale

### 1. Cloner le dépôt

```bash
cd /Users/neobeamon/MistralProjects
git clone https://github.com/teambeamon/ehr-plan-v3.git
ehr-plan-v3
```

### 2. Configurer Turso DB

Créer une base de données sur [Turso](https://turso.tech/) et exécuter:

```sql
-- Créer les tables nécessaires
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
```

### 3. Configurer Vercel

1. Aller sur [Vercel Dashboard](https://vercel.com/dashboard)
2. Cliquer sur "Add New" → "Project"
3. Importer depuis GitHub (sélectionner `ehr-plan-v3`)
4. Dans les paramètres du projet, ajouter les variables d'environnement:
   - `NEXT_PUBLIC_TURSO_URL` = `libsql://votre-db.turso.io`
   - `NEXT_PUBLIC_TURSO_AUTH_TOKEN` = `votre-token-turso`
   - `TURSO_URL` = `libsql://votre-db.turso.io`
   - `TURSO_AUTH_TOKEN` = `votre-token-turso`
   - `NEXT_PUBLIC_ADMIN_PASSWORD` = `votre-mot-de-passe-admin`

### 4. Déployer

Vercel va automatiquement déployer le projet lors du push sur la branche `main`.

## Développement local

### Frontend (Next.js)

```bash
cd ehr-plan-v3
npm install
npm run dev
```

Ouvrir [http://localhost:3000](http://localhost:3000)

### API (Python)

```bash
cd ehr-plan-v3/api
pip install -r requirements.txt
# Tester avec: vercel dev (nécessite Vercel CLI)
```

## Routes disponibles

- `/` - Page d'accueil
- `/salles` - Liste des salles
- `/matches` - Liste des matchs
- `/classements` - Classements des équipes
- `/admin` - Panneau d'administration (nécessite mot de passe)
- `/api/salles` - API pour les salles
- `/api/matchs` - API pour les matchs
- `/api/classements` - API pour les classements

## Résolution des problèmes

### Erreur "Unexpected token 'div'"

Cette erreur se produit lorsque le fichier JSX a une syntaxe incorrecte ou lorsqu'il manque le layout racine. Ce projet inclut:
- `app/layout.tsx` - Layout racine requis par Next.js 14
- Toutes les pages utilisent une syntaxe JSX valide

### Problèmes de déploiement Vercel

1. **Erreur de validation vercel.json**: S'assurer que le fichier ne contient pas de propriétés invalides comme `cacheBust` ou `nodeVersion`.

2. **Build échoue**: Vérifier que tous les fichiers sont valides et que node_modules n'est pas commité.

3. **404 Not Found**: Vérifier les routes dans vercel.json et s'assurer que le projet est bien déployé.

## Gestion des variables d'environnement

### Pour le développement local

Créer un fichier `.env.local`:

```bash
cp .env.example .env.local
# Éditer avec vos valeurs
```

### Pour Vercel

Ajouter les variables dans le tableau de bord Vercel:
- Project Settings → Environment Variables

## Scripts disponibles

- `npm run dev` - Démarrer le serveur de développement
- `npm run build` - Construire pour la production
- `npm run start` - Démarrer le serveur de production
- `npm run lint` - Exécuter le linter

## Technologies utilisées

- **Frontend**: Next.js 14, React 18, TypeScript, Tailwind CSS
- **Backend**: Python, libsql-client (pour Turso)
- **Database**: Turso (SQLite compatible)
- **Hébergement**: Vercel
