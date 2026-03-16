# clean_old_statepoints.py
# 功能：
# 1. 扫描 statepoints 文件夹
# 2. 找出其中较旧的运行结果子文件夹
# 3. 支持“预览模式”和“实际删除模式”
#
# 使用方法：
# 预览将被删除的文件夹（不真正删除）：
# python scripts/clean_old_statepoints.py
#
# 删除 7 天前的运行文件夹：
# python scripts/clean_old_statepoints.py --days 7 --delete
#
# 删除 30 天前的运行文件夹：
# python scripts/clean_old_statepoints.py --days 30 --delete

from pathlib import Path
from datetime import datetime, timedelta
import shutil
import argparse

from common_paths import STATEPOINTS_DIR


def find_candidate_dirs(base_dir: Path):
    """
    找出 statepoints 下面的所有运行子文件夹。
    例如：
    statepoints/enrichment_scan/enrichment_0.20/
    statepoints/pitch_scan/pitch_1.50/
    """
    candidates = []

    if not base_dir.exists():
        return candidates

    for scan_dir in base_dir.iterdir():
        if not scan_dir.is_dir():
            continue

        for run_dir in scan_dir.iterdir():
            if not run_dir.is_dir():
                continue

            # 取文件夹最后修改时间
            mtime = datetime.fromtimestamp(run_dir.stat().st_mtime)
            candidates.append((run_dir, mtime))

    return candidates


def main():
    parser = argparse.ArgumentParser(description="清理旧的 OpenMC statepoints 运行文件夹")
    parser.add_argument(
        "--days",
        type=int,
        default=7,
        help="删除多少天以前的运行文件夹，默认 7 天"
    )
    parser.add_argument(
        "--delete",
        action="store_true",
        help="真正执行删除；如果不加这个参数，则只预览"
    )

    args = parser.parse_args()

    cutoff_time = datetime.now() - timedelta(days=args.days)
    candidates = find_candidate_dirs(STATEPOINTS_DIR)

    old_dirs = []
    for run_dir, mtime in candidates:
        if mtime < cutoff_time:
            old_dirs.append((run_dir, mtime))

    print(f"\n=== Statepoints 清理工具 ===")
    print(f"扫描目录：{STATEPOINTS_DIR}")
    print(f"规则：查找 {args.days} 天前的运行文件夹")
    print(f"当前模式：{'实际删除' if args.delete else '仅预览'}")

    if not old_dirs:
        print("\n没有找到符合条件的旧运行文件夹。")
        return

    print(f"\n找到 {len(old_dirs)} 个候选文件夹：")
    for run_dir, mtime in sorted(old_dirs, key=lambda x: x[1]):
        print(f"- {run_dir}    最后修改时间：{mtime.strftime('%Y-%m-%d %H:%M:%S')}")

    if not args.delete:
        print("\n当前是预览模式，没有真正删除任何文件夹。")
        print("如果确认要删，请使用例如：")
        print("python scripts/clean_old_statepoints.py --days 7 --delete")
        return

    print("\n开始删除...")
    deleted_count = 0

    for run_dir, _ in old_dirs:
        shutil.rmtree(run_dir)
        deleted_count += 1
        print(f"已删除：{run_dir}")

    print(f"\n删除完成，共删除 {deleted_count} 个运行文件夹。")


if __name__ == "__main__":
    main()