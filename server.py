#  coding: utf-8 
import socketserver
import os, mimetypes

# Copyright 2013 Abram Hindle, Eddie Antonio Santos, Zhonghao Lu
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

# Rference: https://stackoverflow.com/questions/7585435/best-way-to-convert-string-to-bytes-in-python-3
# answered by agf Sep 28 '11 at 15:27, edited by Garrett Hyde Oct 14 '17 at 4:42

# Reference: https://developer.mozilla.org/en-US/docs/Web/HTTP/Session
# modified by MDN contributors in Mar 23 '19.

# Reference: https://stackoverflow.com/questions/43580/how-to-find-the-mime-type-of-a-file-in-python
# edited by jfs June 28 '14 at 16:43, edited by Dave Webb Sep 4 '08 at 12:12

class MyWebServer(socketserver.BaseRequestHandler):

    def handle(self):
        """
        This method handles all the requests received. 
        """

        try:
            self.root = "www"
            self.File301 = "/301MovedPermanently.html"
            self.File404 = "/404PageNotFound.html"
            self.File405 = "/405MethodNotFound.html"

            self.data = self.request.recv(1024).strip().decode()
            print("\nGot a request:\n", self.data)
            dataLines = self.data.splitlines()
            requestMethod, requestFilepath, _ = dataLines[0].split(" ")

            if requestMethod != "GET":
                bodyLength, body, fileType = self.readfile(self.File405)
                header = bytearray(
                            "HTTP/1.1 405 Method Not Found\r\n" \
                            "Content-Type: %s\r\n" \
                            "Content-Length: %d\r\n\r\n" % (fileType, bodyLength),
                            encoding = "utf-8")
                self.sendResponse(header, body)
                return
            
            if self.verify(requestFilepath) == False:
                bodyLength, body, fileType = self.readfile(self.File404)
                header = bytearray(
                            "HTTP/1.1 404 Page Not Found\r\n" \
                            "Content-Type: %s\r\n" \
                            "Content-Length: %d\r\n\r\n" % (fileType, bodyLength),
                            encoding = "utf-8")
                self.sendResponse(header, body)
                return
            
            #path is a folder
            if os.path.isdir(self.root + requestFilepath):
                if requestFilepath[-1] != "/":
                    bodyLength, body, fileType = self.readfile(self.File301)
                    newLocation = requestFilepath + "/"
                    header = bytearray(
                                "HTTP/1.1 301 Moved Permanently\r\n" \
                                "Location: %s\r\n" \
                                "Content-Type: %s\r\n" \
                                "Content-Length: %d\r\n\r\n" % \
                                (newLocation, fileType, bodyLength),
                                encoding = "utf-8")
                    self.sendResponse(header, body)
                    return
                else:
                    bodyLength, body, fileType = self.readfile(requestFilepath + "/index.html")
                    header = bytearray(
                                "HTTP/1.1 200 OK\r\n" \
                                "Content-Type: %s\r\n" \
                                "Content-Length: %d\r\n\r\n" % (fileType, bodyLength),
                                encoding = "utf-8")
                    self.sendResponse(header, body)
                    return
            
            #path is a file
            if os.path.isfile(self.root + requestFilepath):
                bodyLength, body, fileType = self.readfile(requestFilepath)
                header = bytearray(
                            "HTTP/1.1 200 OK\r\n" \
                            "Content-Type: %s\r\n" \
                            "Content-Length: %d\r\n\r\n" % (fileType, bodyLength),
                            encoding = "utf-8")
                self.sendResponse(header, body)
                return

        except Exception as e:
            print(e)
            
            


    def verify(self, path):
        """
        This method verifies if a path exists in the root folder which this 
        server is serving for, note for the sake of security, paths that led
        to locations which is not under the root folder are not valid.

        Args:
            path(str): A relative path of a file to the root folder.

        Returns:
            bool: True if the path exists, False otherwise.
        """
        full_path = self.root + path
        if not os.path.exists(full_path):
            return False
        
        rel_path = os.path.relpath(full_path, self.root)
        if "../" in rel_path:
            return False
        
        return True


    def readfile(self, path):
        """
        This method opens and reads a file.

        Args:
            path(str): A relative path of a file to the root folder.
        
        Returns:
            int: The length of the bytearray. 
            bytearray: The bytearray format of the content read from the file.
            str: Mimetype of the file.
        """ 
        file = open(self.root + path)
        content = bytearray(
            file.read(),
            encoding = "utf-8")
        file.close()
        file_type, _ = mimetypes.guess_type(self.root + path)
        return len(content), content, file_type

    def sendResponse(self, header, body = None):
        """
        This method sends response to a client
        
        Args:
            header(bytes): The response header
            body(bytes/NoneType): The response body, defaults to None
        """
        # assert type(header) == bytearray, "TypeError: invalid argument type for send_response(): %s" % str(type(header))
        # if body != None:
        #     assert type(body) == bytearray, "TypeError: invalid argument type for send_response(): %s" % str(type(header))
        try:
            self.request.sendall(header)
            if body != None:
                self.request.sendall(body)
        except Exception as e:
            print(e)
        return

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
