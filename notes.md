“”“
# tasks.json能干什么3/14
”“”
1️⃣ Run Pitch Scan
2️⃣ Run Enrichment Scan
3️⃣ Analyze All Results
4️⃣ Clean Old Statepoints
5️⃣ Run Full Reactor Study
# 如何使用：shift+command+B会弹出
Run Pitch Scan
Run Enrichment Scan
Analyze All Results
Clean Old Statepoints
Run Full Reactor Study
选一个回车即可运行


# project_config.yaml是啥
改扫描范围、步长、批次数、粒子数的配置文件

# config_loader.py是读取配置的工具
# run_full_reactor_study.py是总控脚本，决定6.py和7.py哪个要跑哪个不跑

文件	                              作用
README.md	                         项目简介
README_Project_Workflow.md	         运行流程
project_structure.md	             结构说明

# # # # # # # # # # # # #日常工作流程workflow：# # # # # # # # # # # # # 
先改配置

改 project_config.yaml：

扫描范围

步长

是否启用 pitch / enrichment

是否显示图

是否保存报告

再按一次快捷键

在 VS Code 按：

⌘ + ⇧ + B

选：

Run Full Reactor Study
然后看结果

输出会自动去：

results/pitch_scan/

results/enrichment_scan/

results/.../analysis/

# 需要时再用clean_old_statepoints 清理老的statepoints文件






#每次写新脚本的固定模板:新脚本开头统一写:
from common_paths import INPUT_DIR, make_scan_dirs, working_directory
from datetime import datetime

RESULT_DIR, STATEPOINT_DIR = make_scan_dirs("任务名字")

timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
#
#
#
#
#每次运行 OpenMC 的标准流程:在脚本里必须做到三件事：
#
#1、生成运行目录:statepoints/任务名/参数值/
#例如：statepoints/enrichment_scan/enrichment_0.20/
#statepoints/enrichment_scan/enrichment_0.30/
#
#2、在运行目录执行 openmc
#with working_directory(run_dir):
#    sp_filename = model.run()
#
#3 保存结果文件
#统一保存到：results/任务名/
#例如：results/enrichment_scan/
#    enrichment_keff_2026-03-14_193500.csv
#    keff_enrichment_2026-03-14_193500.png
#
#
#
#
#
#
#每次运行仿真前的检查清单
#1、目录结构正常
#2 脚本里有时间戳
#3 参数扫描范围合理
#4 OpenMC环境正确
#
#
#
#
#
#每次仿真完成后的操作
#1 看 CSV
#2 看 PNG
#3 删除无用 statepoints（定期）
#
#
#
#
#ChatGPT 使用方式（非常重要）
#建立一个 ChatGPT Project
#名字：OpenMC reactor simulation
#放进去：
#common_paths.py
#scan脚本
#项目目录说明
#
#每次新问题 新开对话并给简短背景：
#我的项目结构：

#openmc_project
#scripts
#input
#results
#statepoints
#
#我现在在做 enrichment 扫描
#
#
#
#
#什么时候用
#用 ChatGPT：代码结构设计、调试、理论问题、数据分析
#
#用 codeX：批量改脚本、重构项目、自动改路径、自动生成脚本
#

