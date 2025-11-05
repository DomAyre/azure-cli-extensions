import os
import subprocess
import docker


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

def get_image_config(image: str) -> dict:

    client = docker.from_env()
    raw_image = client.images.get(image)
    image_config = raw_image.attrs.get("Config")

    config = {}

    if image_config.get("Cmd") or image_config.get("Entrypoint"):
        config["command"] = (
            image_config.get("Entrypoint") or [] +
            image_config.get("Cmd") or []
        )

    if image_config.get("Env"):
        config["env_rules"] = [{
            "pattern": p,
            "strategy": "string",
            "required": False,
        } for p in image_config.get("Env")]

    if image_config.get("WorkingDir"):
        config["working_dir"] = image_config.get("WorkingDir")

    return config
