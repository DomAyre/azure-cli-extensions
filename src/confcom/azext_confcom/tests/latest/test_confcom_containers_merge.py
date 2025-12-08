# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
from contextlib import redirect_stdout
from io import StringIO

from azext_confcom.command.containers_merge import containers_merge


def test_containers_merge_combines_definitions():
    first_container = {
        "id": "base",
        "env_rules": [{"command": "one"}],
        "exec_processes": [{"path": "/bin/base"}],
        "mounts": [{"path": "/mnt/base"}],
        "signals": [1],
        "entrypoint": ["/bin/base"],
    }
    second_container = {
        "name": "override",
        "env_rules": [{"command": "two"}],
        "exec_processes": [{"path": "/bin/override"}],
        "mounts": [{"path": "/mnt/override"}],
        "signals": [2],
        "entrypoint": ["/bin/override"],
    }

    expected_env_rules = first_container["env_rules"] + second_container["env_rules"]
    expected_exec_processes = first_container["exec_processes"] + second_container["exec_processes"]
    expected_mounts = first_container["mounts"] + second_container["mounts"]
    expected_signals = first_container["signals"] + second_container["signals"]

    buffer = StringIO()
    with redirect_stdout(buffer):
        containers_merge(first_container, second_container)

    merged_container = json.loads(buffer.getvalue())

    assert merged_container["id"] == "base"
    assert merged_container["name"] == "override"
    assert merged_container["env_rules"] == expected_env_rules
    assert merged_container["exec_processes"] == expected_exec_processes
    assert merged_container["mounts"] == expected_mounts
    assert merged_container["signals"] == expected_signals
    assert merged_container["entrypoint"] == ["/bin/override"]
