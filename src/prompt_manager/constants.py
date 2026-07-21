from platformdirs import user_data_dir
from pathlib import Path

PROMPT_TEMPLATES = Path(user_data_dir("prompt_library")) / "templates"
PROMPTS_DIR: Path = Path(user_data_dir("prompt_library")) / "prompts"
