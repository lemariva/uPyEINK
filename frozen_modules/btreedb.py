import utime
import ujson
from ucollections import namedtuple
import btree


class DB:

    def __init__(self, name, **options):
        self.name = name
        self.f = None
        self.db = None
        self.options = options

    def connect(self):
        try:
            self.f = open(self.name, "r+b")
        except OSError:
            self.f = open(self.name, "w+b")
        self.db = btree.open(self.f, **self.options)

    def close(self):
        self.db.close()
        self.f.close()


class Model:

    __fields__ = None
    Row = None
    row_buf = None

    @classmethod
    def create_table(cls, fail_silently=False):
        cls.__fields__ = tuple(cls.__schema__.keys())
        cls.Row = namedtuple(cls.__table__, cls.__fields__)
        # Static buffer, should work for uasyncio environment
        cls.row_buf = [None] * len(cls.__fields__)

    @classmethod
    def create(cls, **fields):
        row = cls.row_buf
        db = cls.__db__.db
        i = 0
        for k, v in cls.__schema__.items():
            if k not in fields:
                default = v[1]
                if callable(default):
                    default = default()
                row[i] = default
            else:
                row[i] = fields[k]
            i += 1

        pkey = row[0]
        db[pkey] = ujson.dumps(row)
        db.flush()
        #print("create: pkey:", pkey)
        return pkey

    @classmethod
    def update(cls, where, **fields):
        pkey_field = cls.__fields__[0]
        assert len(where) == 1 and pkey_field in where
        #print("update:", where)

        db = cls.__db__.db
        pkey = where[pkey_field]
        row = ujson.loads(db[pkey])
        i = 0
        for k in cls.__fields__:
            if k in fields:
                row[i] = fields[k]
            i += 1
        db[pkey] = ujson.dumps(row)
        db.flush()

    @classmethod
    def get_id(cls, pkey):
        return [cls.Row(*ujson.loads(cls.__db__.db[pkey]))]

    @classmethod
    def scan(cls):
        for v in cls.__db__.db.values():
            yield cls.Row(*ujson.loads(v))

if hasattr(utime, "localtime"):
    def now():
        return "%d-%02d-%02d %02d:%02d:%02d" % utime.localtime()[:6]
    def id():
        return "%d%02d%02d%02d%02d%02d" % utime.localtime()[:6]
else:
    def now():
        return str(int(utime.time()))
