# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import copy
import json
from contextlib import redirect_stdout
from io import StringIO
from io import BytesIO
from pathlib import Path

import pytest
from deepdiff import DeepDiff

from azext_confcom.command.containers_merge import containers_merge


TEST_DIR = Path(__file__).parent
CONFCOM_DIR = TEST_DIR.parent.parent.parent
BASE_CONTAINER_PATH = CONFCOM_DIR / "samples" / "images" / "minimal" / "aci_container.inc.rego"

with BASE_CONTAINER_PATH.open("r", encoding="utf-8") as handle:
    BASE_CONTAINER = json.load(handle)


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
                "root['env_rules'][1]": {
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
                "root['mounts'][1]": {
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
def test_containers_merge_parametrized(override_container: dict, expected_diff: dict):
    base_container = copy.deepcopy(BASE_CONTAINER)
    base_buffer = BytesIO(json.dumps(base_container).encode("utf-8"))
    override_buffer = BytesIO(json.dumps(override_container).encode("utf-8"))

    buffer = StringIO()
    with redirect_stdout(buffer):
        containers_merge(base_buffer, override_buffer)

    merged_container = json.loads(buffer.getvalue())

    diff = DeepDiff(BASE_CONTAINER, merged_container, ignore_order=True)

    assert diff == expected_diff
