


import tempfile
from typing import BinaryIO
from azext_confcom.lib.serialization import policy_deserialize, policy_serialize
from azext_confcom.lib.policy import Policy, Container


def policy_containers_add(policy_file: BinaryIO, container) -> str:

    policy = None
    if policy_file.name == "<stdin>":
        with tempfile.NamedTemporaryFile(delete=True) as temp_policy_file:
            temp_policy_file.write(policy_file.read())
            temp_policy_file.flush()
            policy = policy_deserialize(temp_policy_file.name)
    else:
        policy = policy_deserialize(policy_file.name)


    if not isinstance(container, list):
        container = [container]

    policy.containers.extend(Container(**c) for c in container)
    return policy_serialize(policy)


if __name__ == "__main__":
    print(policy_containers_add())