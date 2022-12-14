import sys

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
    _parser = Parser(arguments.url)
    _proto, _host, _path, _queries = _parser.parse()

    method = Method[arguments.method.lower()]
    argument_data = [None, None, None]

    all_data = [arguments.headers, arguments.cookies, arguments.data]
    for i in range(len(all_data)):
        data = all_data[i]
        if data:
            if path.isfile(data):
                with open(data, 'r') as f:
                    argument_data[i] = f.read()
            else:
                argument_data[i] = data
    _formatted_data = list(map(data_to_dict, argument_data))
    _formatted_data.append(_queries)

    return _proto, _host, _path, method, _formatted_data


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="HTTP(S) client", formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(dest="url", help='Parse from exact url')
    parser.add_argument("-m", dest="method", required=True, help='HTTP(s) request method. E.g GET, POST, e.t.c')

    parser.add_argument("--headers", dest="headers", help='The path to the header file or raw string')
    parser.add_argument("--cookies", dest="cookies", help='The path to the cookie file or raw string')
    parser.add_argument("--fd", dest="data", help='The path to the file with the forms or raw string')
    parser.add_argument("-j", dest="json_location", help='The path where to save the request result')
    parser.add_argument("-t", dest="timeout", default=2.0, type=int, help='Request timeout in seconds')

    args = parser.parse_args()
    proto, host, path, method, request_data = parse_request(args)
    main(host, path, method, args.json_location, args.timeout, request_data, proto)

