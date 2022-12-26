from http import Protocol


class Parser:
    def __init__(self, url: str):
        self.url = url
        self.proto = None
        self.address = None
        self.host = None
        self.path = '/'
        self.queries = dict()

    def parse(self) -> (Protocol, str, str, dict):
        _fragment_index = self.url.find("#")
        if _fragment_index != -1:
            self.url = self.url[:_fragment_index]

        proto_domain_sep = self.url.find("://")
        domain_query_sep = self.url.find("?")
        self.proto = Protocol.HTTPS if "https" in self.url[:proto_domain_sep + 1].lower() else Protocol.HTTP

        if domain_query_sep == -1:
            self.address = self.url[proto_domain_sep + 3:]
        else:
            self.address = self.url[proto_domain_sep + 3: domain_query_sep]

            pairs = self.url[domain_query_sep + 1:].split('&')

            for pair in pairs:
                name, value = pair.split('=')[0], pair.split('=')[1]
                self.queries[name] = value

        _host_path_sep = self.address.find('/')
        if _host_path_sep == -1:
            self.host = self.address
        else:
            self.host = self.address[:_host_path_sep]
            self.path = self.address[_host_path_sep:]

        return self.proto, self.host, self.path, self.queries


