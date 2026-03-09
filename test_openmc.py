"""
OpenMC Reactor Physics Study

Experiments included:
1. Enrichment effect
2. Fuel radius effect
3. Pin pitch effect
4. Critical enrichment estimation

Author: 邱俊诚
Course: 核反应堆技术
"""

import openmc  #软件使用示例

model = openmc.examples.pwr_pin_cell()
model.export_to_xml()

print("OpenMC模型生成成功")