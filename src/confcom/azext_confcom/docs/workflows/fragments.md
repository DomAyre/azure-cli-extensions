# Fragments

## Why

A common use case of confidential containers is to securely release sensitive information such as keys to a trusted workload.

This workload attests itself using, among other things, the security policy which constrains it's behaviour. The source of the sensitive information will be configured to trust specifically that attestation.

This creates a servicing question, if we want to update our container images, this will result in a different security policy, which requires updating the key release policy.

A solution to this question is to move your container definition to a fragment, where the policy just says "I trust the fragment signed by this issuer" and the fragment itself can change without needing to change the policy.

## How

This process can be scaled to n workload containers, for brevity, the example will feature one.

1. Build your workload container image and push it to a OCI compliant registry.

```
docker build -t registry.io/repository:tag .
docker push registry.io/repository:tag
```

2. Define any extra policy that should constrain the final workload. This is part of a final rego container definition and brings in knowledge about the eventual deployment

`deployment_info.inc.rego`
```
{
    env_rules: [
        {
            "key": "ENV1",
            "key_strategy": "string",
            "value": "VAL1",
            "value_strategy": "string",
        }
    ]
}
```

3. Generate a container definition from the image and the extra fields
```
az confcom containers from_image registry.io/repository:tag > image.inc.rego
az confcom containers merge image.inc.rego deployment.inc.rego > container.inc.rego
```

4. Generate a fragment
```
az confcom acifragmentgen \
    --namespace "fragment_name" \
    --svn "1" \
    --with-containers container.inc.rego \
    --outraw \
    > fragment.rego
```

5. Sign the fragment, this is typically done in something like a pipeline so this isn't covered by the tooling. For the next setps, lets say the output of this is `fragment.rego.cose`

6. Attach the signed fragment to the image
```
az confcom fragment attach fragment.rego.cose \
    --manifest-tag registry.io/repository:tag
```

7. At deployment time, generate a reference to the fragment based on the deployment to use in the main policy
```
az confcom fragment reference from_image registry.io/repository:tag \
    > fragment_ref.inc.rego
```

8. Create the main policy with the fragment
```
az confcom acipolicygen \
    --with-fragments fragment_ref.inc.rego \
    --outraw \
    > policy.rego
```

9. Insert the base64 encoded `policy.rego` into the deployment template and deploy

## Next Steps

- If you need to include parameters in your fragments to specialize it's rules, refer to the [Specialized Fragments](azext_confcom/docs/workflows/specialized_fragments.md) workflow.