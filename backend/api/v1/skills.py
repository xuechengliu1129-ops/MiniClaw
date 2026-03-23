"""
Skills API - 基于 DeepAgents 的极简技能管理

核心理念：
- 只需 SKILL.md 文档，零代码开发
- 自动扫描目录加载 Skills
- 前端可视化创建技能（生成 SKILL.md）
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import os
import shutil
from loguru import logger

router = APIRouter(prefix="/skills", tags=["Skills 技能管理"])


class CreateSkillRequest(BaseModel):
    """创建技能请求"""
    name: str = Field(..., description="技能名称（唯一标识）")
    description: str = Field(..., description="技能描述")
    author: Optional[str] = "User"
    version: Optional[str] = "1.0.0"
    parameters: Optional[List[Dict[str, Any]]] = []


@router.get("", response_model=List[Dict])
async def list_skills():
    """获取所有已加载的 Skills（包括系统技能和自定义技能）"""
    try:
        # 直接从文件系统扫描所有可用技能
        from core.skills import get_available_skills
        
        skills_info = get_available_skills()
        
        # 标记为自定义技能
        for skill in skills_info:
            skill["is_system"] = False
            skill["type"] = "custom"
        
        return skills_info
        
    except Exception as e:
        logger.error(f"获取技能列表失败：{e}")
        return []


@router.post("", response_model=Dict)
async def create_skill(
    request: CreateSkillRequest,
    background_tasks: BackgroundTasks
):
    """
    创建新技能（生成 SKILL.md 文件）
    
    流程：
    1. 验证技能名称
    2. 创建目录
    3. 写入 SKILL.md
    4. 后台触发热重载
    """
    try:
        # 1. 验证名称
        skill_name = request.name
        if not skill_name.replace('_', '').isalnum():
            raise HTTPException(
                status_code=400,
                detail="技能名称只能包含字母、数字和下划线"
            )
        
        # 2. 构建目录路径 - 使用三层 dirname 获取 backend 目录
        backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        skill_dir = os.path.join(backend_dir, "core", "skills", "custom_skills", skill_name)
        
        if os.path.exists(skill_dir):
            raise HTTPException(
                status_code=400,
                detail=f"技能已存在：{skill_name}"
            )
        
        os.makedirs(skill_dir, exist_ok=True)
        
        # 3. 写入 SKILL.md
        from datetime import datetime
        skill_md_content = f"""---
name: "{skill_name}"
description: "{request.description}"
author: "{request.author}"
version: "{request.version}"
async_support: true
parameters: {request.parameters if request.parameters else []}
created_at: "{datetime.now().isoformat()}"
---

# {request.description}

## 功能说明

{request.description}

## 使用示例

请参考技能实现。
"""
        
        skill_md_path = os.path.join(skill_dir, "SKILL.md")
        with open(skill_md_path, 'w', encoding='utf-8') as f:
            f.write(skill_md_content)
        
        logger.info(f"✅ 创建技能文档：{skill_md_path}")
        
        # 4. 后台触发热重载（可选）
        async def reload_skills():
            try:
                from main import app
                # TODO: 实现热重载逻辑
                logger.info(f"🔄 后台触发 Skills 重载：{skill_name}")
            except Exception as e:
                logger.error(f"后台重载失败：{e}")
        
        background_tasks.add_task(reload_skills)
        
        return {
            "success": True,
            "message": f"技能 {skill_name} 创建成功，请重启后端服务或手动重载",
            "skill_name": skill_name,
            "directory": skill_dir,
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建技能失败：{e}")
        raise HTTPException(
            status_code=500,
            detail=f"创建技能失败：{str(e)}"
        )


@router.delete("/{skill_name}", response_model=Dict)
async def delete_skill(skill_name: str):
    """
    删除技能（删除对应的文件夹）
    
    流程：
    1. 验证技能名称
    2. 检查目录是否存在
    3. 删除整个文件夹
    """
    try:
        # 1. 验证名称
        if not skill_name.replace('_', '').isalnum():
            raise HTTPException(
                status_code=400,
                detail="技能名称只能包含字母、数字和下划线"
            )
        
        # 2. 构建目录路径 - 使用三层 dirname 获取 backend 目录
        backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        skill_dir = os.path.join(backend_dir, "core", "skills", "custom_skills", skill_name)
        
        # 3. 检查目录是否存在
        if not os.path.exists(skill_dir):
            raise HTTPException(
                status_code=404,
                detail=f"技能不存在：{skill_name}"
            )
        
        # 4. 删除整个文件夹
        shutil.rmtree(skill_dir)
        logger.info(f"✅ 删除技能目录：{skill_dir}")
        
        return {
            "success": True,
            "message": f"技能 {skill_name} 已删除",
            "skill_name": skill_name,
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除技能失败：{e}")
        raise HTTPException(
            status_code=500,
            detail=f"删除技能失败：{str(e)}"
        )