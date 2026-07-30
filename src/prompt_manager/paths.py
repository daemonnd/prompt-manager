from platformdirs import user_config_dir, user_data_dir, user_log_dir
from pathlib import Path

DATA_DIR: Path = Path(user_data_dir("prompt_manager"))
PROMPT_TEMPLATES: Path = DATA_DIR / "templates"
PROMPTS_DIR: Path = DATA_DIR / "prompts"
DATABASE_DIR: Path = DATA_DIR / "templates.db"

LOG_DIR: Path = Path(user_log_dir("prompt_manager"))
LOG_FILE: Path = LOG_DIR / "prompt_manager.jsonl"

CONFIG_DIR: Path = Path(user_config_dir("prompt_manager"))
CONFIG_FILE: Path = CONFIG_DIR / "config.toml"
