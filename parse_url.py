from http import Protocol


class Parser:
    def __init__(self, url: str):
        self.url = url
        self.proto = None
        self.domain = None
        self.queries = dict()

    def parse(self) -> (Protocol, str, dict):
        proto_domain_sep = self.url.find("://")
        domain_query_sep = self.url.find("?")
        self.proto = Protocol.HTTPS if "https" in self.url[:proto_domain_sep + 1].lower() else Protocol.HTTP

        if domain_query_sep == -1:
            self.domain = self.url[proto_domain_sep + 3:]
        else:
            self.domain = self.url[proto_domain_sep + 3: domain_query_sep]
            pairs = self.url[domain_query_sep + 1:].split('&')

            for pair in pairs:
                name, value = pair.split('=')[0], pair.split('=')[1]
                self.queries[name] = value

        return self.proto, self.domain, self.queries


