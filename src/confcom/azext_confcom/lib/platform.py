ACI_MOUNTS = [
    {
        "destination": "/etc/resolv.conf",
        "options": [
            "rbind",
            "rshared",
            "rw"
        ],
        "source": "sandbox:///tmp/atlas/resolvconf/.+",
        "type": "bind"
    }
]

# VN2_MOUNTS = [
#     {
#         "destination": "/etc/resolv.conf",
#         "options": [
#             "rbind",
#             "rshared",
#             "rw"
#         ],
#         "source": "sandbox:///tmp/atlas/emptydir/.+",
#         "type": "bind"
#     }
# ]