
from dataclasses import asdict
from typing import Optional
from azext_confcom import os_util, config
from azext_confcom.lib.arm_to_aci_policy_spec import AciFragmentSpec, arm_to_aci_policy_spec


def _omit_none_dict_factory(items):
    """Dict factory for dataclasses.asdict that drops None values."""
    return {key: value for key, value in items if (value is not None)}


def parse_aci_arm(
    arm_template_path: str,
    arm_template_parameters_path: Optional[str],
    debug_mode: bool,
    exclude_default_fragments: bool,
    infrastructure_svn: Optional[str],
    disable_stdio: bool,
    approve_wildcards: bool,
) -> list[dict[str, str]]:

    with open(arm_template_path, 'r') as f:
        arm_template = os_util.load_json_from_str(f.read())

    arm_template_parameters = {}
    if arm_template_parameters_path is not None:
        with open(arm_template_parameters_path, 'r') as f:
            arm_template_parameters = os_util.load_json_from_str(f.read())

    aci_policy_specs = list(arm_to_aci_policy_spec(
        arm_template=arm_template,
        arm_template_parameters=arm_template_parameters,
        include_infrastructure_fragment=not exclude_default_fragments,
        infrastructure_fragment_min_svn=infrastructure_svn,
        debug_mode=debug_mode,
        allow_stdio_access=not disable_stdio,
        approve_wildcards=approve_wildcards,
    ))

    return [
        asdict(spec, dict_factory=_omit_none_dict_factory)
        for spec in aci_policy_specs
    ]