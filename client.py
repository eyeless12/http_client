from http import HttpClient, Method, Protocol
import argparse
from os import path
from typing import Dict, List
from parse_url import Parser

import re


def main(server_host, domain, request_method, json_location, timeout, data, proto: Protocol):
    sender = HttpClient(server_host, timeout, protocol=proto)
    if request_method is Method.get:
        sender.get(url_parameters=data[3], file_data=data[2], cookies=data[1], headers=data[0], to_json=json_location, domain=domain)
    elif request_method is Method.post:
        sender.post(url_parameters=data[3], file_data=data[2], cookies=data[1], headers=data[0], to_json=json_location, domain=domain)
    elif request_method is Method.head:
        sender.head(url_parameters=data[3], file_data=data[2], cookies=data[1], headers=data[0], to_json=json_location, domain=domain)
    elif request_method is Method.put:
        sender.put(file_data=data[2], cookies=data[1], headers=data[0], to_json=json_location, domain=domain)
    elif request_method is Method.delete:
        sender.delete(file_data=data[2], cookies=data[1], headers=data[0], to_json=json_location, domain=domain)

    print(sender.response)
    print(sender.last_request)
    sender.close()


def data_to_dict(data: str) -> Dict[str, str]:
    if not data:
        return None
    split_data = data.split('\n')
    result = dict()
    for s in split_data:
        header_value = s.split(':')
        result[header_value[0].strip()] = header_value[1].strip()
    return result


def parse_request(arguments):
    _parsed = False
    _host = None
    _proto = None
    _domain = None
    _queries = None

    host = arguments.host
    method = Method[arguments.method.lower()]
    protocol = Protocol.HTTPS
    argument_data = [None, None, None, None]

    if arguments.protocol == "http":
        protocol = Protocol.HTTP
    else:
        protocol = Protocol.HTTPS

    if arguments.parse is not None:
        _parsed = True
        _parser = Parser(arguments.parse)
        _proto, _address, _queries = _parser.parse()

        _index = _address.find('/')
        if _index == -1:
            _host = _address
            _domain = '/'
        else:
            _host = _address[:_index]
            _domain = _address[_index:]

    all_data = [arguments.headers, arguments.cookies, arguments.data, arguments.url_parameters]
    for i in range(len(all_data)):
        data = all_data[i]
        if data:
            if path.isfile(data):
                with open(data, 'r') as f:
                    argument_data[i] = f.read()
            else:
                argument_data[i] = data

    if _parsed:
        data = list(map(data_to_dict, argument_data[-2::-1]))
        if _queries:
            data.append(_queries)
        else:
            data.append(None)

        return _proto, _host, _domain, method, data
    else:
        return protocol, host, '/',  method, list(map(data_to_dict, argument_data))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="HTTP(S) client", formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-a", dest="host", required=True, help='Host of the selected server')
    parser.add_argument("-m", dest="method", required=True, help='HTTP(s) request method. E.g GET, POST, e.t.c')
    parser.add_argument("--parse", dest="parse", help='Parse from exact url')
    parser.add_argument("--proto", dest="protocol", help="HTTPS by default, but you can run client on HTTP protocol")
    parser.add_argument("--headers", dest="headers", help='The path to the header file or raw string')
    parser.add_argument("--cookies", dest="cookies", help='The path to the cookie file or raw string')
    parser.add_argument("--fd", dest="data", help='The path to the file with the forms or raw string')
    parser.add_argument("--up", dest="url_parameters", help='The path to the file with url parameters or raw string')
    parser.add_argument("-j", dest="json_location", help='The path where to save the request result')
    parser.add_argument("-t", dest="timeout", default=2.0, type=int, help='Request timeout in seconds')
    args = parser.parse_args()
    proto, host, domain, method, request_data = parse_request(args)
    main(host, domain, method, args.json_location, args.timeout, request_data, proto)

