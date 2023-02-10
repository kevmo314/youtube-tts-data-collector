import http.server
import os

from pytube import YouTube
import tarfile


class Handler(http.server.BaseHTTPRequestHandler):
    def __init__(self):
        super().__init__()

        with open("data.txt", "r") as f:
            self.urls = f.readlines()
        
        # filter out urls that have already been downloaded
        self.urls = [url for url in self.urls if not os.path.exists("data/yt-%s" % YouTube(url.strip()).video_id)]

    def do_POST(self):
        with tarfile.open(fileobj=self.rfile, mode="r:gz") as tf:
            tf.extractall()
        self.send_response(200)
        self.end_headers()
    
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(self.urls.pop().encode("utf-8"))
        

if __name__ == "__main__":
    httpd = http.server.HTTPServer(("", 8000), Handler)