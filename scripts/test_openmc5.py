#老脚本
import openmc  #改变燃料棒间距试验

# =========================
# 1 定义材料 (materials)
# =========================

# 定义燃料 UO2
fuel = openmc.Material(name='UO2 fuel')
fuel.add_element('U', 1.0, enrichment=3.0)  # U-235 富集度 3%
fuel.add_element('O', 2.0)                  # UO2
fuel.set_density('g/cm3', 10.29769)         # 燃料密度

# 定义包壳材料 Zircaloy
clad = openmc.Material(name='Zircaloy')
clad.add_element('Zr', 1.0)
clad.set_density('g/cm3', 6.55)

# 定义慢化剂 水
water = openmc.Material(name='Water')
water.add_element('H', 2.0)
water.add_element('O', 1.0)
water.set_density('g/cm3', 0.740582)

# 水的热散射数据
water.add_s_alpha_beta('c_H_in_H2O')

# 把材料加入材料集合
materials = openmc.Materials([fuel, clad, water])


# =========================
# 2 定义几何 (geometry)
# =========================

# 这里是本实验的关键变量
pitch = 1.80   # 燃料棒中心距 (cm)  ← 你可以改这个数

fuel_radius = 0.39     # 燃料半径
clad_radius = 0.45720  # 包壳外半径

# 定义两个圆柱面
fuel_or = openmc.ZCylinder(r=fuel_radius)
clad_or = openmc.ZCylinder(r=clad_radius)

# 定义一个方形单元边界
left   = openmc.XPlane(x0=-pitch/2, boundary_type='reflective')
right  = openmc.XPlane(x0=pitch/2,  boundary_type='reflective')
bottom = openmc.YPlane(y0=-pitch/2, boundary_type='reflective')
top    = openmc.YPlane(y0=pitch/2,  boundary_type='reflective')

# =========================
# 3 定义三个区域
# =========================

# 燃料区域
fuel_cell = openmc.Cell(fill=fuel, region=-fuel_or)

# 包壳区域
clad_cell = openmc.Cell(fill=clad, region=+fuel_or & -clad_or)

# 水区域 (慢化剂)
water_cell = openmc.Cell(
    fill=water,
    region=+clad_or & +left & -right & +bottom & -top
)

# 建立宇宙
root = openmc.Universe(cells=[fuel_cell, clad_cell, water_cell])

# 几何对象
geometry = openmc.Geometry(root)


# =========================
# 4 设置计算参数
# =========================

settings = openmc.Settings()

settings.run_mode = 'eigenvalue'  # 求 k-effective

settings.batches = 100     # 总批次数
settings.inactive = 20     # 前20批不计入统计
settings.particles = 5000  # 每批粒子数

# 定义初始中子源
settings.source = openmc.IndependentSource(
    space=openmc.stats.Box(
        [-pitch/2, -pitch/2, -1],
        [ pitch/2,  pitch/2,  1],
        only_fissionable=True
    )
)


# =========================
# 5 建立模型
# =========================

model = openmc.Model(geometry, materials, settings)

# 导出 XML 输入文件
model.export_to_xml()

print("模型生成成功")
print("当前 pin pitch =", pitch, "cm")
print("现在运行: openmc")