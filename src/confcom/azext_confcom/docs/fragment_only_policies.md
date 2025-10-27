# Creating a fragment only policy

## Step 1 - Generate a fragment

This command can be run with any of the same inputs as acipolicygen

```
az confcom acifragmentgen \
    --image myregistry.azurecr.io/my/repo:mytag \
    --svn "1" \
    --feed "my-fragment-1-feed" \
    --namespace "my-fragment-1"
```

## Step 2 - Sign the fragment

This is typically done through some custom pipeline

## Step 3 - Upload the fragment

Fragments can either be attached to an image, or uploaded as a "standalone" fragment

```
oras attach \
    myregistry.azurecr.io/my/repo:mytag \
    my-fragment-1.rego.cose \
    --artifact-type application/x-ms-ccepolicy-frag
```

## Step 4 - Generate the fragment import statement

Fragments can either be attached to an image, or uploaded as a "standalone" fragment

```
az confcom acifragmentgen \
    --fragment-path my-fragment-1.rego.cose \
    --generate-import \
    --minimum-svn "1" > import-my-fragment-1.json
```

---

Repeat steps 1-4 for all images you will include in your final policy.

## Step 4 - Generate the final security policy

Generate the input json which includes the fragments from the n import statements

```
az confcom acipolicygen \
    -i <(\
        jq -s '{fragments: map(.fragments) | add}' \
            import-my-fragment-1.json \
            import-my-fragment-2.json \
    )
```

