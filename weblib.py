# --------------------------------------------------
# Python for web simple library
# Version 1.0.1
# For Apache2 Python3
# Author Tomas Molinari <tomie.molinari@gmail.com>
# --------------------------------------------------

class Weblib:
    """
    Simple Apache2/CGI handler object

    Attributes
    ----------
    string_body : str
        response content in string format (html, json, ...)
    array_headers : str
        array af ready headers
    headers_send : bool
        was the http headers already sendt
    apacheVars : array
        fetched raw array of Apache2 vriables
    """

    def __init__(self):
        import sys, os
        self.string_body = ""
        self.array_headers = []
        self.headers_send = False
        self.apacheVars = os.environ.items()

    def header(self, key:str, value:str):
        """
        Set HTTP heder

        Parameters
        ----------
        key : str
            Key of HTTP header to set (f.e.: Content-Type)
        value : str
            Value of HTTP header fieid (f.e.: application/json)
        """
        if(self.headers_send):
            raise Exception("Headers was already sent!")
        index = 0
        found = False
        fullkey = key + ":" + value + "\r\n"
        for header in self.array_headers:
            if(key != "Set-Cookie" and header.startswith( key+":" )):
                self.array_headers[index] = fullkey
                found = True
            index += 1
        if(not found):
            self.array_headers.append(fullkey)
        return self

    def write(self, data:str):
        """
        Append to body of output

        Parameters
        ----------
        data : str
            Content to append
        """
        self.string_body += data
        return self

    def server(self, key:str):
        """
        Get Apache variable

        Parameters
        ----------
        key : str
            Variable to get (default containg:)
            HTTP_HOST, HTTP_USER_AGENT, HTTP_ACCEPT, 
            HTTP_ACCEPT_LANGUAGE, HTTP_ACCEPT_ENCODING, 
            HTTP_CONNECTION, HTTP_UPGRADE_INSECURE_REQUESTS, 
            HTTP_CACHE_CONTROL, PATH, SERVER_SIGNATURE, 
            SERVER_SOFTWARE, SERVER_NAME, SERVER_ADDR, 
            SERVER_PORT, REMOTE_ADDR, DOCUMENT_ROOT, 
            REQUEST_SCHEME, CONTEXT_PREFIX, 
            CONTEXT_DOCUMENT_ROOT, SERVER_ADMIN, 
            SCRIPT_FILENAME, REMOTE_PORT, GATEWAY_INTERFACE, 
            SERVER_PROTOCOL, REQUEST_METHOD, QUERY_STRING, 
            REQUEST_URI, SCRIPT_NAME
        """
        for name, value in self.apacheVars:
            if(name == key):
                return value
        return False

    def get(self, key:str = "", fallback = False):
        """
        HTTP get query variable

        Parameters
        ----------
        key : str
            Key to look for, if empty, returns array of all
        fallback : any
            Value to return if key not found
        """
        from urllib.parse import parse_qs
        full_qeury = parse_qs(self.server("QUERY_STRING"), True)
        if(key == ""):
            return full_qeury
        elif(key in full_qeury):
            return full_qeury[key]
        return fallback

    def post(self, key:str = "", fallback = False):
        """
        HTTP post query variable

        Parameters
        ----------
        key : str
            Key to look for, if empty, returns array of all
        fallback : any
            Value to return if key not found
        """
        import sys
        from urllib.parse import parse_qs
        if(self.server("REQUEST_METHOD") != "POST"):
            return fallback
        str_input = ""
        for line in sys.stdin:
            str_input += line
        full_qeury = parse_qs(str_input, True)
        if(key == ""):
            return full_qeury
        elif(key in full_qeury):
            return full_qeury[key]
        return fallback
    
    def flush(self, do_exit:bool = True):
        """
        Send content of buffer (and headers if not sent yet) to client

        Parameters
        ----------
        do_exit : bool
            to end script execution
        """
        headers_str = ""
        have_content_type = False
        if(not self.headers_send):
            for header in self.array_headers:
                if(header.startswith("Content-Type")):
                    have_content_type = True
                    headers_str = header + headers_str
                else:
                    headers_str += header
            if(not have_content_type):
                headers_str = "Content-type: text/html\r\n" + headers_str
            print(headers_str)
            self.headers_send = True
        print(self.string_body)
        self.string_body = ""
        if(do_exit):
            exit()
        return self

    def setcookie(self, name : str, value : str, duration_or_date = None, domain = None, path = None, secure = None, http_only = None):
        """
        Create Set-Cookie HTTP header

        Parameters
        ----------
        name : str
            name of cookie to set
        value : str
            value of cookie to set
        duration_or_date : None | str | int
            Set expire tome of cookie, int of seconds or str: rfc1123-date | rfc850-date | asctime-date
        domain : None | str
            Domain to be used for cookie
        path : None | str
            Path (url related) to set cookie
        secure : None | bool
            Allow use of https only
        http_only : None | bool
            Allow access to cookie only from http, not from javascript / frontend
        """
        from urllib.parse import quote
        content = quote(name) + "=" + quote(value)
        if(isinstance(duration_or_date, int)):
            content += "; Max-Age="+str(duration_or_date)
        elif(isinstance(duration_or_date, str)):
            content += "; Expires="+duration_or_date
        if(isinstance(domain, str)):
            content += "; Domain="+domain
        if(isinstance(path, str)):
            content += "; Path="+domain
        if(isinstance(secure, bool) and secure):
            content += "; Secure"
        if(isinstance(http_only, bool) and http_only):
            content += "; HttpOnly"
        self.header("Set-Cookie", content)
        return self

    def __del__(self):
        self.flush()