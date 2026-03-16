# analyze_enrichment_results.py
# 功能：
# 1. 自动读取 results/enrichment_scan 里的最新 CSV
# 2. 绘制带误差棒的 k-effective 曲线
# 3. 自动估算临界富集度（k=1 对应的 enrichment）
# 4. 保存分析图和文字总结
#
# 使用方法：
# 先确保你已经运行过 test_openmc7.py，生成了 enrichment_keff_results_时间戳.csv
# 然后运行：
# python scripts/analyze_enrichment_results.py

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
enrichment_cfg = analysis_cfg["enrichment"]

SCAN_DIR = RESULTS_DIR / enrichment_cfg["scan_dir"]
ANALYSIS_DIR = SCAN_DIR / enrichment_cfg["analysis_dir"]
ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)

SAVE_PLOTS = analysis_cfg["save_plots"]
SAVE_REPORTS = analysis_cfg["save_reports"]
SHOW_PLOTS = analysis_cfg["show_plots"]


# =========================
# 2. 找到最新的结果 CSV
# =========================
csv_files = sorted(SCAN_DIR.glob(enrichment_cfg["csv_pattern"]))

if not csv_files:
    raise FileNotFoundError(
        f"在 {SCAN_DIR} 中没有找到 {enrichment_cfg['csv_pattern']}，请先运行 test_openmc7.py"
    )

latest_csv = csv_files[-1]
print(f"将要分析的 CSV 文件：{latest_csv}")


# =========================
# 3. 读取 CSV 数据
# =========================
enrichments = []
k_values = []
uncertainties = []

with open(latest_csv, "r", newline="") as f:
    reader = csv.DictReader(f)

    for row in reader:
        enrichments.append(float(row["Enrichment (%)"]))
        k_values.append(float(row["k-effective"]))
        uncertainties.append(float(row["uncertainty"]))

if len(enrichments) < 2:
    raise ValueError("CSV 数据点太少，至少需要 2 个点才能分析。")


# =========================
# 4. 估算临界富集度
# =========================
critical_enrichment = None
crossing_interval = None

for i in range(len(enrichments) - 1):
    e1 = enrichments[i]
    e2 = enrichments[i + 1]
    k1 = k_values[i]
    k2 = k_values[i + 1]

    if k1 == 1.0:
        critical_enrichment = e1
        crossing_interval = (e1, e1)
        break

    if (k1 - 1.0) * (k2 - 1.0) < 0:
        critical_enrichment = e1 + (1.0 - k1) * (e2 - e1) / (k2 - k1)
        crossing_interval = (e1, e2)
        break


# =========================
# 5. 生成输出文件名
# =========================
timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
plot_path = ANALYSIS_DIR / f"{enrichment_cfg['plot_prefix']}_{timestamp}.png"
report_path = ANALYSIS_DIR / f"{enrichment_cfg['report_prefix']}_{timestamp}.txt"


# =========================
# 6. 绘图
# =========================
plt.figure(figsize=(8, 6))

plt.errorbar(
    enrichments,
    k_values,
    yerr=uncertainties,
    fmt="o-",
    capsize=4
)

plt.axhline(1.0, linestyle="--")

if critical_enrichment is not None:
    plt.axvline(critical_enrichment, linestyle="--")
    plt.annotate(
        f"critical enrichment ≈ {critical_enrichment:.4f}%",
        xy=(critical_enrichment, 1.0),
        xytext=(critical_enrichment, 1.02),
        arrowprops=dict(arrowstyle="->")
    )

plt.xlabel(enrichment_cfg["xlabel"])
plt.ylabel(enrichment_cfg["ylabel"])
plt.title(enrichment_cfg["title"])
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
        f.write("OpenMC enrichment scan analysis\n")
        f.write("=" * 40 + "\n\n")
        f.write(f"Source CSV: {latest_csv}\n")
        f.write(f"Number of points: {len(enrichments)}\n")
        f.write(f"Minimum enrichment: {min(enrichments):.4f} %\n")
        f.write(f"Maximum enrichment: {max(enrichments):.4f} %\n")
        f.write(f"Minimum k-effective: {min(k_values):.6f}\n")
        f.write(f"Maximum k-effective: {max(k_values):.6f}\n\n")

        if critical_enrichment is not None:
            f.write("Critical enrichment estimation:\n")
            f.write(f"Estimated critical enrichment = {critical_enrichment:.6f} %\n")
            if crossing_interval is not None:
                f.write(
                    f"Crossing interval = [{crossing_interval[0]:.4f}, {crossing_interval[1]:.4f}] %\n"
                )
            f.write("Method: linear interpolation between adjacent points around k=1.\n")
        else:
            f.write("No critical enrichment found in current scan range.\n")
            f.write("Reason: k-effective did not cross 1.0 within the scanned range.\n")

        f.write("\nDetailed data:\n")
        f.write("Enrichment (%)\tk-effective\tuncertainty\n")
        for e, k, u in zip(enrichments, k_values, uncertainties):
            f.write(f"{e:.4f}\t{k:.6f}\t{u:.6f}\n")


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

if critical_enrichment is not None:
    print(f"估算临界富集度 = {critical_enrichment:.6f} %")
    if crossing_interval is not None:
        print(
            f"k=1 穿过区间大约在 {crossing_interval[0]:.4f}% ~ {crossing_interval[1]:.4f}%"
        )
else:
    print("当前扫描范围内没有找到 k-effective 穿过 1 的区间。")