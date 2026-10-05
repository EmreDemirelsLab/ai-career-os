import os


def compose_command() -> list[str]:
    command = ["docker", "compose"]
    for variable, flag in [
        ("CAREER_COMPOSE_FILE", "-f"),
        ("CAREER_COMPOSE_ENV_FILE", "--env-file"),
    ]:
        value = os.environ.get(variable)
        if value:
            command.extend([flag, value])
    return command
