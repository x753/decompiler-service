import json
import os
import subprocess
import sys
from distutils.util import strtobool
from typing import List, Union


class EnvironmentVariable:
    def __init__(self, cast, name, default):
        self.cast = cast
        self.name = name
        self.default = default

    @property
    def value(self):
        val = os.environ.get(self.name, self.default)
        if self.cast is not None and val is not None and isinstance(val, str):
            val = self.cast(val)
        return val

    @value.setter
    def value(self, val):
        if val is None and self.name in os.environ:
            del os.environ[self.name]
        else:
            os.environ[self.name] = str(val)

    def __str__(self):
        if self.value is None:
            return ""
        return str(self.value)

    def __bool__(self):
        return bool(self.value)


VARIABLES = {}


def run_command(command: Union[List[Union[EnvironmentVariable, str]], str]) -> int:
    environment = {
        **os.environ,
        **({k: str(v) for k, v in VARIABLES.items() if v is not None}),
    }
    if isinstance(command, str):
        command = command.split(" ")
    else:
        command = [str(x) for x in command]
    print(" ".join(command))
    result = subprocess.call(command, env=environment)
    if result != 0:
        sys.exit(result)
    return result


def register_variable(cast, name, default):
    var = EnvironmentVariable(cast, name, default)
    VARIABLES[name] = var
    return var


def to_bool(val) -> bool:
    if not val:
        return False
    return bool(strtobool(val))


SERVER_PORT = register_variable(int, "PORT", 8000)
SERVER_HOST = register_variable(str, "HOST", "0.0.0.0")

RUN_MODE = register_variable(str, "RUN_MODE", "uvicorn")
AUTORELOAD = register_variable(str, "AUTORELOAD", False)


def run_uvicorn() -> None:
    print("Launching gunicorn production server")
    command = [
        "python",
        "-m",
        "uvicorn",
        "decapi.app:app",
        "--host",
        f"{SERVER_HOST}",
        "--port",
        f"{SERVER_PORT}",
    ]
    if AUTORELOAD:
        command += ["--reload"]
    run_command(command)


def run_server(mode: str) -> None:
    if mode == "uvicorn":
        run_uvicorn()


def dump_env() -> None:
    with open(os.path.expanduser("~") + "/.bashrc", "a") as f:
        f.writelines(
            [
                f'declare -x {key}="{str(var)}"\n'
                for key, var in VARIABLES.items()
                if var.value is not None
            ]
        )
    with open("/var/run/app-launch.json", "w") as f:
        f.write(json.dumps({k: str(v) for k, v in VARIABLES.items()}))


def main():
    mode = (" ".join(sys.argv[1:])).strip()
    if mode in {"uvicorn"}:
        RUN_MODE.value = mode
        dump_env()
        run_server(mode)
    elif sys.argv[1:]:
        RUN_MODE.value = None
        dump_env()
        run_command(sys.argv[1:])
    else:
        dump_env()
        run_server(str(RUN_MODE))


if __name__ == "__main__":
    main()
