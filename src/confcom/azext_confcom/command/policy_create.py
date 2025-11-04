


from azext_confcom.lib.serialization import policy_serialize
from azext_confcom.lib.policy import Policy


def policy_create() -> str:
    return policy_serialize(Policy())
