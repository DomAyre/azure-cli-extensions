# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json

from azext_confcom.lib.deployments import parse_deployment_template
from azext_confcom.lib.images import get_image_config, get_image_layers
from azext_confcom.lib.platform import ACI_MOUNTS


def aci_container_to_policy(
    arm_container: dict,
):
    properties = arm_container.get("properties", {})
    image = properties.get("image")
    image_config = get_image_config(image)

    return {
        "name": arm_container.get("name"),
        "id": image,
        "layers": get_image_layers(image),
        "command": (
            properties.get("command") or
            image_config.get("command")
        ),
        "env_rules": (
            image_config.get("env_rules") +
            [{
                "pattern": f"{env.get('name')}={env.get('value')}",
                "strategy": "string",
                "required": False,
            } for env in properties.get("environmentVariables", [])]
        ),
        "mounts": ACI_MOUNTS,
    }


def containers_from_aci(
    az_cli_command,
    template: str,
    parameters: dict,
    group_index: int
) -> None:

    template = parse_deployment_template(
        az_cli_command,
        template,
        parameters,
    )

    supported_resources = [r for r in template.get("resources", []) if r.get("type") in {
        "Microsoft.ContainerInstance/containerGroups",
        "Microsoft.ContainerInstance/containerGroupProfiles",
    }]

    container_group = supported_resources[group_index]

    return json.dumps([
        aci_container_to_policy(container)
        for container in container_group.get("properties", {}).get("containers", [])
    ])
