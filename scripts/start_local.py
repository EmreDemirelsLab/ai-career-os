"""Start the single-owner local workspace without overwriting settings or deleting data."""

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(command):
    return subprocess.run(command, cwd=ROOT, check=True)


def main():
    if shutil.which("docker") is None:
        raise SystemExit("Docker is required. Install/start Docker with Compose v2, then retry.")
    try:
        run(["docker", "compose", "version"])
        if not (ROOT / ".env").exists():
            run([sys.executable, "scripts/init_workspace.py"])
        run(["docker", "compose", "up", "--build", "-d", "--wait", "--wait-timeout", "180"])
        run(["docker", "compose", "exec", "-T", "api", "career-os", "seed"])
    except subprocess.CalledProcessError as exc:
        raise SystemExit(
            "Startup did not finish. Check Docker and `docker compose logs`. "
            "Existing settings/data were preserved; resolve the error and retry."
        ) from exc
    print("Open http://localhost:3000 and use CAREER_API_TOKEN from your local .env.")
    print("The key was not printed. Keep it private. No live jobs were collected.")
    print("Stop with: docker compose down (retains your data).")


if __name__ == "__main__":
    main()
