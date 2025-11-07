


import tempfile
from typing import BinaryIO, Optional
from azext_confcom.lib.serialization import policy_deserialize, policy_serialize
from azext_confcom.lib.policy import FragmentReference, Policy, Container


def policy_fragments_add(
    policy_file: BinaryIO,
    fragment_json: dict,
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

    fragment = FragmentReference(**fragment_json)

    policy.fragments.append(fragment)
    serialized_policy = policy_serialize(policy)

    if in_place:
        with open(policy_file.name, "w") as f:
            f.write(serialized_policy)

    return serialized_policy
