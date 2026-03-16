# analyze_pitch_results.py
# 功能：
# 1. 自动读取 results/pitch_scan 里的最新 CSV
# 2. 绘制带误差棒的 k-effective 曲线
# 3. 自动找出 k-effective 最大时对应的最佳 pitch
# 4. 保存分析图和文字总结
#
# 使用方法：
# 先确保你已经运行过 test_openmc6.py，生成了 pitch_keff_results_时间戳.csv
# 然后运行：
# python scripts/analyze_pitch_results.py

from datetime import datetime
import csv

import matplotlib.pyplot as plt

from common_paths import RESULTS_DIR
from config_loader import load_config


# =========================
# 1. 读取配置
# =========================
config = load_config()

analysis_cfg = config["analysis"]
pitch_cfg = analysis_cfg["pitch"]

SCAN_DIR = RESULTS_DIR / pitch_cfg["scan_dir"]
ANALYSIS_DIR = SCAN_DIR / pitch_cfg["analysis_dir"]
ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)

SAVE_PLOTS = analysis_cfg["save_plots"]
SAVE_REPORTS = analysis_cfg["save_reports"]
SHOW_PLOTS = analysis_cfg["show_plots"]


# =========================
# 2. 找到最新的结果 CSV
# =========================
csv_files = sorted(SCAN_DIR.glob(pitch_cfg["csv_pattern"]))

if not csv_files:
    raise FileNotFoundError(
        f"在 {SCAN_DIR} 中没有找到 {pitch_cfg['csv_pattern']}，请先运行 test_openmc6.py"
    )

latest_csv = csv_files[-1]
print(f"将要分析的 CSV 文件：{latest_csv}")


# =========================
# 3. 读取 CSV 数据
# =========================
pitches = []
k_values = []
uncertainties = []

with open(latest_csv, "r", newline="") as f:
    reader = csv.DictReader(f)

    for row in reader:
        pitches.append(float(row["Pitch (cm)"]))
        k_values.append(float(row["k-effective"]))
        uncertainties.append(float(row["uncertainty"]))

if len(pitches) < 1:
    raise ValueError("CSV 中没有有效数据。")


# =========================
# 4. 找到最佳 pitch
# =========================
max_index = k_values.index(max(k_values))
best_pitch = pitches[max_index]
best_keff = k_values[max_index]
best_uncertainty = uncertainties[max_index]


# =========================
# 5. 生成输出文件名
# =========================
timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
plot_path = ANALYSIS_DIR / f"{pitch_cfg['plot_prefix']}_{timestamp}.png"
report_path = ANALYSIS_DIR / f"{pitch_cfg['report_prefix']}_{timestamp}.txt"


# =========================
# 6. 绘图
# =========================
plt.figure(figsize=(8, 6))

plt.errorbar(
    pitches,
    k_values,
    yerr=uncertainties,
    fmt="o-",
    capsize=4
)

plt.axvline(best_pitch, linestyle="--")
plt.annotate(
    f"best pitch ≈ {best_pitch:.4f} cm\nkeff ≈ {best_keff:.6f}",
    xy=(best_pitch, best_keff),
    xytext=(best_pitch, best_keff + 0.01),
    arrowprops=dict(arrowstyle="->")
)

plt.xlabel(pitch_cfg["xlabel"])
plt.ylabel(pitch_cfg["ylabel"])
plt.title(pitch_cfg["title"])
plt.grid(True)
plt.tight_layout()

if SAVE_PLOTS:
    plt.savefig(plot_path, dpi=300)

if SHOW_PLOTS:
    plt.show()
else:
    plt.close()


# =========================
# 7. 生成文字总结
# =========================
if SAVE_REPORTS:
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("OpenMC pitch scan analysis\n")
        f.write("=" * 40 + "\n\n")
        f.write(f"Source CSV: {latest_csv}\n")
        f.write(f"Number of points: {len(pitches)}\n")
        f.write(f"Minimum pitch: {min(pitches):.6f} cm\n")
        f.write(f"Maximum pitch: {max(pitches):.6f} cm\n")
        f.write(f"Minimum k-effective: {min(k_values):.6f}\n")
        f.write(f"Maximum k-effective: {max(k_values):.6f}\n\n")

        f.write("Best pitch estimation:\n")
        f.write(f"Best pitch = {best_pitch:.6f} cm\n")
        f.write(f"k-effective at best pitch = {best_keff:.6f}\n")
        f.write(f"uncertainty at best pitch = {best_uncertainty:.6f}\n\n")

        f.write("Detailed data:\n")
        f.write("Pitch (cm)\tk-effective\tuncertainty\n")
        for p, k, u in zip(pitches, k_values, uncertainties):
            f.write(f"{p:.6f}\t{k:.6f}\t{u:.6f}\n")


# =========================
# 8. 在终端输出结果
# =========================
print("\n=== 分析完成 ===")
print(f"读取的 CSV：{latest_csv}")

if SAVE_PLOTS:
    print(f"分析图已保存为：{plot_path}")
else:
    print("当前配置为不保存分析图。")

if SAVE_REPORTS:
    print(f"文字总结已保存为：{report_path}")
else:
    print("当前配置为不保存文字报告。")

print(f"最佳 pitch = {best_pitch:.6f} cm")
print(f"对应的 k-effective = {best_keff:.6f} ± {best_uncertainty:.6f}")