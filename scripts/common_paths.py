from pathlib import Path
from contextlib import contextmanager
import os

# 这个文件在 scripts 文件夹里
# scripts 的上一级就是整个项目根目录 openmc_project
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# 项目里的几个固定文件夹
INPUT_DIR = PROJECT_ROOT / "input"
RESULTS_DIR = PROJECT_ROOT / "results"
STATEPOINTS_DIR = PROJECT_ROOT / "statepoints"

# 如果文件夹不存在，就自动创建
for folder in [INPUT_DIR, RESULTS_DIR, STATEPOINTS_DIR]:
    folder.mkdir(parents=True, exist_ok=True)

def make_scan_dirs(scan_name: str):
    """
    给某一种扫描建立专属目录
    例如:
        make_scan_dirs("enrichment_scan")
    会返回:
        results/enrichment_scan
        statepoints/enrichment_scan
    """
    result_dir = RESULTS_DIR / scan_name
    statepoint_dir = STATEPOINTS_DIR / scan_name

    result_dir.mkdir(parents=True, exist_ok=True)
    statepoint_dir.mkdir(parents=True, exist_ok=True)

    return result_dir, statepoint_dir

@contextmanager
def working_directory(path: Path):
    """
    临时切换当前工作目录
    用完后自动切回去
    """
    old_cwd = Path.cwd()
    os.chdir(str(path))
    try:
        yield
    finally:
        os.chdir(str(old_cwd))