# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
import os
import pytest
from itertools import product
from deepdiff import DeepDiff

from azext_confcom.custom import parse_aci_arm


TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), ".."))
SAMPLES_ROOT = os.path.abspath(os.path.join(TEST_DIR, "..", "..", "..", "samples", "aci"))


ARGS = {
    "policy_spec.json": {},
    "policy_spec_debug.json": {"debug_mode": True},
    "policy_spec_exclude_default_fragment.json": {"exclude_default_fragments": True},
    "policy_spec_infrastructure_svn.json": {"infrastructure_svn": "99"},
    "policy_spec_disable_stdio.json": {"disable_stdio": True},
}


@pytest.mark.parametrize(
    "sample_directory,generated_policy_spec_path",
    product(os.listdir(SAMPLES_ROOT), ARGS.keys())
)
def test_parse_aci_arm(sample_directory, generated_policy_spec_path):

    for failing_sample_directory, failing_generated_policy_path in [
    ]:
        if (
            failing_sample_directory in (None, sample_directory)
            and failing_generated_policy_path in (None, generated_policy_spec_path)
        ):
            pytest.skip("Skipping test due to known issue")

    arm_template_path = os.path.join(SAMPLES_ROOT, sample_directory, "arm_template.json")
    parameters_path = os.path.join(SAMPLES_ROOT, sample_directory, "parameters.json")
    if not os.path.isfile(parameters_path):
        parameters_path = None
    flags = ARGS[generated_policy_spec_path]

    with open(os.path.join(SAMPLES_ROOT, sample_directory, generated_policy_spec_path), "r", encoding="utf-8") as f:
        expected_policy_spec = json.load(f)

    actual_policy_spec = parse_aci_arm(
        arm_template_path=arm_template_path,
        arm_template_parameters_path=parameters_path,
        debug_mode=flags.get("debug_mode", False),
        exclude_default_fragments=flags.get("exclude_default_fragments", False),
        infrastructure_svn=flags.get("infrastructure_svn", None),
        disable_stdio=flags.get("disable_stdio", False),
        approve_wildcards=False,
    )

    assert DeepDiff(actual_policy_spec, expected_policy_spec, ignore_order=True) == {}, (
        "Policy generation mismatch, actual output for "
        f"{os.path.join(sample_directory, generated_policy_spec_path)}:\n"
        f"{json.dumps(actual_policy_spec, indent=2)}"
    )
