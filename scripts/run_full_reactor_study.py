# run_full_reactor_study.py
# 功能：
# 1. 读取 project_config.yaml
# 2. 根据 enabled 开关决定要不要运行 pitch / enrichment 扫描
# 3. 根据 workflow 配置决定要不要自动分析
# 4. 根据 workflow 配置决定要不要自动清理旧 statepoints
#
# 使用方法：
# python scripts/run_full_reactor_study.py

import subprocess
import sys
from pathlib import Path

from config_loader import load_config


def run_script(script_path: Path, extra_args=None):
    """
    运行单个脚本，并打印运行状态
    """
    if extra_args is None:
        extra_args = []

    print(f"\n{'=' * 60}")
    print(f"正在运行：{script_path.name}")
    if extra_args:
        print(f"附加参数：{' '.join(extra_args)}")
    print(f"{'=' * 60}")

    try:
        subprocess.run(
            [sys.executable, str(script_path)] + extra_args,
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

    config = load_config()

    pitch_scan_cfg = config.get("pitch_scan", {})
    enrichment_scan_cfg = config.get("enrichment_scan", {})
    workflow_cfg = config.get("workflow", {})

    pitch_enabled = pitch_scan_cfg.get("enabled", True)
    enrichment_enabled = enrichment_scan_cfg.get("enabled", True)

    auto_analyze = workflow_cfg.get("auto_analyze_after_run", True)
    auto_clean = workflow_cfg.get("auto_clean_statepoints", False)
    clean_days = workflow_cfg.get("clean_days", 7)
    clean_delete_mode = workflow_cfg.get("clean_delete_mode", False)

    success_count = 0
    fail_count = 0
    skip_count = 0

    print("\n开始运行完整反应堆研究流程...")

    # =========================
    # 1. 运行 pitch 扫描
    # =========================
    if pitch_enabled:
        script = current_dir / "test_openmc6.py"
        if script.exists():
            result = run_script(script)
            if result == "success":
                success_count += 1
            else:
                fail_count += 1
        else:
            print(f"\n跳过：{script.name} 不存在")
            skip_count += 1
    else:
        print("\n根据 project_config.yaml，已跳过 pitch 扫描（pitch_scan.enabled = false）")
        skip_count += 1

    # =========================
    # 2. 运行 enrichment 扫描
    # =========================
    if enrichment_enabled:
        script = current_dir / "test_openmc7.py"
        if script.exists():
            result = run_script(script)
            if result == "success":
                success_count += 1
            else:
                fail_count += 1
        else:
            print(f"\n跳过：{script.name} 不存在")
            skip_count += 1
    else:
        print("\n根据 project_config.yaml，已跳过 enrichment 扫描（enrichment_scan.enabled = false）")
        skip_count += 1

    # =========================
    # 3. 自动分析
    # =========================
    if auto_analyze and (pitch_enabled or enrichment_enabled):
        script = current_dir / "run_all_analysis.py"
        if script.exists():
            result = run_script(script)
            if result == "success":
                success_count += 1
            else:
                fail_count += 1
        else:
            print(f"\n跳过：{script.name} 不存在")
            skip_count += 1
    else:
        print("\n根据 workflow 配置，已跳过自动分析。")
        skip_count += 1

    # =========================
    # 4. 自动清理 statepoints
    # =========================
    if auto_clean:
        script = current_dir / "clean_old_statepoints.py"
        if script.exists():
            extra_args = ["--days", str(clean_days)]
            if clean_delete_mode:
                extra_args.append("--delete")

            result = run_script(script, extra_args=extra_args)
            if result == "success":
                success_count += 1
            else:
                fail_count += 1
        else:
            print(f"\n跳过：{script.name} 不存在")
            skip_count += 1
    else:
        print("\n根据 workflow 配置，已跳过自动清理 statepoints。")
        skip_count += 1

    # =========================
    # 5. 最终总结
    # =========================
    print(f"\n{'=' * 60}")
    print("完整流程结束")
    print(f"成功：{success_count}")
    print(f"失败：{fail_count}")
    print(f"跳过：{skip_count}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()