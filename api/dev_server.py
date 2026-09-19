"""
Development server for EHR Plan V3 API
Run with: python -m uvicorn api.dev_server:app --reload --port 8000
"""
import json
import os
import sys
from pathlib import Path

# Add parent directory to path so we can import index
sys.path.insert(0, str(Path(__file__).parent))

from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
from api.index import handler


class VercelRequest:
    """Convert HTTP request to Vercel Serverless Function format"""
    def __init__(self, method, path, headers, body):
        self.method = method
        self.path = path
        self.headers = headers
        self.body = body


class DevHandler(BaseHTTPRequestHandler):
    """HTTP request handler that routes to our Vercel function"""
    
    def do_GET(self):
        self.handle_request("GET")
    
    def do_POST(self):
        self.handle_request("POST")
    
    def do_PUT(self):
        self.handle_request("PUT")
    
    def do_DELETE(self):
        self.handle_request("DELETE")
    
    def handle_request(self, method):
        # Parse URL
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        
        # Read body
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length) if content_length > 0 else b''
        
        # Convert to string
        body_str = body.decode('utf-8') if body else ''
        
        # Create Vercel-style request
        vercel_request = VercelRequest(
            method=method,
            path=path,
            headers=dict(self.headers),
            body=body_str
        )
        
        # Call our handler
        try:
            result = handler(vercel_request)
            
            # Send response
            self.send_response(result.get('statusCode', 200))
            self.send_header('Content-Type', result.get('headers', {}).get('Content-Type', 'application/json'))
            
            # Add other headers
            for key, value in result.get('headers', {}).items():
                if key.lower() != 'content-type':
                    self.send_header(key, value)
            
            self.end_headers()
            self.wfile.write(result.get('body', b'').encode('utf-8') if isinstance(result.get('body'), str) else result.get('body', b''))
        
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e), 'type': type(e).__name__}).encode('utf-8'))
    
    def log_message(self, format, *args):
        # Suppress default logging
        pass


def run_server(port=8000):
    """Run the development server"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, DevHandler)
    print(f"EHR Plan V3 API Development Server running on http://localhost:{port}")
    print("Press Ctrl+C to stop")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped")


if __name__ == '__main__':
    run_server()
