"""
bob_runner.py
-------------
Thin service layer that invokes IBM Bob in non-interactive mode
as a subprocess using the `bob run` command.

Environment variables consumed:
  BOB_EXECUTABLE_PATH   - absolute or relative path to the bob CLI binary
  BOB_API_KEY           - API key forwarded to Bob via environment
  BOB_TIMEOUT_SECONDS   - max seconds to wait (default 120)
"""

import json
import os
import subprocess
from typing import Any


def _get_bob_env() -> dict[str, str]:
    """Build the environment for the Bob subprocess.

    Inherits the current process environment and injects BOB_API_KEY
    so the credential is never hardcoded.
    """
    env = os.environ.copy()

    bob_api_key = os.getenv("BOB_API_KEY", "")
    if bob_api_key:
        env["BOB_API_KEY"] = bob_api_key

    return env


def run_bob_scaffold(project_spec: dict[str, Any]) -> dict[str, Any]:
    """Run IBM Bob using the `bob run` command against project_spec.

    Parameters
    ----------
    project_spec:
        Arbitrary dict describing the project.

    Returns
    -------
    dict with keys:
        status     - "success" | "error" | "timeout"
        output     - stdout from Bob
        error      - stderr from Bob or exception message
        exit_code  - process exit code, or None on timeout/exception
    """

    bob_executable = os.getenv("BOB_EXECUTABLE_PATH", "bob")
    timeout_raw = os.getenv("BOB_TIMEOUT_SECONDS", "120")

    try:
        timeout = int(timeout_raw)
    except ValueError:
        timeout = 120

    spec_json = json.dumps(project_spec)

    # Bob's installed CLI uses:
    # bob run [options] [prompt...]
    #
    # Therefore, pass the project specification as the prompt
    # instead of using the unsupported --headless/--input arguments.
    prompt = (
        "Execute the following HackMate project specification. "
        "Use it as the task specification for this project.\n\n"
        f"Project specification:\n{spec_json}"
    )

    try:
        result = subprocess.run(
            [
                bob_executable,
                "run",
                "--format",
                "json",
                prompt,
            ],
            capture_output=True,
            text=True,
            timeout=timeout,
            env=_get_bob_env(),
        )

        if result.returncode == 0:
            return {
                "status": "success",
                "output": result.stdout,
                "error": result.stderr,
                "exit_code": result.returncode,
            }

        return {
            "status": "error",
            "output": result.stdout,
            "error": result.stderr
            or f"Bob exited with code {result.returncode}",
            "exit_code": result.returncode,
        }

    except FileNotFoundError:
        return {
            "status": "error",
            "output": "",
            "error": (
                f"Bob executable not found at '{bob_executable}'. "
                "Set BOB_EXECUTABLE_PATH to the correct path."
            ),
            "exit_code": None,
        }

    except subprocess.TimeoutExpired:
        return {
            "status": "timeout",
            "output": "",
            "error": f"Bob did not complete within {timeout} seconds.",
            "exit_code": None,
        }

    except Exception as exc:
        return {
            "status": "error",
            "output": "",
            "error": str(exc),
            "exit_code": None,
        }