
from dataclasses import asdict, fields
from typing import Optional
from azext_confcom import os_util
from azext_confcom.lib.aci_infrastructure import omit_implicit_features
from azext_confcom.lib.aci_policy_spec import POLICY_SPEC_CLASSES
from azext_confcom.lib.arm_to_aci_policy_spec import arm_to_aci_policy_spec


def omit_defaults_dict_factory(fields_dict) -> dict:

    result = {}

    for potential_class in POLICY_SPEC_CLASSES:
        try:
            instance = potential_class(**dict(fields_dict))
            for field in fields(instance):
                value = getattr(instance, field.name)
                if value not in (None, field.default, []):
                    result[field.name] = value
            break
        except TypeError:
            continue

    return result


def parse_aci_arm(
    arm_template_path: str,
    arm_template_parameters_path: Optional[str],
    debug_mode: bool,
    exclude_default_fragments: bool,
    infrastructure_svn: Optional[str],
    disable_stdio: bool,
    approve_wildcards: bool,
    policy_format: str,
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

    specs = []
    for spec in aci_policy_specs:
        if policy_format == "minimal":
            spec = omit_implicit_features(spec)
        specs.append(asdict(spec, dict_factory=omit_defaults_dict_factory))

    return specs
