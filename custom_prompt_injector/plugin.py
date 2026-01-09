"""自定义提示词注入插件主模块"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from typing import ClassVar, Any
from src.plugin_system import BasePlugin, register_plugin, ComponentInfo, BasePrompt
from src.plugin_system.base.component_types import PromptInfo
from src.common.logger import get_logger
from components.prompts import create_custom_prompt_class
from config_schema import CONFIG_SCHEMA, CONFIG_SECTION_DESCRIPTIONS

logger = get_logger("custom_prompt_injector")


@register_plugin
class CustomPromptInjectorPlugin(BasePlugin):
    """自定义提示词注入插件
    
    支持多个自定义提示词注入到 KFC/AFC 系统中，
    每个提示词可独立配置注入目标和优先级。
    """
    
    plugin_name = "custom_prompt_injector"
    enable_plugin = True
    dependencies = []
    python_dependencies = []
    config_file_name = "config.toml"
    
    # 配置 Schema（使用 ClassVar 声明类变量）
    config_schema: ClassVar[dict[str, dict[str, any] | str]] = CONFIG_SCHEMA  # type: ignore
    config_section_descriptions: ClassVar[dict[str, str]] = CONFIG_SECTION_DESCRIPTIONS
    
    def _synchronize_config(
        self, schema_config: dict[str, Any], user_config: dict[str, Any]
    ) -> tuple[dict[str, Any], bool]:
        """重写配置同步方法，保留 prompts 字段（TOML 数组表格式）"""
        changed = False
        
        # 内部递归函数（复制自基类，修改以跳过 prompts 字段）
        def _sync_dicts(schema_dict: dict[str, Any], user_dict: dict[str, Any], parent_key: str = "") -> dict[str, Any]:
            nonlocal changed
            synced_dict = schema_dict.copy()
            
            # 检查并记录用户配置中多余的、在 schema 中不存在的键
            # 修改：跳过 prompts 字段（顶层配置）
            for key in user_dict:
                if key not in schema_dict and key != "prompts":  # 跳过 prompts
                    logger.warning(f"{self.log_prefix} 发现废弃配置项 '{parent_key}{key}'，将被移除。")
                    changed = True
            
            # 以 schema 为基准进行遍历，保留用户的值，补全缺失的项
            for key, schema_value in schema_dict.items():
                full_key = f"{parent_key}{key}"
                if key in user_dict:
                    user_value = user_dict[key]
                    if isinstance(schema_value, dict) and isinstance(user_value, dict):
                        # 递归同步嵌套的字典
                        synced_dict[key] = _sync_dicts(schema_value, user_value, f"{full_key}.")
                    else:
                        # 键存在，保留用户的值
                        synced_dict[key] = user_value
                else:
                    # 键在用户配置中缺失，补全
                    logger.info(f"{self.log_prefix} 补全缺失的配置项: '{full_key}' = {schema_value}")
                    changed = True
            
            return synced_dict
        
        final_config = _sync_dicts(schema_config, user_config)
        
        # 如果用户配置中存在 prompts 字段，保留它（不受 schema 限制）
        if "prompts" in user_config:
            final_config["prompts"] = user_config["prompts"]
            logger.info(f"{self.log_prefix} 保留 [[prompts]] 配置（共 {len(user_config['prompts'])} 项）")
        
        return final_config, changed
    
    def _save_config_to_file(self, config_data: dict[str, Any], config_file_path: str):
        """重写配置保存方法，追加 [[prompts]] 数组表"""
        # 先调用基类方法保存标准配置
        super()._save_config_to_file(config_data, config_file_path)
        
        # 如果配置数据中包含 prompts，追加到文件末尾
        if "prompts" in config_data and isinstance(config_data["prompts"], list):
            try:
                import toml
                
                # 读取现有配置（基类已写入）
                with open(config_file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                # 追加 [[prompts]] 数组表
                with open(config_file_path, "a", encoding="utf-8") as f:
                    f.write("\n")
                    f.write("# ========================================\n")
                    f.write("# 提示词注入配置（支持多个）\n")
                    f.write("# 每个 [[prompts]] 代表一个独立的提示词注入配置\n")
                    f.write("# ========================================\n\n")
                    
                    # 将 prompts 数组序列化为 TOML 格式
                    prompts_dict = {"prompts": config_data["prompts"]}
                    prompts_toml = toml.dumps(prompts_dict)
                    f.write(prompts_toml)
                
                logger.info(f"{self.log_prefix} 已追加 [[prompts]] 配置到文件")
            except Exception as e:
                logger.error(f"{self.log_prefix} 追加 [[prompts]] 配置失败: {e}", exc_info=True)
    
    def __init__(self, *args, **kwargs):
        """插件初始化"""
        super().__init__(*args, **kwargs)
        self._prompt_components = []
        self._load_prompt_configs()
    
    def _load_prompt_configs(self):
        """从配置文件加载提示词配置"""
        try:
            # 获取原始配置（未处理的完整 TOML）
            raw_config = self.config
            
            # 提取 [[prompts]] 数组
            prompts_config = raw_config.get("prompts", [])
            
            if not isinstance(prompts_config, list):
                logger.warning("配置文件中的 'prompts' 不是数组格式，请使用 [[prompts]] 语法")
                return
            
            if not prompts_config:
                logger.info("未配置任何提示词，插件将不注册任何组件")
                return
            
            logger.info(f"从配置文件读取到 {len(prompts_config)} 个提示词配置")
            
            # 为每个提示词配置创建组件类
            for index, prompt_config in enumerate(prompts_config, start=1):
                try:
                    prompt_class = create_custom_prompt_class(prompt_config, index)
                    if prompt_class:
                        self._prompt_components.append(prompt_class)
                except Exception as e:
                    name = prompt_config.get("name", f"prompt_{index}")
                    logger.error(f"创建提示词组件 '{name}' 失败: {e}", exc_info=True)
            
            logger.info(f"成功创建 {len(self._prompt_components)} 个提示词组件")
            
        except Exception as e:
            logger.error(f"加载提示词配置失败: {e}", exc_info=True)
    
    def get_plugin_components(self):
        """返回插件包含的组件列表（动态生成）"""
        # 检查插件是否启用
        if not self.get_config("plugin.enabled", True):
            logger.info("插件未启用，不注册任何组件")
            return []
        
        # 返回动态创建的提示词组件
        components = []
        for prompt_class in self._prompt_components:
            try:
                prompt_info = prompt_class.get_prompt_info()
                components.append((prompt_info, prompt_class))
            except Exception as e:
                logger.error(f"获取提示词组件信息失败: {e}", exc_info=True)
        
        logger.info(f"注册 {len(components)} 个提示词组件到插件系统")
        return components
    
    def _generate_and_save_default_config(self, config_file_path: str):
        """重写配置文件生成方法，生成包含示例的默认配置"""
        # 先使用基类方法生成基础配置（plugin 节）
        super()._generate_and_save_default_config(config_file_path)
        
        # 追加示例 [[prompts]] 配置节
        try:
            with open(config_file_path, "a", encoding="utf-8") as f:
                f.write("\n\n")
                f.write("# ========================================\n")
                f.write("# 提示词注入配置（支持多个）\n")
                f.write("# 每个 [[prompts]] 代表一个独立的提示词注入配置\n")
                f.write("# 可以添加任意数量的 [[prompts]] 配置节\n")
                f.write("# ========================================\n\n")
                f.write("# 完整配置示例（注释形式）：\n")
                f.write("# [[prompts]]\n")
                f.write('# name = "custom_character"          # 提示词唯一标识符（必填）\n')
                f.write('# content = """你的提示词"""          # 提示词内容（必填，多行用三重引号）\n')
                f.write("# enable_kfc = false                  # 是否在 KFC 模式注入（私聊增强）\n")
                f.write("# enable_afc = false                  # 是否在 AFC 模式注入（标准对话）\n")
                f.write("# priority = 100                      # 优先级（1-200，数值越大越高）\n")
                f.write("# enabled = true                      # 是否启用此提示词\n\n")
                f.write("# 取消下方注释并修改内容即可使用：\n")
                f.write("[[prompts]]\n")
                f.write('name = "custom_character"\n')
                f.write('content = """你的提示词"""\n')
                f.write("enable_kfc = false\n")
                f.write("enable_afc = false\n")
                f.write("priority = 100\n")
                f.write("enabled = true\n")
            
            logger.info(f"已生成包含示例配置的配置文件: {config_file_path}")
        except Exception as e:
            logger.error(f"追加示例配置失败: {e}", exc_info=True)
