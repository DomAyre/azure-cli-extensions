


import tempfile
from typing import BinaryIO
from azext_confcom.lib.serialization import policy_deserialize, policy_serialize
from azext_confcom.lib.policy import Fragment, Policy, Container


def policy_fragments_add(policy_file: BinaryIO, fragment) -> str:

    policy = None
    if policy_file.name == "<stdin>":
        with tempfile.NamedTemporaryFile(delete=True) as temp_policy_file:
            temp_policy_file.write(policy_file.read())
            temp_policy_file.flush()
            policy = policy_deserialize(temp_policy_file.name)
    else:
        policy = policy_deserialize(policy_file.name)

    policy.fragments.append(Fragment(**fragment))
    return policy_serialize(policy)


if __name__ == "__main__":
    print(policy_fragments_add())