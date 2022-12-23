import socket
import json
import ssl
from enum import Enum
from typing import Dict, Optional, List, Set


class Method(Enum):
    get = 0
    post = 1
    head = 2
    put = 3
    delete = 4


class Protocol(Enum):
    HTTP = 0
    HTTPS = 1


class HttpClient:
    RECEIVE_CHUNK_SIZE = 4096
    BLOCK_BOUNDARY = '0775995b3f2742db7e88858fbb2ede2b'

    def __init__(self, host, timeout=2.0, protocol: Protocol = Protocol.HTTPS):
        self._raw_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        port = 80 if protocol is Protocol.HTTP else 443
        self._raw_socket.connect((socket.gethostbyname(host), port))
        self._raw_socket.settimeout(timeout)
        self.response = None
        self.last_request = None
        self.response_body = None

        ssl.SSLContext.verify_mode = ssl.VerifyMode.CERT_REQUIRED
        self._socket = _wrapped_socket = ssl.wrap_socket(
            sock=self._raw_socket,
            keyfile=None,
            certfile=None,
            server_side=False,
            cert_reqs=ssl.CERT_REQUIRED,
            ssl_version=ssl.PROTOCOL_SSLv23
        ) if protocol == Protocol.HTTPS else self._raw_socket

    def delete(self,
               http_protocol: str = 'HTTP/1.2',
               domain: str = '/',
               to_json: str = False,
               file_data: Dict[str, str] = None,
               cookies: Dict[str, str] = None,
               headers: Dict[str, str] = None) -> str:

        request_body_string, headers_string = self._format_headers_and_requests(cookies, headers, file_data)
        request = f"DELETE {domain} {http_protocol}\r\n" \
                  f"Host: {self.host}\r\n" \
                  f"{headers_string if headers_string else ''}" \
                  f"\r\n\r\n" \
                  f"{request_body_string if request_body_string else ''}"
        self.last_request = request
        request = request.encode('utf-8')

        self._send(request)
        self.response, self.response_body = self._receive()
        if to_json:
            with open(to_json, "w") as f:
                json.dump(self.response, f, ensure_ascii=False, indent=4)
        return self.response

    def put(self,
            http_protocol: str = 'HTTP/1.2',
            domain: str = '/',
            to_json: str = False,
            file_data: Dict[str, str] = None,
            cookies: Dict[str, str] = None,
            headers: Dict[str, str] = None) -> str:

        request_body_string, headers_string = self._format_headers_and_requests(cookies, headers, file_data)
        request = f"PUT {domain} {http_protocol}\r\n" \
                  f"Host: {self.host}\r\n" \
                  f"{headers_string if headers_string else ''}" \
                  f"\r\n\r\n" \
                  f"{request_body_string if request_body_string else ''}"
        self.last_request = request
        request = request.encode('utf-8')

        self._send(request)
        self.response, self.response_body = self._receive()
        if to_json:
            with open(to_json, "w") as f:
                json.dump(self.response, f, ensure_ascii=False, indent=4)
        return self.response

    def head(self,
             http_protocol: str = 'HTTP/1.2',
             domain: str = '/',
             to_json: str = False,
             url_parameters: Dict[str, str] = None,
             form_data: Dict[str, str] = None,
             file_data: Dict[str, str] = None,
             cookies: Dict[str, str] = None,
             headers: Dict[str, str] = None) -> str:

        if url_parameters is not None:
            domain += f"?{self._join_dict(url_parameters, '=', '&')}"
        request_body_string, headers_string = self._format_headers_and_requests(cookies, headers, file_data, form_data)
        request = f"HEAD {domain} {http_protocol}\r\n" \
                  f"{headers_string if headers_string else ''}" \
                  f"\r\n\r\n" \
                  f"{request_body_string if request_body_string else ''}"
        self.last_request = request
        request = request.encode('utf-8')

        self._send(request)
        self.response, self.response_body = self._receive()
        if to_json:
            with open(to_json, "w") as f:
                json.dump(self.response, f, ensure_ascii=False, indent=4)
        return self.response

    def get(self,
            http_protocol: str = 'HTTP/1.2',
            domain: str = '/',
            to_json: str = False,
            url_parameters: Dict[str, str] = None,
            file_data: Dict[str, str] = None,
            form_data: Dict[str, str] = None,
            cookies: Dict[str, str] = None,
            headers: Dict[str, str] = None) -> str:
        if url_parameters is not None:
            domain += f"?{self._join_dict(url_parameters, '=', '&')}"
        request_body_string, headers_string = self._format_headers_and_requests(cookies, headers, file_data, form_data)

        request = f"GET {domain} {http_protocol}\r\n" \
                  f"{headers_string if headers_string else ''}" \
                  f"\r\n\r\n" \
                  f"{request_body_string if request_body_string else ''}"
        self.last_request = request
        request = request.encode('utf-8')

        self._send(request)
        self.response, self.response_body = self._receive()
        if to_json:
            with open(to_json, "w") as f:
                json.dump(self.response, f, ensure_ascii=False, indent=4)
        return self.response

    def post(self,
             http_protocol: str = 'HTTP/1.2',
             domain: str = '/',
             to_json: str = False,
             url_parameters: Dict[str, str] = None,
             file_data: Dict[str, str] = None,
             form_data: Dict[str, str] = None,
             cookies: Dict[str, str] = None,
             headers: Dict[str, str] = None) -> str:

        if url_parameters is not None:
            domain += f"?{self._join_dict(url_parameters, '=', '&')}"
        request_body_string, headers_string = self._format_headers_and_requests(cookies, headers, file_data, form_data)

        request = f"POST {domain} {http_protocol}\r\n" \
                  f"{headers_string if headers_string else ''}" \
                  f"\r\n\r\n" \
                  f"{request_body_string if request_body_string else ''}"
        self.last_request = request
        request = request.encode('utf-8')

        self._send(request)
        self.response, self.response_body = self._receive()
        if to_json:
            with open(to_json, "w") as f:
                json.dump(self.response, f, ensure_ascii=False, indent=4)
        return self.response

    @staticmethod
    def _file_data_to_string(file_data: Dict[str, str]) -> str:
        res = ''
        for file_name in file_data:
            block_header = f'\r\n--{HttpClient.BLOCK_BOUNDARY}\r\n' \
                           f'Content-Disposition: form-data; ' \
                           f'name="{file_name}"; ' \
                           f'filename="{file_name}"'
            res += f'{block_header}' \
                   f'\r\n\r\n' \
                   f'{file_data[file_name]}'
        return res[2:] + f'\r\n--{HttpClient.BLOCK_BOUNDARY}--\r\n'

    def _format_headers_and_requests(self, cookies, heads, file_data=None, form_data=None):
        request_body_string = ''
        if file_data is not None:
            request_body_string = self._file_data_to_string(file_data)
        elif form_data is not None:
            request_body_string = self._join_dict(form_data, '=', '&')

        if cookies is None:
            cookies = {}
        if heads is None:
            heads = {}
        if cookies:
            heads['Cookie'] = self._join_dict(cookies, '=', '; ')
        headers_string = self._join_dict(heads, ': ', '\r\n')
        return request_body_string, headers_string

    @staticmethod
    def _join_dict(d: Dict[str, str], key_val_sep: str, entry_sep: str) -> str:
        return entry_sep.join(
            map(
                lambda key: f'{key}{key_val_sep}{d[key]}', d
            )
        )

    def _send(self, request: bytes) -> None:
        self.last_request = request.decode()
        sent = 0
        while sent < len(request):
            sent = sent + self._socket.send(request[sent:])

    def _receive(self) -> (str, str):
        response = b""
        headers_end_ind = None
        content_length = None

        while headers_end_ind is None or \
                len(response) - headers_end_ind != content_length:

            chunk = self._socket.recv(self.RECEIVE_CHUNK_SIZE)
            response += chunk

            ind = response.find(b'\r\n\r\n')
            if headers_end_ind is None and ind != -1:
                headers = self._get_headers(response)

                content_length = int(headers[b'Content-Length'])
                headers_end_ind = ind + 4

        response_body = response[-content_length:]
        return response.decode(), response_body.decode()

    @staticmethod
    def _get_headers(byte_string: bytes) -> Dict[bytes, bytes]:
        headers = {}

        for line in byte_string.split(b'\r\n'):
            sep_line = line.split(b': ')
            if len(sep_line) == 2:
                header_name, header_value = sep_line
                headers[header_name] = header_value

        return headers

    def close(self) -> None:
        self._socket.close()

