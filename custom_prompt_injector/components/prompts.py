"""动态提示词组件生成器"""
from typing import ClassVar
from src.plugin_system.base.base_prompt import BasePrompt
from src.plugin_system.base.component_types import InjectionRule, InjectionType, PromptInfo, ComponentType
from src.common.logger import get_logger

logger = get_logger("custom_prompt_injector")


def create_custom_prompt_class(prompt_config: dict, index: int) -> type[BasePrompt] | None:
    """
    动态创建自定义提示词组件类
    
    Args:
        prompt_config: 提示词配置字典，包含 name, content, priority 等
        index: 提示词索引（用于确保唯一性）
    
    Returns:
        动态创建的 BasePrompt 子类，如果配置无效则返回 None
    """
    # 提取配置项
    name = prompt_config.get("name", f"custom_prompt_{index}")
    content = prompt_config.get("content", "").strip()
    priority = prompt_config.get("priority", 100)
    enable_kfc = prompt_config.get("enable_kfc", True)
    enable_afc = prompt_config.get("enable_afc", True)
    enabled = prompt_config.get("enabled", True)
    
    # 如果未启用，返回 None
    if not enabled:
        logger.info(f"提示词 '{name}' 未启用，跳过注册")
        return None
    
    # 如果内容为空，返回 None
    if not content:
        logger.warning(f"提示词 '{name}' 内容为空，跳过注册")
        return None
    
    # 构建注入规则列表
    injection_rules_list = []
    
    # KFC 相关注入目标
    if enable_kfc:
        kfc_targets = [
            "kfc_unified_prompt",  # KFC unified 模式
            "kfc_main",            # KFC 主提示词
            "kfc_style_prompt",    # KFC 风格提示词
            "kfc_planner",         # KFC split 模式 - planner
            "kfc_replyer",         # KFC split 模式 - replyer
        ]
        for target in kfc_targets:
            injection_rules_list.append(
                InjectionRule(
                    target_prompt=target,
                    injection_type=InjectionType.APPEND,
                    priority=priority
                )
            )
    
    # AFC 相关注入目标
    if enable_afc:
        afc_targets = [
            "s4u_style_prompt",    # S4U 风格提示词
            "normal_style_prompt", # 普通风格提示词
        ]
        for target in afc_targets:
            injection_rules_list.append(
                InjectionRule(
                    target_prompt=target,
                    injection_type=InjectionType.APPEND,
                    priority=priority
                )
            )
    
    # 如果没有任何注入规则，返回 None
    if not injection_rules_list:
        logger.warning(f"提示词 '{name}' 未启用任何集成（KFC/AFC），跳过注册")
        return None
    
    # 动态创建类
    class CustomPromptComponent(BasePrompt):
        """动态生成的自定义提示词组件"""
        
        # 类属性（不是实例属性）
        prompt_name: str = name
        prompt_description: str = f"自定义提示词：{name}"
        injection_rules: ClassVar[list[InjectionRule]] = injection_rules_list
        
        # 存储配置，供 execute 使用
        _content: ClassVar[str] = content
        _config: ClassVar[dict] = prompt_config
        
        async def execute(self) -> str:
            """返回提示词内容"""
            debug_mode = self.get_config("plugin.debug_mode", False)
            
            if debug_mode:
                logger.debug(
                    f"注入提示词 '{self.prompt_name}' | "
                    f"优先级={priority} | KFC={enable_kfc} | AFC={enable_afc} | "
                    f"长度={len(self._content)}字符"
                )
            
            return self._content
        
        @classmethod
        def get_prompt_info(cls) -> PromptInfo:
            """返回提示词信息"""
            return PromptInfo(
                name=cls.prompt_name,
                component_type=ComponentType.PROMPT,
                description=cls.prompt_description,
                injection_rules=cls.injection_rules
            )
    
    # 设置类名（方便调试）
    CustomPromptComponent.__name__ = f"CustomPrompt_{name}_{index}"
    CustomPromptComponent.__qualname__ = CustomPromptComponent.__name__
    
    logger.info(
        f"创建提示词组件 '{name}' | "
        f"优先级={priority} | KFC={enable_kfc} | AFC={enable_afc} | "
        f"注入规则数={len(injection_rules_list)}"
    )
    
    return CustomPromptComponent
