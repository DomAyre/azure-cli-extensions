# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
import re

from azure.cli.command_modules.resource.custom import (
    _find_missing_parameters,
    _prepare_deployment_properties_unmodified,
)
from azure.cli.core.azclierror import CLIError
from azure.cli.core.profiles import ResourceType

from azext_confcom.lib.policy import Container
from azext_confcom.lib.images import get_image_config, get_image_layers
from azext_confcom.lib.platform import ACI_MOUNTS


class _ResourceDeploymentCommandAdapter:
    """Ensure required resource type defaults are present when reusing resource module helpers."""

    def __init__(self, cmd):
        self._cmd = cmd
        self.cli_ctx = cmd.cli_ctx

    def get_models(self, *attr_args, **kwargs):
        kwargs.setdefault('resource_type', ResourceType.MGMT_RESOURCE_DEPLOYMENTS)
        return self._cmd.get_models(*attr_args, **kwargs)

    def __getattr__(self, name):
        return getattr(self._cmd, name)


def get_parameters(
    arm_template: dict,
    arm_template_parameters: dict,
) -> dict:

    return {
        parameter_key: (
            arm_template_parameters.get(parameter_key, {}).get("value")
            or arm_template.get("parameters", {}).get(parameter_key, {}).get("value")
            or arm_template.get("parameters", {}).get(parameter_key, {}).get("defaultValue")
        )
        for parameter_key in arm_template.get("parameters", {}).keys()
    }


def eval_parameters(
    arm_template: dict,
    arm_template_parameters: dict,
) -> dict:

    parameters = get_parameters(arm_template, arm_template_parameters)
    return json.loads(re.compile(r"\[parameters\(\s*'([^']+)'\s*\)\]").sub(
        lambda match: json.dumps(parameters.get(match.group(1)) or match.group(0))[1:-1],
        json.dumps(arm_template),
    ))


def eval_variables(
    arm_template: dict,
    arm_template_parameters: dict,
) -> dict:

    variables = arm_template.get("variables", {})
    return json.loads(re.compile(r"\[variables\(\s*'([^']+)'\s*\)\]").sub(
        lambda match: json.dumps(variables.get(match.group(1), match.group(0)))[1:-1],
        json.dumps(arm_template),
    ))


EVAL_FUNCS = [
    eval_parameters,
    eval_variables,
]


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
            } for env in properties.get("environmentVariables")]
        ),
        "mounts": ACI_MOUNTS,
    }


def containers_from_aci(
    az_cli_command,
    template: str,
    parameters: dict,
    group_index: int
) -> None:
    properties = _prepare_deployment_properties_unmodified(
        cmd=_ResourceDeploymentCommandAdapter(az_cli_command),
        deployment_scope='resourceGroup',
        template_file=template,
        parameters=parameters,
        no_prompt=True,
    )
    template = json.loads(properties.template)
    parameters = properties.parameters or {}

    for eval_func in EVAL_FUNCS:
        template = eval_func(template, parameters)

    supported_resources = [r for r in template.get("resources", []) if r.get("type") in {
        "Microsoft.ContainerInstance/containerGroups",
        "Microsoft.ContainerInstance/containerGroupProfiles",
    }]

    container_group = supported_resources[group_index]

    return json.dumps([
        aci_container_to_policy(container)
        for container in container_group.get("properties", {}).get("containers", [])
    ])
