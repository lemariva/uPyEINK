from ucollections import OrderedDict
import ujson
import utime

import btreedb as uorm
import btree


db = uorm.DB("notes.db")

class Note(uorm.Model):

    __db__ = db
    __table__ = "note"
    __schema__ = OrderedDict([
        ("id", ("INT", uorm.id)),
        ("timestamp", ("TIMESTAMP", uorm.now)),
        ("archived", ("INT", 0)),
        ("content", ("TEXT", "")),
    ])


    @classmethod
    def public(cls):
        print("public")
        for v in cls.__db__.db.values(None, None, btree.DESC):
            res = ujson.loads(v)
            row = cls.Row(*res)
            if row.archived:
                continue
            yield row

    @classmethod
    def get_keys(cls):
        keys = []
        for key in cls.__db__.db:
            keys.append(key)
        return keys

    @classmethod
    def del_key(cls, key):
        del cls.__db__.db[key]
        cls.__db__.db.flush()
        return 0