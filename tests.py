import random
import unittest
from http import HttpClient, Protocol
from parse_url import Parser


class Extensions_Tests(unittest.TestCase):

    def setUp(self) -> None:
        self.file_data = {
            f"a{self._create_sequence(10)}.{self._create_sequence(3)}": f"{self._create_sequence(50)}",
            f"b{self._create_sequence(10)}.{self._create_sequence(3)}": f"{self._create_sequence(50)}",
            f"c{self._create_sequence(10)}.{self._create_sequence(3)}": f"{self._create_sequence(50)}",
            f"d{self._create_sequence(10)}.{self._create_sequence(3)}": f"{self._create_sequence(50)}"
        }

        self.headers = {
            f"a{self._create_sequence(10)}": f"{self._create_sequence(25)}",
            f"b{self._create_sequence(10)}": f"{self._create_sequence(25)}",
            f"c{self._create_sequence(10)}": f"{self._create_sequence(25)}"
        }

        self.forms = {
            f"a{self._create_sequence(7)}": f"{self._create_sequence(20)}",
            f"b{self._create_sequence(7)}": f"{self._create_sequence(20)}",
            f"c{self._create_sequence(7)}": f"{self._create_sequence(20)}"
        }

        self.cookies = {
            f"a{self._create_sequence(12)}": f"{self._create_sequence(30)}",
            f"b{self._create_sequence(12)}": f"{self._create_sequence(30)}",
            f"c{self._create_sequence(12)}": f"{self._create_sequence(30)}"
        }

        self.url_parameters = {
            f"a{self._create_sequence(20)}": f"{self._create_sequence(25)}",
            f"b{self._create_sequence(20)}": f"{self._create_sequence(25)}",
            f"c{self._create_sequence(20)}": f"{self._create_sequence(25)}"
        }

        self.client = HttpClient("httpbin.org")

    def _create_sequence(self, length: int) -> str:
        alphabet = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'
        return ''.join([random.choice(alphabet) for _ in range(length)])

    def test_correct_file_data(self):
        keys = list(self.file_data.keys())
        values = list(self.file_data.values())

        expected = (
            f"--{HttpClient.BLOCK_BOUNDARY}\r\n"
            f'Content-Disposition: form-data; name="{keys[0]}"; filename="{keys[0]}"\r\n'
            '\r\n'
            f'{values[0]}\r\n'
            f"--{HttpClient.BLOCK_BOUNDARY}\r\n"
            f'Content-Disposition: form-data; name="{keys[1]}"; filename="{keys[1]}"\r\n'
            '\r\n'
            f'{values[1]}\r\n'
            f"--{HttpClient.BLOCK_BOUNDARY}\r\n"
            f'Content-Disposition: form-data; name="{keys[2]}"; filename="{keys[2]}"\r\n'
            '\r\n'
            f'{values[2]}\r\n'
            f"--{HttpClient.BLOCK_BOUNDARY}\r\n"
            f'Content-Disposition: form-data; name="{keys[3]}"; filename="{keys[3]}"\r\n'
            '\r\n'
            f'{values[3]}\r\n'
            f"--{HttpClient.BLOCK_BOUNDARY}--\r\n"
        )

        actual = HttpClient._file_data_to_string(self.file_data)
        self.assertIsNotNone(actual)
        self.assertEqual(expected, actual)

    def test_request_without_anything(self):
        actual_body, actual_headers = self.client._format_headers_and_requests(heads=None, cookies=None)
        expected_body, expected_headers = "", ""

        self.assertEqual(actual_body, expected_body)
        self.assertEqual(actual_headers, expected_headers)

    def test_request_only_cookies_and_headers(self):
        _, actual_headers = self.client._format_headers_and_requests(heads=self.headers, cookies=self.cookies)
        headers_keys = list(self.headers.keys())
        headers_values = list(self.headers.values())
        expected = (
            f"{headers_keys[0]}: {headers_values[0]}\r\n"
            f"{headers_keys[1]}: {headers_values[1]}\r\n"
            f"{headers_keys[2]}: {headers_values[2]}\r\n"
            f"Cookie: {HttpClient._join_dict(self.cookies, '=', '; ')}"
        )
        self.assertEqual(actual_headers, expected)

    def test_request_with_file_body(self):
        actual_body, _ = self.client._format_headers_and_requests(
            heads=self.headers,
            cookies=self.cookies,
            file_data=self.file_data
        )

        file_keys = list(self.file_data.keys())
        file_values = list(self.file_data.values())
        expected = (
            f"--{HttpClient.BLOCK_BOUNDARY}\r\n"
            f'Content-Disposition: form-data; name="{file_keys[0]}"; filename="{file_keys[0]}"\r\n'
            '\r\n'
            f'{file_values[0]}\r\n'
            f"--{HttpClient.BLOCK_BOUNDARY}\r\n"
            f'Content-Disposition: form-data; name="{file_keys[1]}"; filename="{file_keys[1]}"\r\n'
            '\r\n'
            f'{file_values[1]}\r\n'
            f"--{HttpClient.BLOCK_BOUNDARY}\r\n"
            f'Content-Disposition: form-data; name="{file_keys[2]}"; filename="{file_keys[2]}"\r\n'
            '\r\n'
            f'{file_values[2]}\r\n'
            f"--{HttpClient.BLOCK_BOUNDARY}\r\n"
            f'Content-Disposition: form-data; name="{file_keys[3]}"; filename="{file_keys[3]}"\r\n'
            '\r\n'
            f'{file_values[3]}\r\n'
            f"--{HttpClient.BLOCK_BOUNDARY}--\r\n"
        )
        self.assertEqual(actual_body, expected)

    def test_request_with_form_body(self):
        actual_body, _ = self.client._format_headers_and_requests(
            heads=self.headers,
            cookies=self.cookies,
            form_data=self.forms
        )

        form_keys = list(self.forms.keys())
        form_values = list(self.forms.values())

        expected = '&'.join([f'{form_keys[i]}={form_values[i]}' for i in range(len(form_keys))])
        self.assertEqual(actual_body, expected)

    def test_join_dict(self):
        headers_keys = list(self.headers.keys())
        headers_values = list(self.headers.values())

        get_key_val_sep = lambda: random.choice(['!"#$%&()*+,-./:;<=>?@[]^_`{|}~'])
        get_entry_sep = lambda: random.choice(['!"#$%&()*+,-./:;<=>?@[]^_`{|}~'])
        get_expected = lambda kvs, es: f'{headers_keys[0]}{kvs}{headers_values[0]}{es}{headers_keys[1]}{kvs}{headers_values[1]}{es}{headers_keys[2]}{kvs}{headers_values[2]}'

        for _ in range(100):
            key_value_sep = get_key_val_sep()
            entry_sep = get_entry_sep()

            self.assertEqual(HttpClient._join_dict(self.headers, key_value_sep, entry_sep),
                             get_expected(key_value_sep, entry_sep))

    def test_get_without_parameters(self):
        protocol = 'HTTP/1.2'
        _ = self.client.get(http_protocol=protocol)

        expected = f'GET / {protocol}\r\n\r\n\r\n'
        actual_request = self.client.last_request

        self.assertEqual(actual_request, expected)

    def test_with_certain_domain(self):
        protocol = 'HTTP/1.2'
        domain = f'{self._create_sequence(10)}/'
        _ = self.client.get(http_protocol=protocol, domain=domain)

        expected = f'GET {domain} {protocol}\r\n\r\n\r\n'
        actual_request = self.client.last_request

        self.assertEqual(actual_request, expected)

    def test_get_with_parameters(self):
        protocol = 'HTTP/1.2'
        domain = f'{self._create_sequence(10)}/'
        _ = self.client.get(
            http_protocol=protocol,
            domain=domain,
            url_parameters=self.url_parameters,
            file_data=self.file_data,
            cookies=self.cookies,
            headers=self.headers
        )

        expected_request = self._request_with_parameters('GET', domain, protocol, True)
        actual_request = self.client.last_request

        self.assertEqual(actual_request, expected_request)

    def test_post_without_parameters(self):
        protocol = 'HTTP/1.2'
        _ = self.client.post(http_protocol=protocol)

        expected = f'POST / {protocol}\r\n\r\n\r\n'
        actual_request = self.client.last_request

        self.assertEqual(actual_request, expected)

    def test_post_with_parameters(self):
        protocol = 'HTTP/1.2'
        domain = f'{self._create_sequence(10)}/'
        _ = self.client.post(
            http_protocol=protocol,
            domain=domain,
            url_parameters=self.url_parameters,
            file_data=self.file_data,
            cookies=self.cookies,
            headers=self.headers
        )

        expected_request = self._request_with_parameters('POST', domain, protocol, True)
        actual_request = self.client.last_request

        self.assertEqual(actual_request, expected_request)

    def test_put_without_parameters(self):
        protocol = 'HTTP/1.2'
        domain = f'{self._create_sequence(10)}/'
        _ = self.client.put(http_protocol=protocol, domain=domain)

        expected = (
            f'PUT {domain} {protocol}\r\n'
            f'Host: {self.client.host}\r\n'
            '\r\n\r\n'
        )
        actual_request = self.client.last_request

        self.assertEqual(actual_request, expected)

    def test_put_with_parameters(self):
        protocol = 'HTTP/1.2'
        domain = f'{self._create_sequence(10)}/'
        _ = self.client.put(
            http_protocol=protocol,
            domain=domain,
            file_data=self.file_data,
            cookies=self.cookies,
            headers=self.headers
        )

        expected_request = self._requests_with_host('PUT', domain, protocol, self.client.host)
        actual_request = self.client.last_request

        self.assertEqual(actual_request, expected_request)

    def test_delete_without_parameters(self):
        protocol = 'HTTP/1.2'
        domain = f'{self._create_sequence(10)}/'
        _ = self.client.delete(http_protocol=protocol, domain=domain)

        expected = (
            f'DELETE {domain} {protocol}\r\n'
            f'Host: {self.client.host}\r\n'
            '\r\n\r\n'
        )
        actual_request = self.client.last_request

        self.assertEqual(actual_request, expected)

    def test_delete_with_parameters(self):
        protocol = 'HTTP/1.2'
        domain = f'{self._create_sequence(10)}/'
        _ = self.client.delete(
            http_protocol=protocol,
            domain=domain,
            file_data=self.file_data,
            cookies=self.cookies,
            headers=self.headers
        )

        expected_request = self._requests_with_host('DELETE', domain, protocol, self.client.host)
        actual_request = self.client.last_request

        self.assertEqual(actual_request, expected_request)

    def _request_with_parameters(self, method: str, domain: str, protocol: str, url_required: bool):
        file_keys = list(self.file_data.keys())
        file_values = list(self.file_data.values())
        headers_keys = list(self.headers.keys())
        headers_values = list(self.headers.values())

        expected_domain = domain
        if url_required:
            expected_domain = domain + f'?{self.client._join_dict(self.url_parameters, "=", "&")}'

        expected_request = (
            f'{method} {expected_domain} {protocol}\r\n'
            f"{headers_keys[0]}: {headers_values[0]}\r\n"
            f"{headers_keys[1]}: {headers_values[1]}\r\n"
            f"{headers_keys[2]}: {headers_values[2]}\r\n"
            f"Cookie: {HttpClient._join_dict(self.cookies, '=', '; ')}\r\n\r\n"
            f"--{HttpClient.BLOCK_BOUNDARY}\r\n"
            f'Content-Disposition: form-data; name="{file_keys[0]}"; filename="{file_keys[0]}"\r\n'
            '\r\n'
            f'{file_values[0]}\r\n'
            f"--{HttpClient.BLOCK_BOUNDARY}\r\n"
            f'Content-Disposition: form-data; name="{file_keys[1]}"; filename="{file_keys[1]}"\r\n'
            '\r\n'
            f'{file_values[1]}\r\n'
            f"--{HttpClient.BLOCK_BOUNDARY}\r\n"
            f'Content-Disposition: form-data; name="{file_keys[2]}"; filename="{file_keys[2]}"\r\n'
            '\r\n'
            f'{file_values[2]}\r\n'
            f"--{HttpClient.BLOCK_BOUNDARY}\r\n"
            f'Content-Disposition: form-data; name="{file_keys[3]}"; filename="{file_keys[3]}"\r\n'
            '\r\n'
            f'{file_values[3]}\r\n'
            f"--{HttpClient.BLOCK_BOUNDARY}--\r\n"
        )

        return expected_request

    def test_parser_full(self):
        url = 'https://someurl.com/with/query_string?i=main&mode=front&sid=12ab&enc=+Hello'
        expected_queries = {
            "i": "main",
            "mode": "front",
            "sid": "12ab",
            "enc": "+Hello"
        }
        parser = Parser(url)
        proto, host, path, queries = parser.parse()

        self.assertEqual(proto, Protocol.HTTPS)
        self.assertEqual(host, "someurl.com")
        self.assertEqual(path, "/with/query_string")
        self.assertEqual(queries, expected_queries)

    def test_parser_without_queries(self):
        url = 'https://someurl.com/with/query_string'
        parser = Parser(url)
        proto, host, path, queries = parser.parse()

        self.assertEqual(proto, Protocol.HTTPS)
        self.assertEqual(host, "someurl.com")
        self.assertEqual(path, "/with/query_string")
        self.assertEqual(queries, dict())

    def _requests_with_host(self, method: str, domain: str, protocol: str, host: str):
        file_keys = list(self.file_data.keys())
        file_values = list(self.file_data.values())
        headers_keys = list(self.headers.keys())
        headers_values = list(self.headers.values())

        expected_domain = domain
        expected_request = (
            f'{method} {expected_domain} {protocol}\r\n'
            f'Host: {host}\r\n'
            f"{headers_keys[0]}: {headers_values[0]}\r\n"
            f"{headers_keys[1]}: {headers_values[1]}\r\n"
            f"{headers_keys[2]}: {headers_values[2]}\r\n"
            f"Cookie: {HttpClient._join_dict(self.cookies, '=', '; ')}\r\n\r\n"
            f"--{HttpClient.BLOCK_BOUNDARY}\r\n"
            f'Content-Disposition: form-data; name="{file_keys[0]}"; filename="{file_keys[0]}"\r\n'
            '\r\n'
            f'{file_values[0]}\r\n'
            f"--{HttpClient.BLOCK_BOUNDARY}\r\n"
            f'Content-Disposition: form-data; name="{file_keys[1]}"; filename="{file_keys[1]}"\r\n'
            '\r\n'
            f'{file_values[1]}\r\n'
            f"--{HttpClient.BLOCK_BOUNDARY}\r\n"
            f'Content-Disposition: form-data; name="{file_keys[2]}"; filename="{file_keys[2]}"\r\n'
            '\r\n'
            f'{file_values[2]}\r\n'
            f"--{HttpClient.BLOCK_BOUNDARY}\r\n"
            f'Content-Disposition: form-data; name="{file_keys[3]}"; filename="{file_keys[3]}"\r\n'
            '\r\n'
            f'{file_values[3]}\r\n'
            f"--{HttpClient.BLOCK_BOUNDARY}--\r\n"
        )

        return expected_request

