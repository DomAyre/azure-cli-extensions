import os
import subprocess


def get_image_layers(image: str) -> list[str]:

    binary_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "bin", "dmverity-vhd")

    result = subprocess.run(
        [binary_path, "-d", "roothash", "-i", image],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
        text=True,
    )

    return [line.split("hash: ")[-1] for line in result.stdout.splitlines()]