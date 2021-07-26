

class ClassHelper:

    @staticmethod
    def get_full_class_name(cls: object) -> str:
        return f'{cls.__class__.__module__}.{cls.__class__.__name__}'
