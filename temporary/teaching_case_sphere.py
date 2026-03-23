# 教学案例：建立一个球形燃料-水反射层几何模型，
# 并用 OpenMC 计算其有效增殖因子 k-eff

import os
from pathlib import Path
import openmc


# ============================================================
# 1. 工作目录：全部文件都放到 temporary 文件夹
# ============================================================
WORK_DIR = Path.home() / "Desktop" / "school" / "openmc_project" / "temporary"
WORK_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# 2. 定义材料
#    教学案例：
#    - 内部：U235 燃料球
#    - 外部：轻水
# ============================================================

fuel = openmc.Material(name="U235 fuel")

# 这里决定燃料成分
# 现在是“纯 U235”教学模型。
# 以后如果你想改 k-eff，可以改这里的核素组成，
# 比如改成 U235 + U238 混合，或者改变富集度。
fuel.add_nuclide("U235", 1.0)

# 这里决定燃料密度
# 燃料密度通常会影响体系中的裂变核密度，因此会影响 k-eff。
fuel.set_density("g/cm3", 10.0)

water = openmc.Material(name="Water")

# 这里决定水的组成：H:O = 2:1
# 如果你以后把轻水改成别的慢化剂，也会影响 k-eff。
water.add_nuclide("H1", 2.0)
water.add_nuclide("O16", 1.0)

# 水密度也会影响慢化效果，因此会影响 k-eff。
water.set_density("g/cm3", 1.0)

# 轻水热散射处理
# 这会影响热中子区的物理处理结果，也可能影响 k-eff。
water.add_s_alpha_beta("c_H_in_H2O")

materials = openmc.Materials([fuel, water])


# ============================================================
# 3. 定义几何
#    对应教学图：
#    球内 fuel，球外且盒内 water，盒边界是真空
# ============================================================

# 燃料球半径
# 这是最重要的几何参数之一。
# 改大：燃料体积增大，通常会明显影响 k-eff。
sphere = openmc.Sphere(r=9.0)

# 最外层真空边界盒
# 这里决定“水层有多厚”以及整个计算区域有多大。
# 盒子越大，在燃料球半径不变时，外部水层越厚，
# 慢化/反射条件会改变，因此也会影响 k-eff。
box = openmc.model.RectangularParallelepiped(
    -50.0, 50.0,   # x_min, x_max
    -50.0, 50.0,   # y_min, y_max
    -50.0, 50.0,   # z_min, z_max
    boundary_type="vacuum"   # 真空边界：粒子离开后不再返回
)

# 球内部：燃料区
fuel_cell = openmc.Cell(
    fill=fuel,
    region=-sphere   # -sphere 表示球内
)

# 球外且盒内：水区
water_cell = openmc.Cell(
    fill=water,
    region=+sphere & -box   # +sphere 表示球外；-box 表示盒内
)

root = openmc.Universe(cells=[fuel_cell, water_cell])
geometry = openmc.Geometry(root)


# ============================================================
# 4. 定义计算参数
# ============================================================

settings = openmc.Settings()

# 本题是本征值计算，也就是求 k-eff
settings.run_mode = "eigenvalue"

# 总批次数
# 这不会真正改变物理上的 k-eff，
# 但会影响统计精度和结果稳定性。
settings.batches = 50

# 非活跃批次数
# 这些批次用于让裂变源分布逐渐收敛，
# 不计入最终统计结果。
# 它本身不改变真实 k-eff，但会影响结果是否可靠。
settings.inactive = 10

# 每批粒子数
# 这也主要影响统计误差，不直接改变真实 k-eff。
# 粒子数越大，结果通常越稳定，但计算更慢。
settings.particles = 9000

# 初始源放在原点
# 对这个简单模型来说，初始源通常不会改变最终收敛后的 k-eff，
# 但会影响前几代的收敛速度。
settings.source = openmc.IndependentSource(
    space=openmc.stats.Point((0.0, 0.0, 0.0))
)


# ============================================================
# 5. 切换到 temporary，并导出 XML
# ============================================================
os.chdir(WORK_DIR)

materials.export_to_xml()
geometry.export_to_xml()
settings.export_to_xml()

print("=" * 60)
print("当前工作目录：")
print(WORK_DIR)
print("\n已导出输入文件：")
print("  - materials.xml")
print("  - geometry.xml")
print("  - settings.xml")
print("=" * 60)


# ============================================================
# 6. 运行 OpenMC
# ============================================================
print("\n开始运行 OpenMC...\n")
openmc.run(cwd=str(WORK_DIR))
print("\nOpenMC 运行完成。")


# ============================================================
# 7. 读取最新 statepoint 文件并打印 keff
# ============================================================
statepoint_files = sorted(WORK_DIR.glob("statepoint.*.h5"))

if not statepoint_files:
    print("没有找到 statepoint 文件，无法读取结果。")
else:
    latest_sp = statepoint_files[-1]
    print(f"\n读取结果文件：{latest_sp.name}")

    with openmc.StatePoint(latest_sp) as sp:
        print("\n========== 计算结果 ==========")
        print(f"k-effective = {sp.keff}")
        print("==============================")

print("\n结果文件都保存在：")
print(WORK_DIR)