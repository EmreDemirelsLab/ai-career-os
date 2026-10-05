"""Local Compose backup. Contains personal data; never commit the archive."""

import hashlib
import os
import subprocess
import sys
from pathlib import Path

path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("backups/career.dump")
path.parent.mkdir(parents=True, exist_ok=True)
fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
try:
    with os.fdopen(fd, "wb") as out:
        subprocess.run(
            [
                "docker",
                "compose",
                "exec",
                "-T",
                "postgres",
                "pg_dump",
                "-U",
                "career",
                "-d",
                "career",
                "-Fc",
            ],
            stdout=out,
            check=True,
        )
except BaseException:
    path.unlink(missing_ok=True)
    raise
checksum = hashlib.sha256(path.read_bytes()).hexdigest()
path.with_suffix(path.suffix + ".sha256").write_text(checksum + "\n")
print("Backup created with private file permissions. Encrypt before external storage.")
