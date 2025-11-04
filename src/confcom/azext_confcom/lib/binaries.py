
import os


def get_binaries_dir():
    binaries_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "bin")
    if not os.path.exists(binaries_dir):
        os.makedirs(binaries_dir)
    return binaries_dir

