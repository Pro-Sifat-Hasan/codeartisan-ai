import subprocess
from typing import Dict, Optional


def run_terminal(
    command: str,
    *,
    cwd: Optional[str] = None,
    timeout: int = 30,
    shell: bool = True,
) -> Dict[str, str | int | bool | bytes]:
    """
    Execute a terminal command and capture output.

    Args:
        command (str): Command to execute
        cwd (str | None): Working directory
        timeout (int): Timeout in seconds
        shell (bool): Whether to execute via shell

    Returns:
        dict: Execution result
    """

    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            shell=shell,
            capture_output=True,
            text=True,
            timeout=timeout,
        )

        return {
            "command": command,
            "returncode": result.returncode,
            "success": result.returncode == 0,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
        }

    except subprocess.TimeoutExpired as e:
        return {
            "command": command,
            "returncode": -1,
            "success": False,
            "stdout": e.stdout.strip() if e.stdout else "",
            "stderr": "Command timed out",
        }

    except Exception as e:
        return {
            "command": command,
            "returncode": -1,
            "success": False,
            "stdout": "",
            "stderr": str(e),
        }
