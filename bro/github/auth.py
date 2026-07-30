"""GitHub authentication — Device Flow OAuth."""

from __future__ import annotations

import time

import httpx
import yaml

from bro.config.defaults import AUTH_FILE, BRO_HOME
from bro.utils.console import console, print_error, print_info, print_success
from bro.utils.logger import get_logger
from bro.utils.platform import open_url

logger = get_logger(__name__)

# Default OAuth App client ID (replace with your own for production)
CLIENT_ID = "Ov23liXXXXXXXXXXXXXX"  # Placeholder — users should register their own OAuth App


def ensure_authenticated() -> str | None:
    """Ensure the user is authenticated, returning a token or None."""
    # Check cached token
    token = _load_cached_token()
    if token:
        if _validate_token(token):
            return token
        logger.info("Cached token is invalid, re-authenticating")

    # Run device flow
    return device_flow_auth()


def device_flow_auth() -> str | None:
    """Authenticate using GitHub Device Flow."""
    console.print("\n[bold cyan]🔐 GitHub Authentication[/bold cyan]\n")

    try:
        # Step 1: Request device code
        resp = httpx.post(
            "https://github.com/login/device/code",
            data={"client_id": CLIENT_ID, "scope": "repo"},
            headers={"Accept": "application/json"},
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()

        device_code = data["device_code"]
        user_code = data["user_code"]
        verification_uri = data["verification_uri"]
        interval = data.get("interval", 5)
        expires_in = data.get("expires_in", 900)

        # Step 2: Show user the code
        console.print(f"  Open: [bold blue]{verification_uri}[/bold blue]")
        console.print(f"  Enter code: [bold yellow]{user_code}[/bold yellow]")
        console.print()

        # Try to open browser
        open_url(verification_uri)

        print_info("Waiting for authorization...")

        # Step 3: Poll for token
        start_time = time.time()
        while time.time() - start_time < expires_in:
            time.sleep(interval)

            token_resp = httpx.post(
                "https://github.com/login/oauth/access_token",
                data={
                    "client_id": CLIENT_ID,
                    "device_code": device_code,
                    "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
                },
                headers={"Accept": "application/json"},
                timeout=15,
            )
            token_data = token_resp.json()

            if "access_token" in token_data:
                token = token_data["access_token"]
                _save_cached_token(token)
                print_success("Successfully authenticated with GitHub!")
                return token
            elif token_data.get("error") == "authorization_pending":
                continue
            elif token_data.get("error") == "slow_down":
                interval += 5
            elif token_data.get("error") == "expired_token":
                print_error("Authorization timed out.")
                return None
            else:
                print_error(f"Auth error: {token_data.get('error_description', 'Unknown')}")
                return None

        print_error("Authorization timed out.")
        return None

    except Exception as e:
        logger.error("Device flow auth failed: %s", e)
        print_error(f"Authentication failed: {e}")
        return None


def _load_cached_token() -> str | None:
    """Load cached GitHub token."""
    if AUTH_FILE.exists():
        try:
            data = yaml.safe_load(AUTH_FILE.read_text(encoding="utf-8"))
            return data.get("github_token")
        except Exception:
            pass
    return None


def _save_cached_token(token: str) -> None:
    """Save GitHub token to cache."""
    BRO_HOME.mkdir(parents=True, exist_ok=True)
    AUTH_FILE.write_text(
        yaml.dump({"github_token": token}, default_flow_style=False),
        encoding="utf-8",
    )


def _validate_token(token: str) -> bool:
    """Check if a token is still valid."""
    try:
        resp = httpx.get(
            "https://api.github.com/user",
            headers={"Authorization": f"token {token}", "Accept": "application/json"},
            timeout=10,
        )
        return resp.status_code == 200
    except Exception:
        return False
