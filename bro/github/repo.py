"""GitHub repository management — create and push."""

from __future__ import annotations

from pathlib import Path

from github import Auth, Github
from github.AuthenticatedUser import AuthenticatedUser

from bro.utils.console import print_error, print_info, print_success
from bro.utils.logger import get_logger
from bro.utils.process import run

logger = get_logger(__name__)


def create_and_push(
    token: str,
    repo_name: str,
    project_dir: Path,
    private: bool = True,
    description: str = "",
) -> bool:
    """Create a GitHub repo and push the local project."""
    try:
        auth = Auth.Token(token)
        g = Github(auth=auth)
        user = g.get_user()

        print_info(f"Creating GitHub repository: [bold]{user.login}/{repo_name}[/bold]")

        if not isinstance(user, AuthenticatedUser):
            print_error("Failed to authenticate user for repo creation.")
            return False

        repo = user.create_repo(
            name=repo_name,
            description=description or f"{repo_name} — scaffolded with Bro",
            private=private,
            auto_init=False,
        )

        # Add remote and push
        run(f"git remote add origin {repo.clone_url}", cwd=project_dir)
        run("git branch -M main", cwd=project_dir)
        result = run("git push -u origin main", cwd=project_dir, timeout=60)

        if result.success:
            privacy = "🔒 Private" if private else "🌍 Public"
            print_success(f"Repository created: [bold]{repo.html_url}[/bold] ({privacy})")
            return True
        else:
            print_error(f"Push failed: {result.stderr}")
            print_info(f"Remote added. Try: [bold]cd {project_dir} && git push -u origin main[/bold]")
            return False

    except Exception as e:
        logger.error("GitHub repo creation failed: %s", e)
        print_error(f"Failed to create repository: {e}")
        return False
