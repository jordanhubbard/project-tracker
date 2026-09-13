"""Normalize equivalent REST envelopes without changing entity contents.

The product specification names fields and bounded collections, but does not
require a particular envelope key. Protocol JSON-RPC responses remain untouched.
"""


def entity_response(value):
    if not isinstance(value, dict) or "jsonrpc" in value or "error" in value:
        return value
    for key in ("repository", "task", "session", "peer"):
        if set(value) == {key} and isinstance(value[key], dict):
            return value[key]
    if "items" not in value:
        collections = [
            key
            for key in (
                "repositories",
                "tasks",
                "states",
                "sessions",
                "peers",
                "events",
            )
            if isinstance(value.get(key), list)
        ]
        if len(collections) == 1:
            return dict(value, items=value[collections[0]])
    return value
