"""自定义提示词注入插件 - 元数据定义"""
from src.plugin_system.base.plugin_metadata import PluginMetadata

__plugin_meta__ = PluginMetadata(
    name="自定义提示词注入插件",
    description="支持多个自定义提示词注入到 KFC/AFC 系统中，灵活控制注入位置和优先级",
    usage="在配置文件中定义 [[prompts]] 配置节，设置提示词内容和注入规则",
    version="1.0.0",
    author="MoFox Studio",
    license="MIT",
    keywords=["提示词", "KFC", "AFC", "自定义", "注入"],
    categories=["增强", "提示词"],
    dependencies=[],
    python_dependencies=[],
)
