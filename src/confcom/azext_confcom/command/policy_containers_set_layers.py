


import tempfile
from typing import BinaryIO, Optional
from azext_confcom.lib.serialization import policy_deserialize, policy_serialize
from azext_confcom.lib.images import get_image_layers


def policy_containers_set_layers(
    policy_file: BinaryIO,
    container_id: str,
    image: Optional[str],
    in_place: bool,
) -> str:

    policy = None
    if policy_file.name == "<stdin>":
        assert not in_place
        with tempfile.NamedTemporaryFile(delete=True) as temp_policy_file:
            temp_policy_file.write(policy_file.read())
            temp_policy_file.flush()
            policy = policy_deserialize(temp_policy_file.name)
    else:
        policy = policy_deserialize(policy_file.name)

    container = next(c for c in policy.containers if c.id == container_id)
    container.layers = get_image_layers(image or container_id)
    serialized_policy = policy_serialize(policy)

    if in_place:
        with open(policy_file.name, "w") as f:
            f.write(serialized_policy)

    return serialized_policy
