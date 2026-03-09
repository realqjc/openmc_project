import openmc  #改变燃料棒间距试验--自动扫描
import numpy as np
import matplotlib.pyplot as plt
import csv

# 要测试的 pin pitch 列表（单位：cm）
import numpy as np

pitch_list = np.arange(1.00, 2.01, 0.05) #从 1.00 cm 开始到 2.00 cm 结束每次加 0.05 cm

# 用来保存结果
results = []

# 逐个 pitch 进行计算
for pitch in pitch_list:
    # =========================
    # 1. 定义材料
    # =========================
    fuel = openmc.Material(name='UO2 fuel')
    fuel.add_element('U', 1.0, enrichment=3.0)   # U-235 富集度 3%
    fuel.add_element('O', 2.0)                   # UO2
    fuel.set_density('g/cm3', 10.29769)          # 燃料密度

    clad = openmc.Material(name='Zircaloy')
    clad.add_element('Zr', 1.0)
    clad.set_density('g/cm3', 6.55)

    water = openmc.Material(name='Water')
    water.add_element('H', 2.0)
    water.add_element('O', 1.0)
    water.set_density('g/cm3', 0.740582)
    water.add_s_alpha_beta('c_H_in_H2O')

    materials = openmc.Materials([fuel, clad, water])

    # =========================
    # 2. 定义几何
    # =========================
    fuel_radius = 0.39
    clad_radius = 0.45720

    fuel_or = openmc.ZCylinder(r=fuel_radius)
    clad_or = openmc.ZCylinder(r=clad_radius)

    left   = openmc.XPlane(x0=-pitch/2, boundary_type='reflective')
    right  = openmc.XPlane(x0= pitch/2, boundary_type='reflective')
    bottom = openmc.YPlane(y0=-pitch/2, boundary_type='reflective')
    top    = openmc.YPlane(y0= pitch/2, boundary_type='reflective')

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
    settings.run_mode = 'eigenvalue'
    settings.batches = 100
    settings.inactive = 20
    settings.particles = 5000

    settings.source = openmc.IndependentSource(
        space=openmc.stats.Box(
            [-pitch/2, -pitch/2, -1],
            [ pitch/2,  pitch/2,  1],
            only_fissionable=True
        )
    )

    # =========================
    # 4. 建模并运行
    # =========================
    model = openmc.Model(geometry, materials, settings)

    print(f'正在计算 pitch = {pitch} cm ...')
    sp_filename = model.run()

    # 读取 statepoint 结果文件
    with openmc.StatePoint(sp_filename) as sp:
        keff = sp.keff

    # 保存结果
    results.append((pitch, keff.nominal_value, keff.std_dev))

# =========================
# 5. 打印最终结果表
# =========================
print('\n=== 计算结果 ===')
print('Pitch (cm)    Combined k-effective')

for pitch, k, err in results:
    print(f'{pitch:<12.2f} {k:.5f} +/- {err:.5f}')

# =========================
# 6. 自动找最大 k-effective
# =========================
best_result = max(results, key=lambda x: x[1])
best_pitch, best_k, best_err = best_result

print('\n=== 最佳结果 ===')
print(f'最佳 pitch = {best_pitch:.2f} cm')
print(f'最大 Combined k-effective = {best_k:.5f} +/- {best_err:.5f}')

# =========================
# 7. 画图
# =========================
pitch_values = [item[0] for item in results]
k_values = [item[1] for item in results]

plt.plot(pitch_values, k_values, marker='o')
plt.xlabel('Pin pitch (cm)')
plt.ylabel('Combined k-effective')
plt.title('k-effective vs Pin Pitch')
plt.grid(True)

# 标出最大值点
plt.scatter([best_pitch], [best_k], s=80)
plt.annotate(
    f'Max: ({best_pitch:.2f}, {best_k:.5f})',
    xy=(best_pitch, best_k),
    xytext=(best_pitch + 0.10, best_k - 0.015),
    arrowprops=dict(arrowstyle='->')
)

plt.show()

# =========================
# 8. 保存结果为 CSV 文件
# =========================

with open("pitch_keff_results.csv", "w", newline="") as f:
    writer = csv.writer(f)

    # 写表头
    writer.writerow(["Pitch (cm)", "Combined k-effective", "Uncertainty"])

    # 写数据
    for pitch, k, err in results:
        writer.writerow([pitch, k, err])

print("\n结果已保存为 pitch_keff_results.csv")