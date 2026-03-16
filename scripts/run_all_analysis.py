# run_all_analysis.py
# 功能：
# 1. 读取 project_config.yaml
# 2. 根据 enabled 开关决定要不要运行 enrichment / pitch 分析
# 3. 自动依次运行可用的分析脚本
# 4. 如果脚本不存在或运行失败，会给出提示
#
# 使用方法：
# python scripts/run_all_analysis.py

import subprocess
import sys
from pathlib import Path

from config_loader import load_config


def run_script(script_path: Path):
    """
    运行单个分析脚本，并打印运行结果
    """
    print(f"\n{'=' * 60}")
    print(f"正在运行：{script_path.name}")
    print(f"{'=' * 60}")

    try:
        subprocess.run(
            [sys.executable, str(script_path)],
            check=True,
            text=True
        )
        print(f"\n{script_path.name} 运行完成。")
        return "success"

    except subprocess.CalledProcessError as e:
        print(f"\n{script_path.name} 运行失败。")
        print(f"返回码：{e.returncode}")
        return "failed"

    except FileNotFoundError:
        print(f"\n没有找到脚本：{script_path}")
        return "missing"


def main():
    current_dir = Path(__file__).resolve().parent

    # =========================
    # 1. 读取配置文件
    # =========================
    config = load_config()

    pitch_scan_cfg = config.get("pitch_scan", {})
    enrichment_scan_cfg = config.get("enrichment_scan", {})

    pitch_enabled = pitch_scan_cfg.get("enabled", True)
    enrichment_enabled = enrichment_scan_cfg.get("enabled", True)

    # =========================
    # 2. 根据配置决定要运行哪些分析脚本
    # =========================
    scripts_to_run = []

    if enrichment_enabled:
        scripts_to_run.append(current_dir / "analyze_enrichment_results.py")
    else:
        print("\n根据 project_config.yaml，已跳过 enrichment 分析（enrichment_scan.enabled = false）")

    if pitch_enabled:
        scripts_to_run.append(current_dir / "analyze_pitch_results.py")
    else:
        print("\n根据 project_config.yaml，已跳过 pitch 分析（pitch_scan.enabled = false）")

    # =========================
    # 3. 统计信息
    # =========================
    success_count = 0
    fail_count = 0
    skip_count = 0

    print("\n开始运行所有已启用的分析脚本...")

    if not scripts_to_run:
        print("\n没有任何启用的分析任务。请检查 project_config.yaml 中的 enabled 设置。")
        return

    # =========================
    # 4. 逐个运行
    # =========================
    for script in scripts_to_run:
        if not script.exists():
            print(f"\n跳过：{script.name} 不存在")
            skip_count += 1
            continue

        result = run_script(script)

        if result == "success":
            success_count += 1
        elif result in ("failed", "missing"):
            fail_count += 1
        else:
            skip_count += 1

    # =========================
    # 5. 最终总结
    # =========================
    print(f"\n{'=' * 60}")
    print("所有分析任务结束")
    print(f"成功：{success_count}")
    print(f"失败：{fail_count}")
    print(f"跳过：{skip_count}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()