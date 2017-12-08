

DB_ZONE_MAP = {
    "cle": "kbvsdb",
    "cle_legacy": "ccvsdb",
    "aws": "kbhs",
    "fa_aws": "fahs",
    "localhost": "localhost",
    "do": "localhost",
    }

DATABASE = {
    "ENGINE": "django.contrib.gis.db.backends.mysql",
    "HOST": "{database_host}",
    "NAME": "{service_name}_{env_name}",
    "USER": "root",
    "PASSWORD": "password",
    }


def getDatabase(zone,service,env):
    db = {}
    for key in DATABASE:
        value = DATABASE[key]
        if key == "HOST":
            value = value.format(database_host=DB_ZONE_MAP[zone])
        if key == "NAME":
            value = value.format(service_name=service,
                                 env_name=env)
        db[key] = value
    return db
