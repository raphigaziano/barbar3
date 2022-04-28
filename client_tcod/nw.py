"""
Networking

"""
import socket
import json
import gzip
import uuid
from types import SimpleNamespace


class Request(dict):

    session_key = str(uuid.uuid1())

    @classmethod
    def start(cls, config=None):
        data = config or {}
        return cls(session_key=cls.session_key, type='START', data=data)

    @classmethod
    def action(cls, action_type, data=None):
        d = {'type': action_type, 'data': data or {}}
        return cls(session_key=cls.session_key, type='ACT', data=d)

    @classmethod
    def prompt_response(cls, data):
        return cls(session_key=cls.session_key, type='PROMPT', data=data or {})

    @classmethod
    def get(cls): pass # stub

    @classmethod
    def set(cls, key, val=None):
        d = {'key': key, 'val': val}
        return cls(session_key=cls.session_key, type='SET', data=d)


class Response(SimpleNamespace):

    def __init__(self, *args, **kwargs):
        state = kwargs.pop('gamestate', None)
        self.gs = SimpleNamespace(**state) if state else None
        super().__init__(*args, **kwargs)


class TCPClient:

    def __init__(self, host, port):
        self.host, self.port = host, port
        self.response = None

    def send(self, request):
        request_data = json.dumps(request)

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((self.host, self.port))
            sock.sendall(bytes(request_data, 'utf-8'))

            received = b''
            while True:
                chunk = sock.recv(1024)
                if not chunk:
                    break
                received += chunk

            rdata = json.loads(
                str(gzip.decompress(received), 'utf-8')
            )
            self.response = Response(**rdata)

        return self.response

    def close(self):
        pass
        # self.sock.close()


class DummyTCPClient:
    """
    Mimic TCP connection by sending requests direcly to a game instance.

    """
    def __init__(self, game):
        self.__game = game
        self.response = None

    def send(self, input_):
        raw = self.__game.receive_request(input_)
        self.response = Response(**raw)
        return self.response

    def close(self):
        pass
