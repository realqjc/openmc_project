# config_loader.py
# 功能：读取项目根目录下的 project_config.yaml

from pathlib import Path
import yaml


def load_config():
    project_root = Path(__file__).resolve().parent.parent
    config_path = project_root / "project_config.yaml"

    if not config_path.exists():
        raise FileNotFoundError(f"没有找到配置文件：{config_path}")

    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    return config