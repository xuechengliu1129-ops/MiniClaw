"""
Skill 元数据模型定义
"""
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional


class SkillParameter(BaseModel):
    """技能参数定义"""
    name: str = Field(..., description="参数名称")
    type: str = Field(..., description="参数类型 (str, int, float, bool, list, dict)")
    description: str = Field(..., description="参数描述")
    required: bool = Field(default=False, description="是否必填")
    default: Optional[Any] = Field(default=None, description="默认值")
    min_value: Optional[Any] = Field(default=None, description="最小值约束")
    max_value: Optional[Any] = Field(default=None, description="最大值约束")


class SkillMetadata(BaseModel):
    """技能元数据 - 统一管理 Skill 的核心信息"""
    # 基础信息
    name: str = Field(..., description="技能名称（唯一标识）")
    description: str = Field(..., description="技能描述")
    version: str = Field(default="1.0.0", description="技能版本")
    author: Optional[str] = Field(default=None, description="技能作者")
    
    # 执行信息
    required_roles: List[str] = Field(default_factory=list, description="所需角色列表")
    async_support: bool = Field(default=True, description="是否支持异步执行")
    
    # 状态信息
    enabled: bool = Field(default=True, description="是否启用")
    tags: List[str] = Field(default_factory=list, description="技能标签")
    
    # 参数信息
    parameters: List[SkillParameter] = Field(default_factory=list, description="技能参数列表")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "file_reader",
                "description": "读取文件内容的技能",
                "version": "1.0.0",
                "author": "Developer",
                "required_roles": ["user", "admin"],
                "async_support": True,
                "enabled": True,
                "tags": ["file", "io"],
                "parameters": [
                    {
                        "name": "file_path",
                        "type": "str",
                        "description": "文件路径",
                        "required": True
                    }
                ]
            }
        }