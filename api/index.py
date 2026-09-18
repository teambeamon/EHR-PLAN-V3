import json
import os
import requests
import traceback


def handler(request):
    try:
        # Step 1: Check environment variables
        db_url = os.environ.get("TURSO_DATABASE_URL", os.environ.get("TURSO_URL", None))
        auth_token = os.environ.get("TURSO_AUTH_TOKEN", None)
        
        if not db_url:
            return {
                'statusCode': 500,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'error': 'Missing TURSO_DATABASE_URL',
                    'available_keys': list(os.environ.keys())[:10]
                })
            }
        
        if not auth_token:
            return {
                'statusCode': 500,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'error': 'Missing TURSO_AUTH_TOKEN'
                })
            }
        
        # Step 2: Convert URL
        if db_url.startswith('libsql://'):
            http_url = db_url.replace('libsql://', 'https://')
        else:
            http_url = db_url
        
        # Step 3: Get request info
        path = getattr(request, 'path', '/')
        method = getattr(request, 'method', 'GET')
        
        # Step 4: Handle routes
        if path.startswith("/api/salles") and method == "GET":
            response = requests.post(
                f"{http_url}/v2/sql",
                json={"query": "SELECT * FROM salles"},
                headers={"Authorization": f"Bearer {auth_token}"},
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                rows = data.get('result', []).get('rows', []) if isinstance(data.get('result'), dict) else []
                return {
                    'statusCode': 200,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({'salles': rows})
                }
            else:
                return {
                    'statusCode': response.status_code,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({'error': response.text})
                }

        elif path.startswith("/api/matchs") and method == "GET":
            response = requests.post(
                f"{http_url}/v2/sql",
                json={"query": "SELECT * FROM matchs"},
                headers={"Authorization": f"Bearer {auth_token}"},
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                rows = data.get('result', []).get('rows', []) if isinstance(data.get('result'), dict) else []
                return {
                    'statusCode': 200,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({'matchs': rows})
                }
            else:
                return {
                    'statusCode': response.status_code,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({'error': response.text})
                }

        elif path.startswith("/api/classements") and method == "GET":
            response = requests.post(
                f"{http_url}/v2/sql",
                json={"query": """
                    SELECT e.*, 
                           COUNT(m.id) as matchs_joues,
                           SUM(CASE WHEN m.gagnant_id = e.id THEN 1 ELSE 0 END) as victoires
                    FROM équipes e 
                    LEFT JOIN matchs m ON e.id = m.equipe1_id OR e.id = m.equipe2_id
                    GROUP BY e.id, e.nom, e.logo
                    ORDER BY victoires DESC
                """},
                headers={"Authorization": f"Bearer {auth_token}"},
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                rows = data.get('result', []).get('rows', []) if isinstance(data.get('result'), dict) else []
                return {
                    'statusCode': 200,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({'classements': rows})
                }
            else:
                return {
                    'statusCode': response.status_code,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({'error': response.text})
                }

        elif path.startswith("/api/salles") and method == "POST":
            body = json.loads(request.body) if hasattr(request, 'body') and request.body else {}
            response = requests.post(
                f"{http_url}/v2/sql",
                json={"query": "INSERT INTO salles (nom, capacite, type) VALUES (?, ?, ?)", "args": [body.get('nom'), body.get('capacite'), body.get('type', 'Standard')]},
                headers={"Authorization": f"Bearer {auth_token}"},
                timeout=10
            )
            if response.status_code in [200, 201]:
                return {
                    'statusCode': 201,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({'message': 'Salle créée'})
                }
            else:
                return {
                    'statusCode': response.status_code,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({'error': response.text})
                }

        elif path.startswith("/api/matchs") and method == "POST":
            body = json.loads(request.body) if hasattr(request, 'body') and request.body else {}
            response = requests.post(
                f"{http_url}/v2/sql",
                json={"query": "INSERT INTO matchs (salle_id, equipe1_id, equipe2_id, date, statut) VALUES (?, ?, ?, ?, ?)", "args": [body.get('salle_id'), body.get('equipe1_id'), body.get('equipe2_id'), body.get('date'), body.get('statut', 'programmé')]},
                headers={"Authorization": f"Bearer {auth_token}"},
                timeout=10
            )
            if response.status_code in [200, 201]:
                return {
                    'statusCode': 201,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({'message': 'Match créé'})
                }
            else:
                return {
                    'statusCode': response.status_code,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({'error': response.text})
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
