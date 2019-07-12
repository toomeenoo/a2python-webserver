# --------------------------------------------------
# Python for web simple library
# Version 1.0.1
# For Apache2 Python3
# Author Tomas Molinari <tomie.molinari@gmail.com>
# --------------------------------------------------

class Weblib:
    def __init__(self):
        import sys, os
        self.string_body = ""
        self.array_headers = []
        self.headers_send = False
        self.apacheVars = os.environ.items()

    def header(self, key, value):
        index = 0
        found = False
        fullkey = key + ": " + value + "\n\n"
        for header in self.array_headers:
            if(header.startswith( key+": " )):
                self.array_headers[index] = fullkey
                found = True
            index += 1
        if(not found):
            self.array_headers.append(fullkey)

    def write(self, data):
        self.string_body += data

    def server(self, key):
        for name, value in self.apacheVars:
            if(name == key):
                return value
        return False

    def query(self, key = "", fallback = False):
        from urllib.parse import parse_qs
        full_qeury = parse_qs(self.server("QUERY_STRING"), True)
        if(key == ""):
            return full_qeury
        elif(key in full_qeury):
            return full_qeury[key]
        return fallback

    def flush(self, do_exit = True):
        have_content_type = False
        if(not self.headers_send):
            for header in self.array_headers:
                if(header.startswith("Content-Type")):
                    have_content_type = True
                print(header)
            if(not have_content_type):
                print("Content-type: text/html\n\n")
            self.headers_send = True
        print(self.string_body)
        self.string_body = ""
        if(do_exit):
            exit()

    def __del__(self):
        self.flush()