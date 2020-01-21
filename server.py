#  coding: utf-8 
import socketserver
import os, mimetypes, urllib

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
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
    
    ROOT = "www"

    def handle(self):
        #ref: https://developer.mozilla.org/en-US/docs/Web/HTTP/Session   
        #ref: https://stackoverflow.com/questions/7585435/best-way-to-convert-string-to-bytes-in-python-3

        try:
            self.data = self.request.recv(1024).strip().decode()
            print ("\n\nGot a request of:\n%s\n" % self.data)
            request_header_list = self.data.splitlines()
            request_method, request_filepath, _ = request_header_list[0].split(" ")
            #print("request_method: ", request_method, request_method == "GET")

            if request_method == "GET":
                relative_filepath = os.path.relpath(MyWebServer.ROOT + request_filepath)
                if "../" in relative_filepath:
                    response_body = bytearray(open(MyWebServer.ROOT + "/404PageNotFound.html").read(), encoding = "utf-8")
                    self.request.send(b"HTTP/1.1 404 Page Not Found\r\n")
                    self.request.send(b"Content-Type: text/html\r\n")
                    self.request.send(b"Content-Length: %d\r\n\r\n" % len(response_body))
                    self.request.sendall(response_body)
                    return

                isExist = os.path.exists(relative_filepath)
                print("Request File Relative Path: %s" % relative_filepath)
                print("Path is %sValid!" % ("" if isExist else "not "))

                if not isExist:
                    response_body = bytearray(open(MyWebServer.ROOT + "/404PageNotFound.html").read(), encoding = "utf-8")
                    self.request.send(b"HTTP/1.1 404 Page Not Found\r\n")
                    self.request.send(b"Content-Type: text/html\r\n")
                    self.request.send(b"Content-Length: %d\r\n\r\n" % len(response_body))
                    self.request.sendall(response_body)
                else:
                    if os.path.isfile(relative_filepath): #file
                        response_body = bytearray(open(relative_filepath).read(), encoding = "utf-8")
                        self.request.send(b"HTTP/1.1 200 OK\r\n")
                        file_type, _ = mimetypes.guess_type(relative_filepath)
                        print("file_type", file_type)
                        self.request.send(bytearray("Content-Type: %s\r\n" % file_type, encoding = "utf-8"))
                        self.request.send(b"Content-Length: %d\r\n\r\n" % len(response_body))
                        self.request.send(response_body)
                    else: #dir
                        if request_filepath[-1] != '/':
                            self.request.send(b"HTTP/1.1 301 Redirect\r\n")
                            response_body = bytearray(open(MyWebServer.ROOT + "/301Redirect.html").read(), encoding = "utf-8")
                            self.request.send(b"Location: %s/\r\n" % bytearray(request_filepath, encoding = 'utf-8'))
                            self.request.send(b"Content-Type: text/html\r\n")
                            self.request.send(b"Content-Length: %d\r\n\r\n" % len(response_body))
                            self.request.send(response_body)
                        else:
                            return_file = relative_filepath + "/index.html"
                            file_type, _ = mimetypes.guess_type(return_file)
                            self.request.send(b"HTTP/1.1 200 OK\r\n")
                            response_body = bytearray(open(return_file).read(), encoding = "utf-8")
                            self.request.send(bytearray("Content-Type: %s\r\n" % file_type, encoding = "utf-8"))
                            self.request.send(b"Content-Length: %d\r\n\r\n" % len(response_body))
                            self.request.send(response_body)
                            
            else: 
                print("Request method is not GET")
                response_body = bytearray(open(MyWebServer.ROOT + "/405MethodNotFound.html").read(), encoding = "utf-8")
                self.request.send(b"HTTP/1.1 405 Method Not Found\r\n")
                self.request.send(b"Content-Type: text/html\r\n")
                self.request.send(b"Content-Length: %d\r\n\r\n" % len(response_body))
                self.request.send(response_body)
        
        except Exception as e:
            print(e)
    
    def send_response(self, header, body = None):
        assert type(header) == bytes, "TypeError: invalid argument type for send_response(): %s" % str(type(header))
        if body != None:
            assert type(body) == bytes, "TypeError: invalid argument type for send_response(): %s" % str(type(header))
        pass
        


if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
