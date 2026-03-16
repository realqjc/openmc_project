#老脚本
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
#conda activate openmc-x86 记得开始之前先运行
#现在不用了
#cmd+shift+B 自动计算 输出 保存csv与图片

import openmc  #软件使用示例

model = openmc.examples.pwr_pin_cell()
model.export_to_xml()

print("OpenMC模型生成成功")