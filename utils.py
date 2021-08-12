
class Singleton(type):
    __instances = {}

    def __call__(cls, *args, **kwargs):
        instance = cls.__instances.get(cls)
        if instance:
            return instance

        instance = super().__call__(*args, **kwargs)
        cls.__instances[cls] = instance

        return instance
