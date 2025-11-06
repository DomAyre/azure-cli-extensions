
import json
from typing import Optional


def fragments_aci() -> str:
    return json.dumps({
        "feed": "mcr.microsoft.com/aci/aci-cc-infra-fragment",
        "includes": [
            "containers",
            "fragments"
        ],
        "issuer": "did:x509:0:sha256:I__iuL25oXEVFdTP_aBLx_eT1RPHbCQ_ECBQfYZpt9s::eku:1.3.6.1.4.1.311.76.59.1.3",
        "minimum_svn": "4"
    })