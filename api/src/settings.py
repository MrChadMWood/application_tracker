import os


# Safekeeping for now
class MissingEnvironmentVariable(Exception):
    pass

def get_env_var(var_name, safe=False):
    try:
        return os.environ[var_name]
    except KeyError:
        if not safe:
            raise MissingEnvironmentVariable(f"{var_name} does not exist")

dbconn_config = {
    'username': 'admin',
    'password': 'admin',
    'hostname': 'storage',
    'port': 5432,
    'database': 'apptracker'
}

hot_reload = True