# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def load_command_table(self, _):

    with self.command_group("confcom") as g:
        g.custom_command("acipolicygen", "acipolicygen_confcom")
        g.custom_command("acifragmentgen", "acifragmentgen_confcom")
        g.custom_command("katapolicygen", "katapolicygen_confcom")

    with self.command_group("confcom policy") as g:
        g.custom_command("create", "policy_create")

    with self.command_group("confcom policy containers") as g:
        g.custom_command("add", "policy_containers_add")

    with self.command_group("confcom policy containers set") as g:
        g.custom_command("layers", "policy_containers_set_layers")

    with self.command_group("confcom policy fragments") as g:
        g.custom_command("add", "policy_fragments_add")

    with self.command_group("confcom containers") as g:
        g.custom_command("pause", "containers_pause")
        g.custom_command("from_image", "containers_from_image")
        g.custom_command("from_aci", "containers_from_aci")

    with self.command_group("confcom fragments") as g:
        g.custom_command("aci", "fragments_aci")

    with self.command_group("confcom aci policy") as g:
        g.custom_command("insert", "aci_policy_insert")

    with self.command_group("confcom"):
        pass
