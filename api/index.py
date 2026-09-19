import json
import os
import requests
import traceback
import hashlib
import secrets
import uuid
from datetime import datetime, timedelta


def _hash(text: str) -> str:
    """Hash a string using SHA256"""
    return hashlib.sha256(text.encode()).hexdigest()


def _get_db_connection():
    """Get or create a connection to Turso database"""
    db_url = os.environ.get("TURSO_URL", os.environ.get("NEXT_PUBLIC_TURSO_URL", None))
    auth_token = os.environ.get("TURSO_AUTH_TOKEN", os.environ.get("NEXT_PUBLIC_TURSO_AUTH_TOKEN", None))
    
    if not db_url or not auth_token:
        return None
    
    if db_url.startswith('libsql://'):
        http_url = db_url.replace('libsql://', 'https://')
    else:
        http_url = db_url
    
    return {
        'url': http_url,
        'token': auth_token
    }


def _db_execute(db_conn, sql: str, params=None):
    """Execute a SQL query and return results"""
    if not db_conn:
        return None
    
    payload = {"query": sql}
    if params:
        payload["args"] = params
    
    try:
        response = requests.post(
            f"{db_conn['url']}/v2/sql",
            json=payload,
            headers={"Authorization": f"Bearer {db_conn['token']}"},
            timeout=10
        )
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print(f"DB Error: {e}")
        return None


def _init_db(db_conn):
    """Initialize database tables for users, sessions, and application data"""
    # Users table
    _db_execute(db_conn, """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            hashed_password TEXT NOT NULL,
            email TEXT,
            role TEXT DEFAULT 'user',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Sessions table
    _db_execute(db_conn, """
        CREATE TABLE IF NOT EXISTS sessions (
            token TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            expires_at TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    
    # Salles table
    _db_execute(db_conn, """
        CREATE TABLE IF NOT EXISTS salles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            capacite INTEGER DEFAULT 0,
            type TEXT DEFAULT 'Standard'
        )
    """)
    
    # Équipes table
    _db_execute(db_conn, """
        CREATE TABLE IF NOT EXISTS équipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            logo TEXT
        )
    """)
    
    # Matchs table
    _db_execute(db_conn, """
        CREATE TABLE IF NOT EXISTS matchs (
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
        )
    """)
    
    # Insert default admin user if not exists
    try:
        result = _db_execute(db_conn, "SELECT id FROM users WHERE username = ?", ["admin"])
        if not result or not result.get('result') or len(result['result']['rows']) == 0:
            hashed = _hash("admin123")
            _db_execute(db_conn, """
                INSERT INTO users (username, hashed_password, role, email, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, ["admin", hashed, "admin", "admin@ehr-plan.local", datetime.now().isoformat()])
    except:
        pass
    
    # Insert sample data if tables are empty
    try:
        result = _db_execute(db_conn, "SELECT COUNT(*) as count FROM salles")
        if result and result.get('result') and result['result']['rows'][0]['count'] == 0:
            _db_execute(db_conn, "INSERT INTO salles (nom, capacite, type) VALUES (?, ?, ?)", ["Salle A", 20, "Compétition"])
            _db_execute(db_conn, "INSERT INTO salles (nom, capacite, type) VALUES (?, ?, ?)", ["Salle B", 15, "Entraînement"])
            
        result = _db_execute(db_conn, "SELECT COUNT(*) as count FROM équipes")
        if result and result.get('result') and result['result']['rows'][0]['count'] == 0:
            _db_execute(db_conn, "INSERT INTO équipes (nom) VALUES (?)", ["Équipe Rouge"])
            _db_execute(db_conn, "INSERT INTO équipes (nom) VALUES (?)", ["Équipe Bleue"])
            _db_execute(db_conn, "INSERT INTO équipes (nom) VALUES (?)", ["Équipe Verte"])
            
        result = _db_execute(db_conn, "SELECT COUNT(*) as count FROM matchs")
        if result and result.get('result') and result['result']['rows'][0]['count'] == 0:
            _db_execute(db_conn, """
                INSERT INTO matchs (salle_id, équipe1_id, équipe2_id, date, statut)
                VALUES (?, ?, ?, ?, ?)
            """, [1, 1, 2, datetime.now().isoformat(), "programmé"])
    except:
        pass


def handler(request):
    import urllib.parse
    
    try:
        # Step 1: Check environment variables and initialize DB
        db_conn = _get_db_connection()
        
        if not db_conn:
            return {
                'statusCode': 500,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'error': 'Missing TURSO_URL or TURSO_AUTH_TOKEN',
                    'available_keys': list(os.environ.keys())[:10]
                })
            }
        
        # Initialize database (create tables if not exist + default admin user)
        _init_db(db_conn)
        
        # Step 2: Get request info
        path = getattr(request, 'path', '/')
        method = getattr(request, 'method', 'GET')
        body = getattr(request, 'body', '')
        
        # Parse form data if present
        parsed_body = {}
        if body and method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            try:
                parsed_body = {k: v[0] if isinstance(v, list) else v for k, v in urllib.parse.parse_qs(body).items()}
            except:
                try:
                    parsed_body = json.loads(body)
                except:
                    parsed_body = {}
        
        # Helper to get form value
        def get_form(key: str, default=''):
            return parsed_body.get(key, default)
        
        # Step 3: Handle authentication routes
        
        # --- LOGIN ---
        if path == "/api/login" and method == "POST":
            username = get_form('username')
            password = get_form('password')
            
            if not username or not password:
                return {
                    'statusCode': 400,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({'error': 'Username and password required'})
                }
            
            # Find user in database
            result = _db_execute(db_conn, """
                SELECT id, username, hashed_password, role FROM users WHERE username = ?
            """, [username])
            
            if not result or not result.get('result') or len(result['result']['rows']) == 0:
                return {
                    'statusCode': 401,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({'error': 'Invalid credentials'})
                }
            
            user = result['result']['rows'][0]
            hashed_input = _hash(password)
            
            if user['hashed_password'] != hashed_input:
                return {
                    'statusCode': 401,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({'error': 'Invalid credentials'})
                }
            
            # Generate session token (expires in 24 hours)
            session_token = secrets.token_urlsafe(64)
            expires_at = (datetime.now() + timedelta(hours=24)).isoformat()
            
            # Store session in database
            _db_execute(db_conn, """
                INSERT INTO sessions (token, user_id, expires_at)
                VALUES (?, ?, ?)
            """, [session_token, user['id'], expires_at])
            
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'token': session_token,
                    'username': user['username'],
                    'role': user['role'],
                    'expires_at': expires_at
                })
            }
        
        # --- LOGOUT ---
        if path == "/api/logout" and method == "POST":
            token = get_form('token')
            if token:
                _db_execute(db_conn, "DELETE FROM sessions WHERE token = ?", [token])
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'message': 'Logged out successfully'})
            }
        
        # --- RESET PASSWORD ---
        if path == "/api/reset-password" and method == "POST":
            email = get_form('email')
            
            if not email:
                return {
                    'statusCode': 400,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({'error': 'Email required'})
                }
            
            # In demo mode, just generate a new password for the admin user
            # In production, you would send an email with a reset link
            new_password = secrets.token_urlsafe(8)
            hashed_password = _hash(new_password)
            
            # For demo: update admin password
            _db_execute(db_conn, """
                UPDATE users SET hashed_password = ?, email = ? WHERE username = 'admin'
            """, [hashed_password, email])
            
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'message': 'Password reset successfully (demo mode). New password generated.',
                    'new_password': new_password,
                    'email': email
                })
            }
        
        # --- GET CURRENT USER ---
        if path == "/api/me" and method == "GET":
            token = get_form('token')
            if not token:
                # Try to get from Authorization header
                headers = getattr(request, 'headers', {})
                auth_header = headers.get('authorization', '') if isinstance(headers, dict) else ''
                if auth_header.startswith('Bearer '):
                    token = auth_header[7:]  # Remove 'Bearer ' prefix
            
            if not token:
                # Try to get from query params
                parsed = urllib.parse.urlparse(path)
                query_params = urllib.parse.parse_qs(parsed.query)
                token = query_params.get('token', [None])[0]
            
            if not token:
                return {
                    'statusCode': 401,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({'error': 'Token required'})
                }
            
            result = _db_execute(db_conn, """
                SELECT u.id, u.username, u.role, u.email
                FROM users u
                JOIN sessions s ON u.id = s.user_id
                WHERE s.token = ? AND s.expires_at > CURRENT_TIMESTAMP
            """, [token])
            
            if not result or not result.get('result') or len(result['result']['rows']) == 0:
                return {
                    'statusCode': 401,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({'error': 'Invalid or expired token'})
                }
            
            user = result['result']['rows'][0]
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'username': user['username'],
                    'role': user['role'],
                    'email': user['email']
                })
            }
        
        # Step 4: Handle other routes using the new DB helper
        # --- GET SALLES ---
        if path.startswith("/api/salles") and method == "GET":
            result = _db_execute(db_conn, "SELECT * FROM salles")
            if result and result.get('result'):
                rows = result['result'].get('rows', []) if isinstance(result['result'], dict) else []
                return {
                    'statusCode': 200,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({'salles': rows})
                }
            else:
                return {
                    'statusCode': 500,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({'error': 'Database error'})
                }

        # --- POST SALLES ---
        elif path.startswith("/api/salles") and method == "POST":
            nom = get_form('nom')
            capacite = get_form('capacite', 0)
            type_salle = get_form('type', 'Standard')
            
            result = _db_execute(db_conn, """
                INSERT INTO salles (nom, capacite, type) VALUES (?, ?, ?)
            """, [nom, int(capacite) if capacite else 0, type_salle])
            
            if result:
                return {
                    'statusCode': 201,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({'message': 'Salle créée'})
                }
            else:
                return {
                    'statusCode': 500,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({'error': 'Failed to create salle'})
                }

        # --- GET MATCHS ---
        elif path.startswith("/api/matchs") and method == "GET":
            result = _db_execute(db_conn, "SELECT * FROM matchs")
            if result and result.get('result'):
                rows = result['result'].get('rows', []) if isinstance(result['result'], dict) else []
                return {
                    'statusCode': 200,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({'matchs': rows})
                }
            else:
                return {
                    'statusCode': 500,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({'error': 'Database error'})
                }

        # --- POST MATCHS ---
        elif path.startswith("/api/matchs") and method == "POST":
            salle_id = get_form('salle_id')
            equipe1_id = get_form('equipe1_id')
            equipe2_id = get_form('equipe2_id')
            date_match = get_form('date')
            statut = get_form('statut', 'programmé')
            
            result = _db_execute(db_conn, """
                INSERT INTO matchs (salle_id, equipe1_id, equipe2_id, date, statut) 
                VALUES (?, ?, ?, ?, ?)
            """, [int(salle_id) if salle_id else 1, 
                   int(equipe1_id) if equipe1_id else 1, 
                   int(equipe2_id) if equipe2_id else 2,
                   date_match, statut])
            
            if result:
                return {
                    'statusCode': 201,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({'message': 'Match créé'})
                }
            else:
                return {
                    'statusCode': 500,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({'error': 'Failed to create match'})
                }

        # --- GET CLASSEMENTS ---
        elif path.startswith("/api/classements") and method == "GET":
            result = _db_execute(db_conn, """
                SELECT e.*, 
                       COUNT(m.id) as matchs_joues,
                       SUM(CASE WHEN m.gagnant_id = e.id THEN 1 ELSE 0 END) as victoires
                FROM équipes e 
                LEFT JOIN matchs m ON e.id = m.equipe1_id OR e.id = m.equipe2_id
                GROUP BY e.id, e.nom, e.logo
                ORDER BY victoires DESC
            """)
            if result and result.get('result'):
                rows = result['result'].get('rows', []) if isinstance(result['result'], dict) else []
                return {
                    'statusCode': 200,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({'classements': rows})
                }
            else:
                return {
                    'statusCode': 500,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({'error': 'Database error'})
                }

        else:
            return {
                'statusCode': 404,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Not found', 'path': path, 'method': method})
            }

    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'error': str(e),
                'type': type(e).__name__
            })
        }

# Vercel Python Runtime v3 requires explicit exports
__all__ = ['handler']
app = handler
application = handler
