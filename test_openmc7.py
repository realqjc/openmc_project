import openmc  #改变燃料棒间距试验--自动扫描
import numpy as np
import matplotlib.pyplot as plt
import csv

# =========================
# 1 扫描的富集度范围 (%)
# =========================

enrichment_list = np.arange(0.2, 2.1, 0.1)

results = []

# =========================
# 2 参数扫描循环
# =========================

for enrichment in enrichment_list:

    # -------- 材料 --------

    fuel = openmc.Material(name='UO2 fuel')
    fuel.add_element('U', 1.0, enrichment=enrichment)
    fuel.add_element('O', 2.0)
    fuel.set_density('g/cm3', 10.29769)

    clad = openmc.Material(name='Zircaloy')
    clad.add_element('Zr', 1.0)
    clad.set_density('g/cm3', 6.55)

    water = openmc.Material(name='Water')
    water.add_element('H', 2.0)
    water.add_element('O', 1.0)
    water.set_density('g/cm3', 0.740582)
    water.add_s_alpha_beta('c_H_in_H2O')

    materials = openmc.Materials([fuel, clad, water])

    # -------- 几何 --------

    pitch = 1.50

    fuel_radius = 0.39
    clad_radius = 0.45720

    fuel_or = openmc.ZCylinder(r=fuel_radius)
    clad_or = openmc.ZCylinder(r=clad_radius)

    left = openmc.XPlane(x0=-pitch/2, boundary_type='reflective')
    right = openmc.XPlane(x0=pitch/2, boundary_type='reflective')
    bottom = openmc.YPlane(y0=-pitch/2, boundary_type='reflective')
    top = openmc.YPlane(y0=pitch/2, boundary_type='reflective')

    fuel_cell = openmc.Cell(fill=fuel, region=-fuel_or)
    clad_cell = openmc.Cell(fill=clad, region=+fuel_or & -clad_or)

    water_cell = openmc.Cell(
        fill=water,
        region=+clad_or & +left & -right & +bottom & -top
    )

    root = openmc.Universe(cells=[fuel_cell, clad_cell, water_cell])
    geometry = openmc.Geometry(root)

    # -------- 计算设置 --------

    settings = openmc.Settings()
    settings.run_mode = 'eigenvalue'

    settings.batches = 100
    settings.inactive = 20
    settings.particles = 5000

    settings.source = openmc.IndependentSource(
        space=openmc.stats.Box(
            [-pitch/2, -pitch/2, -1],
            [pitch/2, pitch/2, 1],
            only_fissionable=True
        )
    )

    # -------- 运行 --------

    model = openmc.Model(geometry, materials, settings)

    print(f"正在计算 enrichment = {enrichment:.2f}%")

    sp_filename = model.run()

    with openmc.StatePoint(sp_filename) as sp:
        keff = sp.keff

    results.append((enrichment, keff.nominal_value, keff.std_dev))


# =========================
# 3 打印结果
# =========================

print("\n=== 计算结果 ===")
print("Enrichment (%)    Combined k-effective")

for e, k, err in results:
    print(f"{e:<15.2f} {k:.5f} +/- {err:.5f}")

# =========================
# 4额外添加： 自动估算临界富集度
# =========================

critical_enrichment = None

# 逐段检查 k-effective 是否跨过 1.0
for i in range(len(results) - 1):
    e1, k1, err1 = results[i]
    e2, k2, err2 = results[i + 1]

    # 如果刚好等于 1
    if k1 == 1.0:
        critical_enrichment = e1
        break

    # 如果在这一段里跨过了 1
    if (k1 - 1.0) * (k2 - 1.0) < 0:
        # 线性插值公式
        critical_enrichment = e1 + (1.0 - k1) * (e2 - e1) / (k2 - k1)
        break

# 打印结果
print("\n=== 临界富集度估算 ===")
if critical_enrichment is not None:
    print(f"估算临界富集度 = {critical_enrichment:.4f} %")
else:
    print("在当前扫描范围内，没有找到 k-effective 穿过 1 的区间")


# =========================
# 5 画图
# =========================

enrichments = [r[0] for r in results]
k_values = [r[1] for r in results]

plt.plot(enrichments, k_values, marker='o')
plt.xlabel("U-235 enrichment (%)")
plt.ylabel("Combined k-effective")
plt.title("k-effective vs Enrichment")
plt.grid(True)

plt.show()


# =========================
# 6 保存CSV
# =========================

with open("enrichment_keff_results.csv", "w", newline="") as f:

    writer = csv.writer(f)

    writer.writerow(["Enrichment (%)", "k-effective", "uncertainty"])

    for e, k, err in results:
        writer.writerow([e, k, err])

print("\n结果已保存为 enrichment_keff_results.csv")