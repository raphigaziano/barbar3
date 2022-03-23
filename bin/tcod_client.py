import os, sys
import argparse


if __name__ == '__main__':
    root_dir = os.path.dirname(os.path.dirname(__file__))
    sys.path.insert(0, root_dir)

    from barbarian.game import Game as BarbarGame
    from client_tcod.client import BarbarClient
    from client_tcod.nw import TCPClient, DummyTCPClient

    DEFAULT_HOST, DEFAULT_PORT = "localhost", 9999

    parser = argparse.ArgumentParser(conflict_handler='resolve')
    parser.add_argument('-s', '--seed', help='Random seed')

    network_group = parser.add_argument_group('Natworking')
    network_group.add_argument(
        '-n', '--networked', action='store_true', help='Play over network')
    network_group.add_argument(
        '-h', '--host', default=DEFAULT_HOST, help='Server host')
    network_group.add_argument(
        '-p', '--port', type=int, default=DEFAULT_PORT, help='Server port')

    args = parser.parse_args()

    if args.networked:
        print(args.host, args.port)
        connection = TCPClient(args.host, args.port)
    else:
        connection = DummyTCPClient(game=BarbarGame())

    client = BarbarClient()
    sys.exit(client.start(connection, args.seed))
