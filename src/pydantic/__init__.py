class FieldInfo:
    def __init__(self, default=None, ge=None, le=None, gt=None, description=None):
        self.default = default
        self.ge = ge
        self.le = le
        self.gt = gt
        self.description = description

def Field(default=None, **kwargs):
    return FieldInfo(default=default, **kwargs)

class BaseModelMeta(type):
    def __new__(mcls, name, bases, ns):
        annotations = ns.get('__annotations__', {})
        defaults = {}
        infos = {}
        for fname in annotations:
            value = ns.get(fname, None)
            if isinstance(value, FieldInfo):
                defaults[fname] = value.default
                infos[fname] = value
            else:
                defaults[fname] = value
        ns['_defaults'] = defaults
        ns['_field_infos'] = infos
        return super().__new__(mcls, name, bases, ns)

class BaseModel(metaclass=BaseModelMeta):
    def __init__(self, **data):
        for name, default in self._defaults.items():
            value = data.pop(name, default)
            info = self._field_infos.get(name)
            if info:
                if info.ge is not None and value < info.ge:
                    raise ValueError(f'{name} must be >= {info.ge}')
                if info.le is not None and value > info.le:
                    raise ValueError(f'{name} must be <= {info.le}')
                if info.gt is not None and value <= info.gt:
                    raise ValueError(f'{name} must be > {info.gt}')
            setattr(self, name, value)
        if data:
            raise ValueError(f'Unexpected fields: {list(data.keys())}')
