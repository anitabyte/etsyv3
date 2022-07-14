from enum import Enum


def todict(obj, classkey=None, nullable=[]):
    if isinstance(obj, dict):
        data = {}
        for (k, v) in obj.items():
            data[k] = todict(v, classkey)
        return data
    elif Enum in obj.__class__.__mro__:
        return todict(obj.value)
    elif hasattr(obj, "_ast"):
        return todict(obj._ast())
    elif hasattr(obj, "__iter__") and not isinstance(obj, str):
        return [todict(v, classkey) for v in obj]
    elif hasattr(obj, "__dict__"):
        data = dict(
            [
                (key, todict(value, classkey))
                if key not in nullable and value not in [[], "" or 0]
                else (key, None)
                for key, value in obj.__dict__.items()
                if not callable(value) and not key.startswith("_") and value is not None
            ]
        )
        if classkey is not None and hasattr(obj, "__class__"):
            data[classkey] = obj.__class__.__name__
        return data
    else:
        return obj
