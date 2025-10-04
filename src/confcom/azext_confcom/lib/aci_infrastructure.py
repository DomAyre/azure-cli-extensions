


from dataclasses import fields, is_dataclass, replace
from azext_confcom import config
from azext_confcom.lib.aci_policy_spec import AciContainerPropertyEnvVariable, AciContainerPropertyVolumeMounts, AciFragmentSpec


INFRASTRUCTURE_FRAGMENTS = [AciFragmentSpec(**frag) for frag in config.DEFAULT_REGO_FRAGMENTS]
OPENGCS_ENV_RULES = [AciContainerPropertyEnvVariable(**env_var) for env_var in config.OPENGCS_ENV_RULES]
FABRIC_ENV_RULES = [AciContainerPropertyEnvVariable(**env_var) for env_var in config.FABRIC_ENV_RULES]
MANAGED_IDENTITY_ENV_RULES = [AciContainerPropertyEnvVariable(**env_var) for env_var in config.MANAGED_IDENTITY_ENV_RULES]
ENABLE_RESTART_ENV_RULE = [AciContainerPropertyEnvVariable(**env_var) for env_var in config.ENABLE_RESTART_ENV_RULE]
DEFAULT_MOUNTS_USER = [AciContainerPropertyVolumeMounts(**mount) for mount in config.DEFAULT_MOUNTS_USER]


implicit_features = [
    *INFRASTRUCTURE_FRAGMENTS,
    *OPENGCS_ENV_RULES,
    *FABRIC_ENV_RULES,
    *MANAGED_IDENTITY_ENV_RULES,
    *ENABLE_RESTART_ENV_RULE,
    *DEFAULT_MOUNTS_USER,
]


def omit_implicit_features(obj):
    if obj is None:
        return None
    if is_dataclass(obj):
        return replace(obj, **{f.name: omit_implicit_features(getattr(obj, f.name)) for f in fields(obj)})
    if isinstance(obj, list):
        return [omit_implicit_features(x) for x in obj if x not in implicit_features]
    return obj