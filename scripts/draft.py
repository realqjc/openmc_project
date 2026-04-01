#新脚本风格统一化：
#请基于本项目现有来源文件，生成一个新的 OpenMC 扫描脚本。
# 要求参照 config_loader.py、common_paths.py、project_config.yaml 的现有约定，
# 将扫描区间参数统一交由 yaml 管理；
# 脚本自动执行区间扫描，并把结果按日期命名保存到 results/ 目录。
# 如果项目来源中已有 test_openmc6.py，请尽量沿用它的代码组织风格；
# 如果没有，就按本项目其余脚本的工程风格生成。