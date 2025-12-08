# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json

from typing_extensions import BinaryIO

from azext_confcom.lib.containers import merge_containers


def containers_merge(
    dst_container: BinaryIO,
    src_container: BinaryIO,
) -> str:
    print(json.dumps(merge_containers(
        json.loads(dst_container.read().decode('utf-8')),
        json.loads(src_container.read().decode('utf-8')),
    )))
