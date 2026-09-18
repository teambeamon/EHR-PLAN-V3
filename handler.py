import json
import os
import requests


async def handler(request):
    # Get Turso configuration from environment
    db_url = os.environ.get("TURSO_DATABASE_URL", os.environ.get("TURSO_URL", None))
    auth_token = os.environ.get("TURSO_AUTH_TOKEN", None)
    
    # For debugging: return env info if something is missing
    if not db_url or not auth_token:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'error': 'Missing environment variables',
                'TURSO_DATABASE_URL': db_url,
                'TURSO_AUTH_TOKEN': '*** REDACTED ***' if auth_token else None
            })
        }
    
    # Convert libsql:// URL to HTTPS URL for REST API
    if db_url and db_url.startswith('libsql://'):
        http_url = db_url.replace('libsql://', 'https://')
    else:
        http_url = db_url

    # Get the path from the request
    path = request.path
    method = request.method

    try:
        # Route handling
        if path.startswith("/api/salles") and method == "GET":
            response = requests.post(
                f"{http_url}/v2/sql",
                json={"query": "SELECT * FROM salles"},
                headers={"Authorization": f"Bearer {auth_token}"}
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
                headers={"Authorization": f"Bearer {auth_token}"}
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
                headers={"Authorization": f"Bearer {auth_token}"}
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
            body = json.loads(request.body)
            response = requests.post(
                f"{http_url}/v2/sql",
                json={"query": "INSERT INTO salles (nom, capacite, type) VALUES (?, ?, ?)", "args": [body.get('nom'), body.get('capacite'), body.get('type', 'Standard')]},
                headers={"Authorization": f"Bearer {auth_token}"}
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
            body = json.loads(request.body)
            response = requests.post(
                f"{http_url}/v2/sql",
                json={"query": "INSERT INTO matchs (salle_id, equipe1_id, equipe2_id, date, statut) VALUES (?, ?, ?, ?, ?)", "args": [body.get('salle_id'), body.get('equipe1_id'), body.get('equipe2_id'), body.get('date'), body.get('statut', 'programmé')]},
                headers={"Authorization": f"Bearer {auth_token}"}
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
                'body': json.dumps({'error': 'Not found'})
            }

    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e)})
        }

# Vercel Python requires one of these to be defined at the top level
app = handler
application = handler
