import openmc  #富集度试验

# 生成PWR单燃料棒模型
model = openmc.examples.pwr_pin_cell()

# 取出燃料材料
fuel = model.materials[0]

# 清空原有核素
fuel.nuclides.clear()

# 设置新的燃料组成（U-235富集度 3%）
fuel.add_element('U', 1.0, enrichment=3.0)
fuel.add_element('O', 2.0)

# 设置燃料密度
fuel.set_density('g/cm3', 10.29769)

# 导出XML输入文件
model.export_to_xml()

print("模型已生成，现在可以运行 openmc 计算")