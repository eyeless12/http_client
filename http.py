import socket
import json
from enum import Enum
from typing import Dict, Optional, List, Set


class HttpClient:
    RECEIVE_CHUNK_SIZE = 4096
    BLOCK_BOUNDARY = '0775995b3f2742db7e88858fbb2ede2b'

    class Method(Enum):
        GET = 'GET'
        POST = 'POST'

    def __init__(self, host):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        self.socket.connect((socket.gethostbyname(host), 80))
        self.response = None
        self.response_body = None

    def send(self,
             method: Method,
             http_protocol: str = 'HTTP/1.2',
             domain: str = '/',
             to_json: bool = False,
             url_parameters: Dict[str, str] = None,
             form_data: Dict[str, str] = None,
             file_data: Dict[str, str] = None,
             cookies: Dict[str, str] = None,
             headers: Dict[str, str] = None) -> str:

        if url_parameters is not None:
            domain += f"?{self._join_dict(url_parameters, '=', '&')}"

        request_body_string = ''
        if file_data is not None:
            request_body_string = self._file_data_to_string(file_data)
        elif form_data is not None:
            request_body_string = self._join_dict(form_data, '=', '&')

        if cookies is None:
            cookies = {}
        if headers is None:
            headers = {}
        if file_data is not None:
            headers['Content-Type'] = f'multipart/form-data; ' \
                                      f'boundary={self.BLOCK_BOUNDARY}'
        elif url_parameters is not None or form_data is not None:
            headers['Content-Type'] = 'application/x-www-form-urlencoded'
        if method == self.Method.POST:
            headers['Content-Length'] = len(request_body_string.encode('utf-8'))
        if cookies:
            headers['Cookie'] = self._join_dict(cookies, '=', '; ')
        headers_string = self._join_dict(headers, ': ', '\r\n')

        request = f"{method.value} {domain} {http_protocol}\r\n" \
                  f"Host: {self.host}\r\n"\
                  f"{headers_string if headers_string else ''}" \
                  f"\r\n\r\n" \
                  f"{request_body_string if request_body_string else ''}"
        print(request)
        request = request.encode('utf-8')

        self._send(request)
        self.response, self.response_body = self._receive()
        if to_json:
            with open("response.json", "w") as f:
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

    @staticmethod
    def _join_dict(d: Dict[str, str], key_val_sep: str, entry_sep: str) -> str:
        return entry_sep.join(
            map(
                lambda key: f'{key}{key_val_sep}{d[key]}', d
            )
        )

    def _send(self, request: bytes) -> None:
        sent = 0
        while sent < len(request):
            sent = sent + self.socket.send(request[sent:])

    def _receive(self) -> (str, str):
        response = b""
        headers_end_ind = None
        content_length = None

        while headers_end_ind is None or \
                len(response) - headers_end_ind != content_length:

            chunk = self.socket.recv(self.RECEIVE_CHUNK_SIZE)
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
        self.socket.close()


def main():
    sender = HttpClient("httpbin.org")

    sender.send(sender.Method.GET, to_json=True)
    print(sender.response)


if __name__ == "__main__":
    main()
