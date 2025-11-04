
import json

from azext_confcom.lib.images import get_image_layers
from azext_confcom.rootfs_proxy import SecurityPolicyProxy


def container_from_image(image: str) -> str:
    return json.dumps({
        "id": image,
        "name": image,
        "layers": get_image_layers(image),
    })