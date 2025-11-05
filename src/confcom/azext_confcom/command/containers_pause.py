
import json


def containers_pause() -> str:
    return json.dumps({
        "command": ["/pause"],
        "layers": ["16b514057a06ad665f92c02863aca074fd5976c755d26bff16365299169e8415"],
        "name": "pause-container",
    })