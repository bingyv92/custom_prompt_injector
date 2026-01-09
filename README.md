# 自定义提示词注入插件

## 📝 功能介绍

支持多个自定义提示词注入到 MoFox_Bot 的 KFC/AFC 对话系统中，灵活控制提示词的注入位置、优先级和适用场景。

## ✨ 主要特性

- ✅ **多提示词支持**：可配置任意数量的独立提示词
- ✅ **灵活注入控制**：每个提示词可独立配置 KFC/AFC 集成
- ✅ **优先级管理**：支持 1-200 级优先级设置
- ✅ **动态开关**：每个提示词可独立启用/禁用
- ✅ **多行内容**：支持使用三重引号定义复杂提示词
- ✅ **零代码配置**：纯配置文件驱动，无需编写代码

## 🚀 快速开始

### 1. 基础配置

编辑 `config/plugins/custom_prompt_injector/config.toml`：

```toml
[plugin]
enabled = true
debug_mode = false

[[prompts]]
name = "my_first_prompt"
content = "你的提示词内容"
enable_kfc = true
enable_afc = true
priority = 100
enabled = true
```

### 2. 多行提示词示例

```toml
[[prompts]]
name = "character_setting"
content = """
【角色设定】
名字：小狐
性格：活泼可爱
特点：喜欢用颜文字
"""
enable_kfc = true
enable_afc = true
priority = 120
enabled = true
```

### 3. 添加更多提示词

只需继续添加 `[[prompts]]` 配置节：

```toml
[[prompts]]
name = "style_guide"
content = "回复风格指导..."
priority = 90
enabled = true

[[prompts]]
name = "background_info"
content = "背景信息..."
priority = 80
enabled = false  # 暂时禁用
```

## ⚙️ 配置说明

### plugin 节

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `enabled` | bool | true | 是否启用插件 |
| `debug_mode` | bool | false | 是否输出调试日志 |

### [[prompts]] 节（可多个）

| 配置项 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `name` | string | ✅ | - | 提示词唯一标识符 |
| `content` | string | ✅ | - | 提示词具体内容 |
| `enable_kfc` | bool | ❌ | true | 是否在 KFC 模式注入 |
| `enable_afc` | bool | ❌ | true | 是否在 AFC 模式注入 |
| `priority` | int | ❌ | 100 | 注入优先级（1-200） |
| `enabled` | bool | ❌ | true | 是否启用此提示词 |

### 优先级建议

```
50-80    低优先级   背景信息、辅助指导
100-120  中优先级   常规增强、风格调整
130-150  高优先级   关键指导、行为约束
160+     最高优先级 覆盖性指令
```

## 💡 使用场景

### 场景 1：增强角色人设

```toml
[[prompts]]
name = "character_core"
content = """
【核心人设】
- 你是一只活泼的小狐狸
- 喜欢使用"呐"、"嗯"等语气词
- 性格开朗但偶尔害羞
"""
priority = 120
```

### 场景 2：私聊模式增强

```toml
[[prompts]]
name = "private_mode"
content = """
【私聊模式】
当前是一对一私密对话：
1. 语气更亲密自然
2. 可以讨论更私人的话题
3. 表达更真实的情感
"""
enable_kfc = true   # 仅在私聊模式生效
enable_afc = false
priority = 110
```

### 场景 3：回复风格规范

```toml
[[prompts]]
name = "reply_rules"
content = """
【回复规范】
- 避免使用"作为AI"等表述
- 保持对话自然流畅
- 适当使用表情和语气词
- 回复长度适中
"""
priority = 90
```

## 🔧 高级用法

### 条件启用

根据需要临时启用/禁用提示词：

```toml
[[prompts]]
name = "debug_mode"
content = "调试模式专用提示..."
enabled = false  # 平时禁用，调试时启用
```

### 优先级冲突处理

当多个提示词存在冲突时，优先级高的后注入，因此影响更大：

```toml
[[prompts]]
name = "base_setting"
content = "基础设定..."
priority = 100

[[prompts]]
name = "override_setting"
content = "覆盖设定..."
priority = 150  # 会覆盖基础设定
```

### 分离 KFC/AFC

针对不同场景使用不同提示词：

```toml
# 群聊专用
[[prompts]]
name = "group_mode"
content = "群聊场景指导..."
enable_kfc = false
enable_afc = true

# 私聊专用
[[prompts]]
name = "private_mode"
content = "私聊场景指导..."
enable_kfc = true
enable_afc = false
```

## 📊 注入目标说明

### KFC 模式注入点
- `kfc_unified_prompt` - KFC unified 模式主提示词
- `kfc_main` - KFC 主提示词
- `kfc_style_prompt` - KFC 风格提示词
- `kfc_planner` - KFC split 模式规划器
- `kfc_replyer` - KFC split 模式回复器

### AFC 模式注入点
- `s4u_style_prompt` - S4U 风格提示词
- `normal_style_prompt` - 标准风格提示词

## ⚠️ 注意事项

1. **提示词内容不要过长**：建议单个提示词不超过 500 字
2. **避免冲突指令**：多个提示词的指令应保持一致
3. **优先级合理分配**：核心设定用高优先级，辅助信息用低优先级
4. **测试后上线**：修改配置后建议先在测试环境验证
5. **调试模式**：遇到问题时启用 `debug_mode = true` 查看日志

## 🐛 故障排除

### 提示词未生效

1. 检查 `plugin.enabled = true`
2. 检查该提示词的 `enabled = true`
3. 启用 `debug_mode` 查看日志
4. 确认优先级设置合理

### 多行内容解析错误

确保使用三重引号：

```toml
# ✅ 正确
content = """
多行
内容
"""

# ❌ 错误
content = "多行
内容"
```

### 配置不生效

重启机器人后配置才会加载。

## 📄 许可证

MIT License

## 👥 作者

bingyy92

---

*插件版本：1.0.0*
# custom_prompt_injector
适用于mofox的自定义插入提示词的插件
