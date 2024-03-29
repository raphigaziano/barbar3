import os, sys
import json
import gzip
import socket
import socketserver
import argparse

# This assumes we're running from the <root>/bin folder
root_dir = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, root_dir)

from barbarian.game import Game


class BarbarTCPHandler(socketserver.BaseRequestHandler):
    """
    The request handler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """
    def __init__(self, *args, **kwargs):
        self.game = None
        super().__init__(*args, **kwargs)

    def setup(self):
        print('--- setup ---')

    def handle(self):
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(1024).strip()
        data = json.loads(self.data)

        skey = data.pop('session_key')
        if skey not in self.server.sessions:
            print('Initializing a new game instance')
            self.server.sessions[skey] = Game()
        game = self.server.sessions[skey]

        print('Handling request for session {}'.format(skey))
        print("{} wrote:".format(self.client_address[0]))
        print(self.data)

        if self.server.profile:
            from pyinstrument import Profiler
            profiler = Profiler()
            profiler.start()
        game_response = game.receive_request(data)
        r = gzip.compress(bytes(json.dumps(game_response), 'utf-8'))
        if self.server.profile:
            profiler.stop()
            profiler.print()
        print('Response size:', len(r))

        self.request.sendall(r)

    def finish(self):
        print('--- finish ---')


class BarbarServer(socketserver.ThreadingTCPServer):

    allow_reuse_address = True

    def __init__(self, *args, **kwargs):
        self.profile = kwargs.pop('profile', False)
        super().__init__(*args, **kwargs)
        self.sessions = {}
        print('Listening on {}...'.format(self.server_address))


if __name__ == "__main__":

    DEFAULT_HOST, DEFAULT_PORT = "localhost", 9999

    parser = argparse.ArgumentParser(conflict_handler='resolve')
    parser.add_argument(
        '-h', '--host', default=DEFAULT_HOST, help='Server host')
    parser.add_argument(
        '-p', '--port', type=int, default=DEFAULT_PORT, help='Server port')
    parser.add_argument(
        '--profile', action='store_true', 
        help='profile each response (Requires pyinstrument)')

    args = parser.parse_args()
    host, port  = args.host, args.port

    # Create the server, binding to localhost on port 9999
    with BarbarServer(
        (host, port), BarbarTCPHandler, profile=args.profile
    ) as server:
        # Activate the server; this will keep running until you
        # interrupt the program with Ctrl-C
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
