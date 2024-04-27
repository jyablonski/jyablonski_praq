from datetime import datetime
import json


def json_serializer(obj):
    if isinstance(obj, (datetime, datetime.date)):
        return obj.isoformat()
    raise "Type %s not serializable" % type(obj)


test = {"value": 10, "created_at": datetime.now()}

# you'll get a typerror because created_at is a datetime object
# which looks like `datetime.datetime(2024, 4, 27, 11, 15)` etc
dump1 = json.dumps(test)

# you get a raw string now with just a timestamp value
# which looks like `"2024-04-27T11:17:50.652182`
dump2 = json.dumps(test, default=json_serializer, ensure_ascii=False)

# encode it into bytes via utf-8 so it can be sent over the network
# networks transmit data in binary, this ensures it's properly encoded and transmitted
# same thing happens when you store data in a file
dump3 = json.dumps(test, default=json_serializer, ensure_ascii=False).encode("utf-8")

# json loads expects a string, but by default it will also detect bytes
# and decode it for you
dump4 = json.loads(dump3)

dump5 = json.loads(dump3.decode("utf-8"))
