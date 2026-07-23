"""MkDocs hooks (clak-style): copy repo logo into the built site."""

import logging
import shutil
from pathlib import Path

logger = logging.getLogger("mkdocs")

_REPO_ROOT = Path(__file__).resolve().parent.parent
_LOGO_SRC = _REPO_ROOT / "logo"


def on_post_build(config, **kwargs):
    if not _LOGO_SRC.is_dir():
        logger.warning("Logo dir missing: %s", _LOGO_SRC)
        return
    dest = Path(config["site_dir"]) / "logo"
    logger.info("Copying logo to %s", dest)
    shutil.copytree(_LOGO_SRC, dest, dirs_exist_ok=True)
