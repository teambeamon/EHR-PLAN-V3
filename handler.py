import json
import os
from libsql import Client


async def handler(request):
    # Debug: Check if environment variables are available
    db_url = os.environ.get("TURSO_DATABASE_URL", os.environ.get("TURSO_URL", "libsql://localhost"))
    auth_token = os.environ.get("TURSO_AUTH_TOKEN")
    
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
    
    # Initialize Turso client
    try:
        turso = Client(url=db_url, auth_token=auth_token)
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': f'Failed to create Turso client: {str(e)}'})
        }

    # Get the path from the request
    path = request.path
    method = request.method

    try:
        # Route handling
        if path.startswith("/api/salles") and method == "GET":
            result = turso.execute("SELECT * FROM salles")
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'salles': result.rows})
            }

        elif path.startswith("/api/matchs") and method == "GET":
            result = turso.execute("SELECT * FROM matchs")
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'matchs': result.rows})
            }

        elif path.startswith("/api/classements") and method == "GET":
            result = turso.execute("""
                SELECT e.*, 
                       COUNT(m.id) as matchs_joues,
                       SUM(CASE WHEN m.gagnant_id = e.id THEN 1 ELSE 0 END) as victoires
                FROM équipes e 
                LEFT JOIN matchs m ON e.id = m.equipe1_id OR e.id = m.equipe2_id
                GROUP BY e.id, e.nom, e.logo
                ORDER BY victoires DESC
            """)
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'classements': result.rows})
            }

        elif path.startswith("/api/salles") and method == "POST":
            body = json.loads(request.body)
            turso.execute(
                "INSERT INTO salles (nom, capacite, type) VALUES (?, ?, ?)",
                [body.get('nom'), body.get('capacite'), body.get('type', 'Standard')]
            )
            return {
                'statusCode': 201,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'message': 'Salle créée'})
            }

        elif path.startswith("/api/matchs") and method == "POST":
            body = json.loads(request.body)
            turso.execute(
                "INSERT INTO matchs (salle_id, equipe1_id, equipe2_id, date, statut) VALUES (?, ?, ?, ?, ?)",
                [body.get('salle_id'), body.get('equipe1_id'), body.get('equipe2_id'), 
                 body.get('date'), body.get('statut', 'programmé')]
            )
            return {
                'statusCode': 201,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'message': 'Match créé'})
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
