from platformdirs import user_data_dir
from pathlib import Path

DATA_DIR: Path = Path(user_data_dir("prompt_library"))
PROMPT_TEMPLATES: Path = DATA_DIR / "templates"
PROMPTS_DIR: Path = DATA_DIR / "prompts"
DATABASE_DIR: Path = DATA_DIR / "templates.db"
