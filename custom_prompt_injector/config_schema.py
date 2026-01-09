"""配置 Schema 定义"""
from src.plugin_system import ConfigField

CONFIG_SCHEMA = {
    "plugin": {
        "enabled": ConfigField(
            type=bool,
            default=True,
            description="是否启用自定义提示词注入插件",
            example="true",
            hint="禁用后所有提示词将不会注入到对话系统中"
        ),
        "debug_mode": ConfigField(
            type=bool,
            default=False,
            description="是否启用调试模式，会输出详细日志",
            example="false",
            hint="调试时建议启用，可查看提示词注入的详细过程和优先级信息"
        ),
    }
}

# 配置节描述
CONFIG_SECTION_DESCRIPTIONS = {
    "plugin": "插件基础配置",
}
