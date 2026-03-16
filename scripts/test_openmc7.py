# test_openmc7.py
# enrichment scan
# 改变燃料富集度试验 -- 自动扫描 -- 寻找临界点
# 已按 test_openmc6.py / project_config.yaml 规格改造：
# 1. results/enrichment_scan/ 保存 CSV 和 PNG
# 2. statepoints/enrichment_scan/ 保存运行产生的 h5 文件
# 3. 每个 enrichment 单独一个运行子文件夹
# 4. model.xml 自动移动到 input/ 文件夹
# 5. 扫描参数和 OpenMC 设置从 project_config.yaml 读取

import csv
import shutil
from datetime import datetime

import matplotlib.pyplot as plt
import numpy as np
import openmc

from common_paths import INPUT_DIR, make_scan_dirs, working_directory
from config_loader import load_config

# 为富集度扫描创建专属结果目录和状态文件目录
RESULT_DIR, STATEPOINT_DIR = make_scan_dirs("enrichment_scan")

# 读取配置文件
config = load_config()

enrichment_cfg = config["enrichment_scan"]
settings_cfg = config["settings"]
geometry_cfg = config["geometry"]

timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
plot_path = RESULT_DIR / f"keff_enrichment_{timestamp}.png"
csv_path = RESULT_DIR / f"enrichment_keff_results_{timestamp}.csv"

# =========================
# 1. 扫描的富集度范围 (%)
# =========================
enrichment_list = np.arange(
    enrichment_cfg["start"],
    enrichment_cfg["stop"] + enrichment_cfg["step"] / 2,
    enrichment_cfg["step"]
)

results = []

# =========================
# 2. 参数扫描循环
# =========================
for enrichment in enrichment_list:

    # -------------------------
    # 材料
    # -------------------------
    fuel = openmc.Material(name="UO2 fuel")
    fuel.add_element("U", 1.0, enrichment=enrichment)
    fuel.add_element("O", 2.0)
    fuel.set_density("g/cm3", 10.29769)

    clad = openmc.Material(name="Zircaloy")
    clad.add_element("Zr", 1.0)
    clad.set_density("g/cm3", 6.55)

    water = openmc.Material(name="Water")
    water.add_element("H", 2.0)
    water.add_element("O", 1.0)
    water.set_density("g/cm3", 0.740582)
    water.add_s_alpha_beta("c_H_in_H2O")

    materials = openmc.Materials([fuel, clad, water])

    # -------------------------
    # 几何
    # -------------------------
    pitch = enrichment_cfg["fixed_pitch"]
    fuel_radius = geometry_cfg["fuel_radius"]
    clad_radius = geometry_cfg["clad_radius"]

    fuel_or = openmc.ZCylinder(r=fuel_radius)
    clad_or = openmc.ZCylinder(r=clad_radius)

    left = openmc.XPlane(x0=-pitch / 2, boundary_type="reflective")
    right = openmc.XPlane(x0=pitch / 2, boundary_type="reflective")
    bottom = openmc.YPlane(y0=-pitch / 2, boundary_type="reflective")
    top = openmc.YPlane(y0=pitch / 2, boundary_type="reflective")

    fuel_cell = openmc.Cell(fill=fuel, region=-fuel_or)
    clad_cell = openmc.Cell(fill=clad, region=+fuel_or & -clad_or)
    water_cell = openmc.Cell(
        fill=water,
        region=+clad_or & +left & -right & +bottom & -top
    )

    root = openmc.Universe(cells=[fuel_cell, clad_cell, water_cell])
    geometry = openmc.Geometry(root)

    # -------------------------
    # 计算设置
    # -------------------------
    settings = openmc.Settings()
    settings.run_mode = "eigenvalue"
    settings.batches = settings_cfg["batches"]
    settings.inactive = settings_cfg["inactive"]
    settings.particles = settings_cfg["particles"]

    settings.source = openmc.IndependentSource(
        space=openmc.stats.Box(
            [-pitch / 2, -pitch / 2, -1],
            [pitch / 2, pitch / 2, 1],
            only_fissionable=True
        )
    )

    # -------------------------
    # 建模并运行
    # -------------------------
    model = openmc.Model(geometry, materials, settings)

    print(f"正在计算 enrichment = {enrichment:.2f}%")

    # 每一个富集度都放到自己的子文件夹中运行
    run_dir = STATEPOINT_DIR / f"enrichment_{enrichment:.2f}"
    run_dir.mkdir(parents=True, exist_ok=True)

    with working_directory(run_dir):
        sp_filename = model.run()

    # 如果 model.xml 在运行目录中生成，就移动到 input 文件夹
    generated_model_xml = run_dir / "model.xml"
    target_model_xml = INPUT_DIR / "model.xml"
    if generated_model_xml.exists():
        shutil.move(str(generated_model_xml), str(target_model_xml))

    # 读取 statepoint 结果
    with openmc.StatePoint(sp_filename) as sp:
        keff = sp.keff

    results.append((enrichment, keff.nominal_value, keff.std_dev))

# =========================
# 3. 输出结果
# =========================
print("\n=== 计算结果 ===")
print("Enrichment (%)    Combined k-effective")
for e, k, err in results:
    print(f"{e:<15.2f} {k:.5f} +/- {err:.5f}")

# =========================
# 4. 估算临界富集度
# =========================
critical_enrichment = None

for i in range(len(results) - 1):
    e1, k1, err1 = results[i]
    e2, k2, err2 = results[i + 1]

    if k1 == 1.0:
        critical_enrichment = e1
        break

    if (k1 - 1.0) * (k2 - 1.0) < 0:
        critical_enrichment = e1 + (1.0 - k1) * (e2 - e1) / (k2 - k1)
        break

print("\n=== 临界富集度估算 ===")
if critical_enrichment is not None:
    print(f"估算临界富集度 = {critical_enrichment:.4f} %")
else:
    print("在当前扫描范围内，没有找到 k-effective 穿过 1 的区间")

# =========================
# 5. 绘图
# =========================
enrichments = [r[0] for r in results]
k_values = [r[1] for r in results]

plt.figure(figsize=(8, 5))
plt.plot(enrichments, k_values, marker="o")
plt.xlabel("U-235 enrichment (%)")
plt.ylabel("Combined k-effective")
plt.title("k-effective vs Enrichment")
plt.grid(True)
plt.savefig(plot_path, dpi=300, bbox_inches="tight")
plt.show()

# =========================
# 6. 保存 CSV
# =========================
with open(csv_path, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Enrichment (%)", "k-effective", "uncertainty"])
    for e, k, err in results:
        writer.writerow([e, k, err])

print(f"\n结果已保存为 {csv_path}")
print(f"图像已保存为 {plot_path}")
print(f"状态文件目录为 {STATEPOINT_DIR}")
print(f"输入文件目录为 {INPUT_DIR}")