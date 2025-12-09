# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import copy
import json
import re
import pytest

from contextlib import redirect_stdout
from deepdiff import DeepDiff
from io import BytesIO, StringIO

from azext_confcom.command.containers_merge import containers_merge
from azext_confcom.lib.policy import (
    Container,
    ContainerCapabilities,
    Policy,
)
from azext_confcom.lib.serialization import policy_serialize


def build_base_container() -> dict:
    base_policy = Policy(
        containers=[
            Container(
                capabilities=ContainerCapabilities(
                    bounding=["CAP_AUDIT_WRITE"],
                    effective=["CAP_AUDIT_WRITE"],
                    permitted=["CAP_AUDIT_WRITE"],
                ),
                command=["/hello"],
                id="confcom_test_minimal",
                layers=["base-layer-sha"],
                name="confcom_test_minimal",
            )
        ]
    )

    policy_rego = policy_serialize(base_policy)
    containers_match = re.search(r"containers := (\[.*\])\n\nallow_", policy_rego, re.DOTALL)
    assert containers_match is not None
    containers_json = containers_match.group(1)
    return json.loads(containers_json)[0]


BASE_CONTAINER = build_base_container()


MERGE_TEST_CASES = [
    pytest.param(
        {"name": "custom_name"},
        {
            "values_changed": {
                "root['name']": {
                    "new_value": "custom_name",
                    "old_value": "confcom_test_minimal",
                }
            }
        },
        id="override-name",
    ),
    pytest.param(
        {"command": ["/override"]},
        {
            "values_changed": {
                "root['command'][0]": {
                    "new_value": "/override",
                    "old_value": "/hello",
                }
            }
        },
        id="override-command",
    ),
    pytest.param(
        {
            "env_rules": [
                {"pattern": "FOO=bar", "strategy": "string", "required": True},
            ]
        },
        {
            "iterable_item_added": {
                "root['env_rules'][0]": {
                    "pattern": "FOO=bar",
                    "strategy": "string",
                    "required": True,
                }
            }
        },
        id="append-env-rules",
    ),
    pytest.param(
        {
            "mounts": [
                {
                    "destination": "/data",
                    "options": ["ro"],
                    "source": "sandbox:///tmp/data",
                    "type": "bind",
                }
            ]
        },
        {
            "iterable_item_added": {
                "root['mounts'][0]": {
                    "destination": "/data",
                    "options": ["ro"],
                    "source": "sandbox:///tmp/data",
                    "type": "bind",
                }
            }
        },
        id="append-mounts",
    ),
    pytest.param(
        {"allow_elevated": True},
        {
            "values_changed": {
                "root['allow_elevated']": {
                    "new_value": True,
                    "old_value": False,
                }
            }
        },
        id="override-allow-elevated",
    ),
    pytest.param(
        {
            "capabilities": {
                "ambient": [],
                "bounding": [],
                "effective": [],
                "inheritable": [],
                "permitted": [],
            }
        },
        {
            "iterable_item_removed": {
                "root['capabilities']['bounding'][0]": "CAP_AUDIT_WRITE",
                "root['capabilities']['effective'][0]": "CAP_AUDIT_WRITE",
                "root['capabilities']['permitted'][0]": "CAP_AUDIT_WRITE",
            }
        },
        id="override-capabilities",
    ),
    pytest.param(
        {
            "exec_processes": [
                {
                    "command": ["/healthcheck"],
                    "signals": ["SIGUSR1"],
                }
            ]
        },
        {
            "iterable_item_added": {
                "root['exec_processes'][0]": {
                    "command": ["/healthcheck"],
                    "signals": ["SIGUSR1"],
                }
            }
        },
        id="append-exec-processes",
    ),
    pytest.param(
        {"signals": ["SIGHUP"]},
        {
            "iterable_item_added": {
                "root['signals'][0]": "SIGHUP",
            }
        },
        id="append-signals",
    ),
    pytest.param(
        {
            "user": {
                "group_idnames": [{"pattern": "1234", "strategy": "id", "required": False}],
                "umask": "0777",
                "user_idname": {"pattern": "1234", "strategy": "id", "required": False},
            }
        },
        {
            "values_changed": {
                "root['user']['group_idnames'][0]['pattern']": {
                    "new_value": "1234",
                    "old_value": "",
                },
                "root['user']['group_idnames'][0]['strategy']": {
                    "new_value": "id",
                    "old_value": "any",
                },
                "root['user']['umask']": {
                    "new_value": "0777",
                    "old_value": "0022",
                },
                "root['user']['user_idname']['pattern']": {
                    "new_value": "1234",
                    "old_value": "",
                },
                "root['user']['user_idname']['strategy']": {
                    "new_value": "id",
                    "old_value": "any",
                },
            }
        },
        id="override-user",
    ),
    pytest.param(
        {"layers": ["override-layer-sha"]},
        {
            "values_changed": {
                "root['layers'][0]": {
                    "new_value": "override-layer-sha",
                    "old_value": "base-layer-sha",
                }
            }
        },
        id="override-layers",
    ),
    pytest.param(
        {"working_dir": "/workspace"},
        {
            "values_changed": {
                "root['working_dir']": {
                    "new_value": "/workspace",
                    "old_value": "/",
                }
            }
        },
        id="override-working-dir",
    ),
]


@pytest.mark.parametrize("override_container, expected_diff", MERGE_TEST_CASES)
def test_containers_merge(override_container: dict, expected_diff: dict):
    base_container = copy.deepcopy(BASE_CONTAINER)
    base_buffer = BytesIO(json.dumps(base_container).encode("utf-8"))
    override_buffer = BytesIO(json.dumps(override_container).encode("utf-8"))

    buffer = StringIO()
    with redirect_stdout(buffer):
        containers_merge(base_buffer, override_buffer)

    merged_container = json.loads(buffer.getvalue())

    diff = DeepDiff(BASE_CONTAINER, merged_container, ignore_order=True)

    assert diff == expected_diff
