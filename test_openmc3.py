import openmc   #富集度试验

model = openmc.examples.pwr_pin_cell()

fuel = model.materials[0]
fuel.nuclides.clear()
fuel.add_element('U', 1.0, enrichment=2.0)
fuel.add_element('O', 2.0)
fuel.set_density('g/cm3', 10.29769)

model.settings.batches = 100
model.settings.inactive = 20
model.settings.particles = 5000

model.export_to_xml()

print("模型已生成，现在可以运行 openmc 计算")