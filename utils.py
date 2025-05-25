#used to automatically register classes in a registry: used for bossess
def register_state(registry, name=None):
    def wrapper(cls):
        key = name or cls.__name__.lower()
        if key in registry:
            raise ValueError(f"Duplicate state key '{key}' in registry")
        registry[key] = cls
        return cls
    return wrapper