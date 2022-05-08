import os, sys


# # This assumes we're running from the <root>/bin folder
root_dir = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, root_dir)

from barbarian.server import run_server


if __name__ == "__main__":
    run_server()
