#  coding: utf-8 
import socketserver
import os
import mimetypes


# Copyright 2013 Abram Hindle, Eddie Antonio Santos, Anastasia Borissova
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/

class MyWebServer(socketserver.BaseRequestHandler):

    def handle(self):
        error404 = False
        error301 = False
        statusCode = None
        content = None

        self.data = self.request.recv(1024).strip()
        #print("Got a request of: %s\n" % self.data)
        text = self.data.decode().split("\r\n")
        header = text[0].split(" ")

        # Get method
        method = header[0]

        # Get path
        securePath = (header[1]).replace("../", "")
        #print("PATH:______________", header[1])
        #print("STRIPPED PATH:______________", securePath)
        filePath = os.path.abspath(os.getcwd() + "/www" + securePath)

        if os.path.exists(filePath):
            # https://pythonexamples.org/python-check-if-path-is-file-or-directory/
            if os.path.isdir(filePath):
                if securePath[-1] == '/':
                    filePath = os.path.abspath(os.getcwd() + "/www" + securePath + "index.html")
                else:
                    statusCode = f"301 Moved Permanently to http://127.0.0.1:8080{securePath}/\r\n"
                    content = f"<h1>301 Moved Permanently to http://127.0.0.1:8080{securePath}/</h1>"
                    filePath = os.path.abspath(os.getcwd() + "/www" + securePath + "/index.html")
                    error301 = True
            else:
                filePath = os.path.abspath(os.getcwd() + "/www" + securePath)
        else:
            error404 = True
            statusCode = "404 Not Found\r\n"
            content = "<h1>404 Not Found</h1>"

        # Get protocol
        protocol = header[2]

        # Get MIME type
        # https://docs.python.org/3/library/mimetypes.html
        mimeType = (mimetypes.guess_type(filePath))[0]
        if mimeType is None:
            mimeType = "text/html"
        mimeType = "Content-Type: " + mimeType + "\r\n"


        # Get status code and content
        if method != "GET":
            statusCode = "405 Method Not Allowed\r\n"
            content = "<h1>405 Method Not Allowed</h1>"
        elif not error404 and not error301:
            statusCode = "200 OK\r\n"
            content = open(filePath, "r").read()

        # Send
        response = protocol + " " + statusCode + mimeType + "\r\n" + content + "\r\n"
        self.request.sendall(response.encode())


if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
