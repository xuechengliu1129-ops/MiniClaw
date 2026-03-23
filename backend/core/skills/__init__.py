"""
Skills 技能标准化管理模块 - 基于 DeepAgents 原生机制

核心理念：
- 100% 复用 DeepAgents 原生 Skills 能力
- 只需 SKILL.md 文档，零代码开发
- 自动扫描、渐进式加载、热插拔
- 与 DeepAgent 深度集成

使用方式：
```python
from deepagents import create_deep_agent

agent = create_deep_agent(
    skills=["./custom_skills/"],  # 指向 SKILL.md 目录
)

result = agent.invoke({
    "messages": [{"role": "user", "content": "帮我读取文件"}]
})
```
"""

from deepagents import create_deep_agent
from loguru import logger
import os
from typing import Dict, Any, List

__version__ = "3.0.0"
__author__ = "MiniClaw Team"

# 重新导出 DeepAgents 核心组件
__all__ = ["create_deep_agent", "get_available_skills"]


def load_skills_from_directory(skills_dir: str) -> Dict[str, Any]:
    """
    从目录加载所有 SKILL.md 文件（参考官方示例）
    
    Args:
        skills_dir: Skills 根目录
        
    Returns:
        Dict[str, Any]: {skill_name: {"content": str, "path": str}}
    """
    skills_files = {}
    
    if not os.path.exists(skills_dir):
        logger.warning(f"Skills 目录不存在：{skills_dir}")
        return skills_files
    
    # 遍历所有子目录
    for item in os.listdir(skills_dir):
        skill_dir = os.path.join(skills_dir, item)
        
        if not os.path.isdir(skill_dir):
            continue
        
        skill_md_path = os.path.join(skill_dir, "SKILL.md")
        
        if os.path.exists(skill_md_path):
            with open(skill_md_path, 'r', encoding='utf-8') as f:
                skill_content = f.read()
            
            # 虚拟路径格式（必须以 / 开头）
            virtual_path = f"/skills/{item}/SKILL.md"
            skills_files[virtual_path] = {
                "content": skill_content,
                "real_path": skill_md_path,
                "name": item,  # 技能名称（目录名）
            }
            
            logger.info(f"✅ 加载 Skill: {virtual_path}")
    
    return skills_files


def get_available_skills(skills_dir: str = None) -> List[Dict[str, str]]:
    """
    获取所有可用技能的信息（用于前端展示或 AI 提示词）
    
    Args:
        skills_dir: Skills 目录路径，默认为 backend/core/skills/custom_skills
        
    Returns:
        List[Dict]: 技能信息列表 [{name, description, author, version}]
    """
    if skills_dir is None:
        skills_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            "skills", 
            "custom_skills"
        )
    
    skills_info = []
    
    if not os.path.exists(skills_dir):
        return skills_info
    
    # 扫描所有子目录
    for item in os.listdir(skills_dir):
        skill_dir = os.path.join(skills_dir, item)
        
        if not os.path.isdir(skill_dir):
            continue
        
        skill_md_path = os.path.join(skill_dir, "SKILL.md")
        
        if not os.path.exists(skill_md_path):
            continue
        
        try:
            # 解析 SKILL.md 获取元数据
            import re
            with open(skill_md_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 解析 YAML frontmatter
            yaml_match = re.search(r'---\n(.*?)\n---', content, re.DOTALL)
            if yaml_match:
                yaml_content = yaml_match.group(1)
                
                # 提取各个字段
                name_match = re.search(r'name:\s*"([^"]+)"', yaml_content)
                desc_match = re.search(r'description:\s*"([^"]+)"', yaml_content)
                author_match = re.search(r'author:\s*"([^"]+)"', yaml_content)
                version_match = re.search(r'version:\s*"([^"]+)"', yaml_content)
                
                skills_info.append({
                    "name": name_match.group(1) if name_match else item,
                    "description": desc_match.group(1) if desc_match else "无描述",
                    "author": author_match.group(1) if author_match else "Unknown",
                    "version": version_match.group(1) if version_match else "1.0.0",
                    "directory": item,
                })
        except Exception as e:
            logger.error(f"解析 SKILL.md 失败 {item}: {e}")
    
    return skills_info


def initialize_skills_system(skills_dir: str = None):
    """
    初始化 Skills 系统
    
    Args:
        skills_dir: Skills 目录路径，默认为 backend/core/skills/custom_skills
        
    Returns:
        tuple: (create_deep_agent 函数，skills_files 字典，skills_dir 路径，skills_info 列表)
    """
    if skills_dir is None:
        skills_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            "skills", 
            "custom_skills"
        )
    
    logger.info(f"🚀 DeepAgent Skills 系统初始化：{skills_dir}")
    
    # 加载所有 SKILL.md 文件内容
    skills_files = load_skills_from_directory(skills_dir)
    
    # 获取所有技能的元数据（用于展示和提示词）
    skills_info = get_available_skills(skills_dir)
    
    logger.info(f"✅ 发现 {len(skills_info)} 个技能：{[s['name'] for s in skills_info]}")
    logger.info("✅ DeepAgent Skills 系统初始化完成")
    
    return create_deep_agent, skills_files, skills_dir, skills_info


def get_skills_system_prompt(skills_info: list = None) -> str:
    """
    生成包含技能信息的系统提示词
    
    Args:
        skills_info: 技能信息列表
        
    Returns:
        str: 系统提示词字符串
    """
    if not skills_info:
        return "你是一个智能助手。"
    
    skills_description = "\n".join([
        f"- **{skill['name']}**: {skill['description']}"
        for skill in skills_info
    ])
    
    system_prompt = f"""你是一个智能助手，可以使用以下技能来帮助用户：

可用技能列表:
{skills_description}

当用户的请求涉及这些技能时，请自动识别并调用对应的技能。
如果用户询问有哪些技能，请直接列出上述技能列表及其描述。"""
    
    return system_prompt


# 在模块级别导出
__all__ = ["create_deep_agent", "get_available_skills", "get_skills_system_prompt"]
