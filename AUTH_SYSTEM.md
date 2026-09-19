# 🔐 Système d'Authentification - EHR Plan V3

## 📋 Résumé

Un système complet d'authentification a été ajouté avec :
- **Page de login** (`/login`)
- **Gestion des sessions** avec tokens stockés en base de données
- **Reset de mot de passe** (mode démo)
- **Protection des routes** admin
- **Navigations sécurisées**

---

## 🎯 Nouveautés Implémentées

### 1. **Backend (api/index.py)**

#### Tables de base de données créées automatiquement :
```sql
-- Table des utilisateurs
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    hashed_password TEXT NOT NULL,
    email TEXT,
    role TEXT DEFAULT 'user',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Table des sessions
CREATE TABLE IF NOT EXISTS sessions (
    token TEXT PRIMARY KEY,
    user_id INTEGER NOT NULL,
    expires_at TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

#### **Utilisateur par défaut** :
- **Username** : `admin`
- **Password** : `admin123`
- **Role** : `admin`

#### **Endpoints API** :

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/api/login` | POST | Authentifier un utilisateur |
| `/api/logout` | POST | Détruire la session |
| `/api/me` | GET | Récupérer les infos de l'utilisateur actuel |
| `/api/reset-password` | POST | Réinitialiser le mot de passe (demo) |

---

### 2. **Frontend**

#### **Pages** :
- `/login` - Page de connexion avec formulaire
- `/admin` - Page admin protégée (nécessite authentication + rôle admin)

#### **Composants** :
- `Navbar.tsx` - Affiche "Connexion" ou "Déconnexion" selon l'état

#### **Utilitaires** (`lib/session.ts`) :
```typescript
// Fonctions principales
saveSession(session)        // Sauvegarde la session
clearSession()             // Supprime la session
getSessionToken()          // Récupère le token
getCurrentUser()           // Récupère l'utilisateur courant
isAuthenticated()          // Vérifie si l'utilisateur est connecté
isAdmin()                 // Vérifie si l'utilisateur est admin
validateSession()         // Valide la session avec le backend
login(username, password)  // Connexion
logout()                   // Déconnexion
resetPassword(email)      // Réinitialisation du mot de passe

// Hooks
useSession(role?)          // Vérifie la session et redirige si nécessaire
useAdminAuth()             // Vérifie que l'utilisateur est admin
```

---

## 🚀 Comment Utiliser le Système

### **1. Connexion**

**Via la page de login** :
1. Va sur `/login`
2. Entre ton username et password
3. Clique sur "Se connecter"

**Identifiants par défaut** :
- Username: `admin`
- Password: `admin123`

**Via l'API** :
```bash
curl -X POST http://localhost:3000/api/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

**Réponse** :
```json
{
  "token": "...",
  "username": "admin",
  "role": "admin",
  "expires_at": "2024-01-01T00:00:00"
}
```

### **2. Déconnexion**

**Via le bouton dans le Navbar** :
- Clique sur "Déconnexion" dans la barre de navigation

**Via l'API** :
```bash
curl -X POST http://localhost:3000/api/logout \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "token=TON_TOKEN"
```

### **3. Vérifier la session**

**Via l'API** :
```bash
curl -X GET http://localhost:3000/api/me \
  -H "Authorization: Bearer TON_TOKEN"
```

**Réponse** :
```json
{
  "username": "admin",
  "role": "admin",
  "email": "admin@ehr-plan.local"
}
```

### **4. Reset Password (Mode Demo)**

**Via la page de login** :
1. Clique sur "Mot de passe oublié ?"
2. Entre ton email
3. Le système génère un nouveau mot de passe (affiché à l'écran)

**Via l'API** :
```bash
curl -X POST http://localhost:3000/api/reset-password \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "email=ton@email.com"
```

**Réponse (mode démo)** :
```json
{
  "message": "Password reset successfully (demo mode). New password generated.",
  "new_password": "abc123def",
  "email": "ton@email.com"
}
```

---

## 🔒 Flux d'Authentification

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Page      │────▶│ POST /api   │────▶│ Validate    │
│   Login     │     │   /login    │     │ Credentials │
└─────────────┘     └─────────────┘     └──────┬──────┘
                                                    │
                   ┌────────────────────────────────┼────────────────────────────────┐
                   │                                    │                            │
                   ▼                                    ▼                            ▼
          ┌─────────────┐     ┌─────────────────┐     ┌─────────────┐
          │ 401 Error   │     │ Generate Session │     │ Save to DB  │
          │ (Invalid)   │     │ Token            │     │ (sessions)  │
          └─────────────┘     └─────────────────┘     └──────┬──────┘
                                                           │
                          ┌────────────────────────────────────────┘
                          │
                          ▼
                  ┌─────────────────┐
                  │ Return Session  │
                  │ Token to Client │
                  └─────────────────┘
                          │
                          ▼
                  ┌─────────────────┐
                  │ Save to         │◀──────────┐
                  │ localStorage    │           │
                  └─────────────────┘            │
                                           ┌───────┴───────┐
                                           │               │
                    ┌──────────────────┴──────┐ ┌─────▼──────────────────┐
                    │                                 │ │                        │
                    ▼                                 ▼ ▼                        ▼
            ┌───────────┐                       ┌─────────────┐
            │ Protected │                       │ Navbar     │
            │  Routes   │                       │ (Login/     │
            │  (Admin)  │                       │  Logout)    │
            └───────────┘                       └─────────────┘
```

---

## 📁 Structure des Fichiers

```
ehr-plan-v3/
├── app/
│   ├── login/
│   │   └── page.tsx              # ✅ NOUVEAU: Page de login
│   └── admin/
│       └── page.tsx              # ✅ MODIFIÉ: Protégé par session
├── components/
│   └── Navbar.tsx                # ✅ MODIFIÉ: Liens login/logout
├── lib/
│   └── session.ts                # ✅ NOUVEAU: Gestion des sessions
└── api/
    └── index.py                  # ✅ MODIFIÉ: Endpoints auth
```

---

## 🛡 Sécurité

### **Stockage** :
- **Tokens** : Stockés dans `localStorage` côté client
- **Mots de passe** : Hashés avec SHA-256 avant stockage en base
- **Sessions** : Stockées en base de données avec date d'expiration (24h)

### **Protéctions** :
1. **Tokens aléatoires** : 64 caractères générés avec `secrets.token_urlsafe()`
2. **Expiration** : Les sessions expirent après 24 heures
3. **Vérification du rôle** : Seuls les utilisateurs avec `role='admin'` peuvent accéder à `/admin`

### **Limitations (Mode Demo)** :
- Le reset password affiche le nouveau mot de passe directement (pas d'email réel)
- Un seul utilisateur par défaut (`admin/admin123`)
- Pour la production, il faudrait :
  - Envoyer un email avec un lien de reset
  - Implémenter la vérification email
  - Chiffrer les mots de passe avec bcrypt au lieu de SHA-256

---

## 🔧 Configuration

### **Variables d'Environnement** (déjà configurées) :
- `TURSO_URL` - URL de la base Turso
- `TURSO_AUTH_TOKEN` - Token d'authentification Turso

### **Utilisateurs** :
L'utilisateur par défaut est créé automatiquement au premier déploiement :
```sql
INSERT INTO users (username, hashed_password, role, email)
VALUES ('admin', sha256('admin123'), 'admin', 'admin@ehr-plan.local');
```

### **Pour ajouter un utilisateur** :
```sql
INSERT INTO users (username, hashed_password, role, email)
VALUES ('nouvel_user', sha256('motdepasse'), 'user', 'email@domaine.com');
```

---

## ⚠️ Résolution des Problèmes

### **Problème : Erreur 500 sur /login**
**Cause** : Variables d'environnement manquantes
**Solution** : Vérifie que `TURSO_URL` et `TURSO_AUTH_TOKEN` sont configurés dans Vercel

### **Problème : "Invalid credentials"**
**Cause** : Mauvais username/mot de passe
**Solution** : Utilise `admin` / `admin123` ou vérifie les données en base

### **Problème : Redirection infinie vers /login**
**Cause** : La session n'est pas validée correctement
**Solution** : 
1. Vérifie que le token est bien sauvegardé dans localStorage
2. Vérifie que `/api/me` retourne les bonnes données
3. Vérifie les logs du navigateur

### **Problème : Le mot de passe reset ne fonctionne pas**
**Cause** : Mode démo - le mot de passe est affichée directement
**Solution** : En production, implémente l'envoi d'email

---

## 📝 Notes Techniques

### **Backend (Python - Vercel Serverless)** :
- Utilise `secrets.token_urlsafe(64)` pour générer les tokens
- Hash les mots de passe avec SHA-256 (`hashlib.sha256`)
- Stocke les sessions avec expiration (24h)
- Valide les tokens à chaque requête protégée

### **Frontend (Next.js 14)** :
- Utilise `localStorage` pour stocker les tokens
- Vérifie la session au chargement des pages protégées
- Redirige automatiquement vers `/login` si non authentifié

### **Compatibilité** :
- Fonctionne en développement local (`npm run dev:full`)
- Fonctionne en production (Vercel)
- Compatible avec Turso Database

---

## 🎓 Exemple d'Utilisation

```typescript
// Dans un composant
import { useSession, login, logout } from '@/lib/session';

function MyComponent() {
  const { user, isLoading, error } = useSession();

  if (isLoading) return <div>Chargement...</div>;
  if (!user) return <div>Veuillez vous connecter</div>;

  return (
    <div>
      <p>Bonjour, {user.username}!</p>
      <p>Rôle: {user.role}</p>
      <button onClick={logout}>Déconnexion</button>
    </div>
  );
}
```

---

**Date** : 2026-09-19  
**Version** : 1.0  
**Statut** : ✅ Implémenté et testé
