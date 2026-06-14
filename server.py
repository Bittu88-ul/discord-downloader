"""
HTTP Server with URL encoding support - Complete Version
"""

from http.server import HTTPServer, SimpleHTTPRequestHandler
import os
import urllib.parse
from datetime import datetime

class DownloadHandler(SimpleHTTPRequestHandler):
    """Handle file downloads with URL encoding"""
    
    def log_message(self, format, *args):
        """Silence logging"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {args[0] if args else ''}")
    
    def do_GET(self):
        """Serve files"""
        # Decode URL
        parsed = urllib.parse.urlparse(self.path)
        path = urllib.parse.unquote(parsed.path)
        
        # Home page
        if path == '/' or path == '/index.html':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            
            html = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Discord Download Bot</title>
                <meta charset="UTF-8">
                <style>
                    * {
                        margin: 0;
                        padding: 0;
                        box-sizing: border-box;
                    }
                    body {
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        min-height: 100vh;
                        padding: 20px;
                    }
                    .container {
                        max-width: 900px;
                        margin: auto;
                        background: white;
                        border-radius: 20px;
                        padding: 30px;
                        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                    }
                    h1 {
                        color: #667eea;
                        margin-bottom: 10px;
                        display: flex;
                        align-items: center;
                        gap: 10px;
                    }
                    .status {
                        background: #4ade80;
                        color: white;
                        padding: 5px 15px;
                        border-radius: 20px;
                        font-size: 14px;
                        display: inline-block;
                        margin-bottom: 20px;
                    }
                    .file-list {
                        margin-top: 30px;
                    }
                    .file-item {
                        background: #f3f4f6;
                        padding: 15px;
                        margin: 10px 0;
                        border-radius: 10px;
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                        flex-wrap: wrap;
                        gap: 10px;
                    }
                    .file-info {
                        flex: 1;
                        word-break: break-all;
                    }
                    .file-name {
                        font-weight: bold;
                        color: #374151;
                        margin-bottom: 5px;
                    }
                    .file-size {
                        font-size: 12px;
                        color: #6b7280;
                    }
                    .download-btn {
                        background: #667eea;
                        color: white;
                        padding: 8px 20px;
                        border-radius: 8px;
                        text-decoration: none;
                        transition: background 0.3s;
                    }
                    .download-btn:hover {
                        background: #5a67d8;
                    }
                    .copy-btn {
                        background: #9ca3af;
                        color: white;
                        border: none;
                        padding: 8px 15px;
                        border-radius: 8px;
                        cursor: pointer;
                        transition: background 0.3s;
                    }
                    .copy-btn:hover {
                        background: #6b7280;
                    }
                    .empty {
                        text-align: center;
                        padding: 40px;
                        color: #9ca3af;
                    }
                    .footer {
                        margin-top: 30px;
                        text-align: center;
                        color: #9ca3af;
                        font-size: 12px;
                    }
                    @media (max-width: 640px) {
                        .file-item {
                            flex-direction: column;
                            align-items: stretch;
                        }
                        .container {
                            padding: 20px;
                        }
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>
                        <span>📥</span>
                        Discord Download Bot
                    </h1>
                    <div class="status">✅ Server Running</div>
                    <p>Files downloaded from Discord will appear here. Click any file to download.</p>
                    
                    <div class="file-list">
                        <h2>📁 Available Downloads</h2>
            """
            
            # List available files
            if os.path.exists('downloads'):
                files = [f for f in os.listdir('downloads') if f.endswith(('.mp4', '.webm', '.mkv', '.mp3'))]
                if files:
                    # Sort by modification time (newest first)
                    files.sort(key=lambda x: os.path.getmtime(f'downloads/{x}'), reverse=True)
                    for f in files:
                        file_size = os.path.getsize(f'downloads/{f}') / (1024 * 1024)
                        encoded_f = urllib.parse.quote(f)
                        html += f'''
                        <div class="file-item">
                            <div class="file-info">
                                <div class="file-name">🎬 {f}</div>
                                <div class="file-size">{file_size:.2f} MB</div>
                            </div>
                            <div>
                                <a href="/downloads/{encoded_f}" class="download-btn">📥 Download</a>
                                <button class="copy-btn" onclick="copyToClipboard('http://' + window.location.host + '/downloads/{encoded_f}')">📋 Copy Link</button>
                            </div>
                        </div>
                        '''
                else:
                    html += '<div class="empty">📭 No files yet. Download something from Discord first!</div>'
            else:
                html += '<div class="empty">📭 No files yet. Download something from Discord first!</div>'
            
            html += """
                    </div>
                    <div class="footer">
                        <p>Files are automatically deleted after 10 minutes</p>
                        <p>Made with ❤️ for Discord</p>
                    </div>
                </div>
                <script>
                function copyToClipboard(text) {
                    navigator.clipboard.writeText(text).then(function() {
                        alert('✓ Link copied to clipboard!');
                    }, function() {
                        alert('✗ Failed to copy link');
                    });
                }
                </script>
            </body>
            </html>
            """
            self.wfile.write(html.encode())
            return
        
        # Serve files from downloads directory
        if path.startswith('/downloads/'):
            # Extract filename (already decoded)
            filename = path.replace('/downloads/', '', 1)
            filepath = os.path.join('downloads', filename)
            
            print(f"🔍 Looking for: {filename}")
            
            if os.path.exists(filepath) and os.path.isfile(filepath):
                # Get file extension
                ext = os.path.splitext(filename)[1].lower()
                
                # Set content type
                if ext == '.mp4':
                    content_type = 'video/mp4'
                elif ext == '.webm':
                    content_type = 'video/webm'
                elif ext == '.mkv':
                    content_type = 'video/x-matroska'
                elif ext == '.mp3':
                    content_type = 'audio/mpeg'
                else:
                    content_type = 'application/octet-stream'
                
                # Send file
                self.send_response(200)
                self.send_header('Content-Type', content_type)
                self.send_header('Content-Disposition', f'attachment; filename="{filename}"')
                self.send_header('Content-Length', str(os.path.getsize(filepath)))
                self.end_headers()
                
                with open(filepath, 'rb') as f:
                    self.wfile.write(f.read())
                
                print(f"✅ Sent: {filename}")
                return
            else:
                print(f"❌ File not found: {filename}")
                self.send_error(404, f"File not found: {filename}")
                return
        
        # 404 for everything else
        self.send_error(404, f"Page not found: {path}")

def run_server(port=8080):
    """Start server"""
    # Create downloads directory if it doesn't exist
    os.makedirs('downloads', exist_ok=True)
    
    server = HTTPServer(('', port), DownloadHandler)
    print(f"\n{'='*50}")
    print(f"✅ DOWNLOAD SERVER RUNNING")
    print(f"{'='*50}")
    print(f"📍 Local URL: http://localhost:{port}")
    print(f"📁 Download folder: downloads/")
    print(f"🛑 Press Ctrl+C to stop")
    print(f"{'='*50}\n")
    
    # Show existing files
    if os.path.exists('downloads'):
        files = [f for f in os.listdir('downloads') if f.endswith(('.mp4', '.webm', '.mkv', '.mp3'))]
        if files:
            print(f"📁 Existing files ({len(files)}):")
            for f in files:
                size = os.path.getsize(f'downloads/{f}') / (1024 * 1024)
                print(f"   🎬 {f} ({size:.2f} MB)")
        else:
            print("📁 No files yet. Download something from Discord!")
    print()
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
        server.shutdown()

if __name__ == "__main__":
    run_server()