# fixed/events.py — shared, stable, depends on nothing: the in-process event bus.
_handlers = []


def subscribe(handler):
    _handlers.append(handler)


def publish(event):
    return [handler(event) for handler in _handlers]
