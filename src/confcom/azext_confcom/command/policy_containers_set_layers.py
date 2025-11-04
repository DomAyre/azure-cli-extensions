


import tempfile
from typing import BinaryIO, Optional
from azext_confcom.lib.serialization import policy_deserialize, policy_serialize
from azext_confcom.lib.policy import Policy, Container
from azext_confcom.rootfs_proxy import SecurityPolicyProxy


def policy_containers_set_layers(policy_file: BinaryIO, container_id: str, image: Optional[str]) -> str:

    policy = None
    if policy_file.name == "<stdin>":
        with tempfile.NamedTemporaryFile(delete=True) as temp_policy_file:
            temp_policy_file.write(policy_file.read())
            temp_policy_file.flush()
            policy = policy_deserialize(temp_policy_file.name)
    else:
        policy = policy_deserialize(policy_file.name)

    container = next(c for c in policy.containers if c.id == container_id)
    container.layers = SecurityPolicyProxy().get_policy_image_layers(*(image or container_id).split(":"))
    return policy_serialize(policy)
