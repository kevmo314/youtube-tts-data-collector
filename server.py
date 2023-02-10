import http.server
import io
import os
import random
import tarfile

from pytube import YouTube


class Handler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        data = self.rfile.read(int(self.headers["Content-Length"]))
        with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as tf:
            tf.extractall()
        self.send_response(200)
        self.end_headers()
    
    def do_GET(self):
        with open("data.txt", "r") as f:
            urls = [url.strip() for url in f.readlines() if not os.path.exists("data/yt-%s" % YouTube(url.strip()).video_id)]
            if len(urls) == 0:
                self.send_response(404)
                self.end_headers()
                return
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        urls = random.sample(urls, 16)
        self.wfile.write("\n".join(urls).encode("utf-8"))
        

if __name__ == "__main__":
    httpd = http.server.HTTPServer(("", 8000), Handler)
    httpd.serve_forever()