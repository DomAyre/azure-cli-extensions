# Specialized Fragments

This workflow assumes knowledge of the [Fragments](azext_confcom/docs/workflows/fragment_only_policies.md) workflow.

## Why

Many workloads have some configuration which defines it's behaviour.

If you're using a fragment which is defined at image build time, but the container is configured at deployment time, the fragment specialization allows the policy to enforce this configuration.

## How

This process is mostly the same as the [Fragments](azext_confcom/docs/workflows/fragment_only_policies.md) workflow, there are two differences:

1. In your partial container definition, include some usage of parameters, e.g.

`deployment_info.inc.rego`
```
{
    env_rules: [
        {
            "key": "ENV1",
            "key_strategy": "string",
            "value": parameter("env1_value"),
            "value_strategy": "string",
        }
    ]
}
```
- When generating the fragment, the tool sees the usage of parameters and adds declarations for each one

```
parameters := {
    "env1_value": {}
}
```

2. When generating the reference to the fragment, you specify the values of the parameters
```
az confcom fragment reference from_image registry.io/repository:tag \
    --parameters "env1_value=custom_env_value" \
    > fragment_ref.inc.rego
```

