# test_openmc6.py（pitch scan）
# 改变燃料棒间距试验 -- 自动扫描 -- 寻找最佳 pin pitch
# 已按 test_openmc7.py 的规格加入路径管理：
# 1. results/pitch_scan/ 保存 CSV 和 PNG
# 2. statepoints/pitch_scan/ 保存运行产生的 h5 文件
# 3. 每个 pitch 单独一个运行子文件夹
# 4. model.xml 自动移动到 input/ 文件夹

import csv
import shutil
from datetime import datetime

import matplotlib.pyplot as plt
import numpy as np
import openmc

from common_paths import INPUT_DIR, make_scan_dirs, working_directory
from config_loader import load_config

# 为 pitch 扫描创建专属结果目录和状态文件目录
RESULT_DIR, STATEPOINT_DIR = make_scan_dirs("pitch_scan")

config = load_config()

pitch_cfg = config["pitch_scan"]
settings_cfg = config["settings"]
geometry_cfg = config["geometry"]

timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
plot_path = RESULT_DIR / f"keff_pitch_{timestamp}.png"
csv_path = RESULT_DIR / f"pitch_keff_results_{timestamp}.csv"

# 要测试的 pin pitch 列表（单位：cm）
pitch_list = np.arange(
    pitch_cfg["start"],
    pitch_cfg["stop"] + pitch_cfg["step"] / 2,
    pitch_cfg["step"]
)

# 保存结果
results = []

# =========================
# 参数扫描循环
# =========================
for pitch in pitch_list:
    # =========================
    # 1. 定义材料
    # =========================
    fuel = openmc.Material(name="UO2 fuel")
    fuel.add_element("U", 1.0, enrichment=pitch_cfg["fixed_enrichment"])
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

    # =========================
    # 2. 定义几何
    # =========================
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

    # =========================
    # 3. 定义计算设置
    # =========================
    settings = openmc.Settings()
    settings.run_mode = "eigenvalue"
    settings.batches = settings_cfg["batches"]
    settings.inactive = settings_cfg["inactive"]
    settings.particles = settings_cfg["particles"]

    # 与 test_openmc7.py 风格保持一致
    settings.source = openmc.IndependentSource(
        space=openmc.stats.Box(
            [-pitch / 2, -pitch / 2, -1],
            [pitch / 2, pitch / 2, 1],
            only_fissionable=True
        )
    )

    # =========================
    # 4. 建模并运行
    # =========================
    model = openmc.Model(geometry, materials, settings)

    print(f"正在计算 pitch = {pitch:.2f} cm")

    # 每一个 pitch 都放到自己的子文件夹中运行
    run_dir = STATEPOINT_DIR / f"pitch_{pitch:.2f}"
    run_dir.mkdir(parents=True, exist_ok=True)

    with working_directory(run_dir):
        sp_filename = model.run()

    # 如果 model.xml 在运行目录中生成，就移动到 input 文件夹
    generated_model_xml = run_dir / "model.xml"
    target_model_xml = INPUT_DIR / "model.xml"
    if generated_model_xml.exists():
        shutil.move(str(generated_model_xml), str(target_model_xml))

    # 读取 statepoint 结果文件
    with openmc.StatePoint(sp_filename) as sp:
        keff = sp.keff

    # 保存结果
    results.append((pitch, keff.nominal_value, keff.std_dev))

# =========================
# 5. 打印最终结果表
# =========================
print("\n=== 计算结果 ===")
print("Pitch (cm)    Combined k-effective")
for pitch, k, err in results:
    print(f"{pitch:<12.2f} {k:.5f} +/- {err:.5f}")

# =========================
# 6. 自动找最大 k-effective
# =========================
best_result = max(results, key=lambda x: x[1])
best_pitch, best_k, best_err = best_result

print("\n=== 最佳结果 ===")
print(f"最佳 pitch = {best_pitch:.2f} cm")
print(f"最大 Combined k-effective = {best_k:.5f} +/- {best_err:.5f}")

# =========================
# 7. 画图
# =========================
pitch_values = [item[0] for item in results]
k_values = [item[1] for item in results]

plt.figure(figsize=(8, 5))
plt.plot(pitch_values, k_values, marker="o")
plt.xlabel("Pin pitch (cm)")
plt.ylabel("Combined k-effective")
plt.title("k-effective vs Pin Pitch")
plt.grid(True)

# 标出最大值点
plt.scatter([best_pitch], [best_k], s=80)
plt.annotate(
    f"Max: ({best_pitch:.2f}, {best_k:.5f})",
    xy=(best_pitch, best_k),
    xytext=(best_pitch + 0.10, best_k - 0.015),
    arrowprops=dict(arrowstyle="->")
)

plt.savefig(plot_path, dpi=300, bbox_inches="tight")
plt.show()

# =========================
# 8. 保存结果为 CSV 文件
# =========================
with open(csv_path, "w", newline="") as f:
    writer = csv.writer(f)

    # 写表头
    writer.writerow(["Pitch (cm)", "k-effective", "uncertainty"])

    # 写数据
    for pitch, k, err in results:
        writer.writerow([pitch, k, err])

print(f"\n结果已保存为 {csv_path}")
print(f"图像已保存为 {plot_path}")
print(f"状态文件目录为 {STATEPOINT_DIR}")
print(f"输入文件目录为 {INPUT_DIR}")