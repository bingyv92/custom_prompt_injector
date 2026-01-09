from src.plugin_system.base.plugin_metadata import PluginMetadata

__plugin_meta__ = PluginMetadata(
    name="自定义提示词注入插件",
    description="适用于mofox的自定义插入提示词的插件",
    usage="支持多个自定义提示词注入到 MoFox_Bot 的 KFC/AFC 对话系统中，灵活控制提示词的注入位置、优先级和适用场景。",
    version="1.0.0",
    author="bingyv92",
    license="MIT",
    repository_url="https://github.com/bingyv92/custom_prompt_injector",
)
