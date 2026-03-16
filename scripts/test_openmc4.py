#老脚本
import openmc  #燃料半径试验

# ===== 1. 材料 =====
fuel = openmc.Material(name='UO2 fuel')
fuel.add_element('U', 1.0, enrichment=3.0)
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

# ===== 2. 几何 =====
pitch = 1.26

fuel_radius = 0.44      # 这里改燃料半径
clad_radius = 0.45720   # 包壳外半径先保持不变

fuel_or = openmc.ZCylinder(r=fuel_radius)
clad_or = openmc.ZCylinder(r=clad_radius)

left = openmc.XPlane(x0=-pitch/2, boundary_type='reflective')
right = openmc.XPlane(x0=pitch/2, boundary_type='reflective')
bottom = openmc.YPlane(y0=-pitch/2, boundary_type='reflective')
top = openmc.YPlane(y0=pitch/2, boundary_type='reflective')

fuel_cell = openmc.Cell(fill=fuel, region=-fuel_or)
clad_cell = openmc.Cell(fill=clad, region=+fuel_or & -clad_or)
water_cell = openmc.Cell(fill=water, region=+clad_or & +left & -right & +bottom & -top)

root = openmc.Universe(cells=[fuel_cell, clad_cell, water_cell])
geometry = openmc.Geometry(root)

# ===== 3. 设置 =====
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

# ===== 4. 建模并导出 =====
model = openmc.Model(geometry, materials, settings)
model.export_to_xml()

print(f"模型已生成：fuel radius = {fuel_radius} cm")
print("现在运行：openmc")