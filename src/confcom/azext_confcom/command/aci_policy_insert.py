


import tempfile
from typing import BinaryIO
from azext_confcom.lib.serialization import policy_deserialize, policy_serialize
from azext_confcom.lib.policy import Policy, Container
import re
import base64


def aci_policy_insert(
    policy_file: BinaryIO,
    template_path: str,
) -> str:

    policy = None
    if policy_file.name == "<stdin>":
        with tempfile.NamedTemporaryFile(delete=True) as temp_policy_file:
            temp_policy_file.write(policy_file.read())
            temp_policy_file.flush()
            policy = policy_deserialize(temp_policy_file.name)
    else:
        policy = policy_deserialize(policy_file.name)

    serialized_policy = policy_serialize(policy)

    # Read the template file
    with open(template_path, 'r') as template_file:
        template_content = template_file.read()

    # Base64 encode the serialized policy
    encoded_policy = base64.b64encode(serialized_policy.encode()).decode()

    # Replace the ccePolicy value with the encoded policy
    updated_content = re.sub(r'"ccePolicy":\s*"[^"]*"', f'"ccePolicy": "{encoded_policy}"', template_content)

    # Write the updated content back to the template file
    with open(template_path, 'w') as template_file:
        template_file.write(updated_content)
