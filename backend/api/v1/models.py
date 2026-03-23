"""
模型配置 API 路由
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from pydantic import BaseModel
from loguru import logger

from db.database import get_db
from db.models import ModelConfig
from core.model.ollama_adapter import OllamaAdapter
from core.model.google_gemini_adapter import GoogleGeminiAdapter

router = APIRouter(prefix="/models", tags=["模型配置"])


class ModelCreate(BaseModel):
    """模型创建请求"""
    name: str
    provider: str
    endpoint: str
    api_key: str = ""
    temperature: float = 0.7
    max_tokens: int = 4096


class ModelUpdate(BaseModel):
    """模型更新请求"""
    name: str = None
    endpoint: str = None
    api_key: str = None
    temperature: float = None
    max_tokens: int = None
    is_active: bool = None


class ModelResponse(BaseModel):
    """模型响应"""
    id: int
    name: str
    provider: str
    endpoint: str
    api_key: str = ""
    temperature: float
    max_tokens: int
    is_active: bool
    
    class Config:
        from_attributes = True


@router.get("", response_model=List[ModelResponse])
async def get_models(db: AsyncSession = Depends(get_db)):
    """获取所有模型配置"""
    result = await db.execute(select(ModelConfig))
    models = result.scalars().all()
    
    # 转换为响应对象，并隐藏 API Key
    response_models = []
    for model in models:
        response_model = ModelResponse(
            id=model.id,
            name=model.name,
            provider=model.provider,
            endpoint=model.endpoint,
            api_key="***" if model.api_key else "",  # 只在响应中隐藏
            temperature=model.temperature,
            max_tokens=model.max_tokens,
            is_active=model.is_active,
        )
        response_models.append(response_model)
    
    return response_models


@router.post("", response_model=None)
async def add_model(model_data: ModelCreate, db: AsyncSession = Depends(get_db)):
    """添加模型"""
    
    # 自动设置端点 - 用户不需要关心
    endpoint = model_data.endpoint
    if not endpoint or endpoint.strip() == "":
        if model_data.provider == "google":
            endpoint = "https://generativelanguage.googleapis.com"
        elif model_data.provider == "ollama":
            endpoint = "http://localhost:11434"
        elif model_data.provider.lower() in ["openai", "nio"]:
            # NIO公司的固定 Base URL
            endpoint = "https://modelgateway.nioint.com/publicService/v1"
        else:
            endpoint = ""
    
    # 自动设置默认参数 - 用户不需要关心
    temperature = model_data.temperature if model_data.temperature else 0.7
    max_tokens = model_data.max_tokens if model_data.max_tokens else 8192
    
    model = ModelConfig(
        name=model_data.name,
        provider=model_data.provider,
        endpoint=endpoint,
        api_key=model_data.api_key,  # ✅ 直接保存前端传入的真实 API Key
        temperature=temperature,
        max_tokens=max_tokens,
        is_active=False,
    )
    
    db.add(model)
    await db.commit()
    await db.refresh(model)
    
    # ⚠️ 返回响应时隐藏 API Key，但数据库中保存的是真实值
    return {
        "id": model.id,
        "name": model.name,
        "provider": model.provider,
        "endpoint": model.endpoint,
        "api_key": "***",  # 只在返回时显示掩码
        "temperature": model.temperature,
        "max_tokens": model.max_tokens,
        "is_active": model.is_active,
    }


@router.put("/{model_id}", response_model=ModelResponse)
async def update_model(
    model_id: int,
    model_data: ModelUpdate,
    db: AsyncSession = Depends(get_db)
):
    """更新模型配置"""
    result = await db.execute(
        select(ModelConfig).where(ModelConfig.id == model_id)
    )
    model = result.scalar_one_or_none()
    
    if not model:
        raise HTTPException(status_code=404, detail="模型不存在")
    
    # 更新字段
    update_data = model_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(model, field, value)
    
    await db.commit()
    await db.refresh(model)
    
    model.api_key = "***"
    return model


@router.delete("/{model_id}")
async def delete_model(model_id: int, db: AsyncSession = Depends(get_db)):
    """删除模型"""
    result = await db.execute(
        select(ModelConfig).where(ModelConfig.id == model_id)
    )
    model = result.scalar_one_or_none()
    
    if not model:
        raise HTTPException(status_code=404, detail="模型不存在")
    
    await db.delete(model)
    await db.commit()
    
    return {"message": "模型已删除"}


@router.post("/{model_id}/active")
async def set_active_model(model_id: int, db: AsyncSession = Depends(get_db)):
    """设置默认模型"""
    # 先取消所有模型的激活状态
    all_models = await db.execute(select(ModelConfig))
    for model in all_models.scalars().all():
        model.is_active = False
    
    # 激活指定模型
    result = await db.execute(
        select(ModelConfig).where(ModelConfig.id == model_id)
    )
    model = result.scalar_one_or_none()
    
    if not model:
        raise HTTPException(status_code=404, detail="模型不存在")
    
    model.is_active = True
    await db.commit()
    
    return {"message": f"已将 {model.name} 设为默认模型"}


@router.post("/{model_id}/test")
async def test_model(model_id: int, db: AsyncSession = Depends(get_db)):
    """测试模型连接"""
    result = await db.execute(
        select(ModelConfig).where(ModelConfig.id == model_id)
    )
    model = result.scalar_one_or_none()
    
    if not model:
        raise HTTPException(status_code=404, detail="模型不存在")
    
    # 根据 provider 选择不同的测试方式
    if model.provider == "ollama":
        try:
            ollama = OllamaAdapter(model.endpoint)
            success = await ollama.test_connection(model.name)
            
            if success:
                return {
                    "message": "连接测试成功",
                    "model": model.name,
                    "provider": model.provider,
                    "endpoint": model.endpoint,
                }
            else:
                raise HTTPException(
                    status_code=500,
                    detail=f"无法连接到 Ollama 服务或模型不存在\n请检查：\n1. Ollama 服务是否运行（ollama serve）\n2. 模型 '{model.name}' 是否已下载"
                )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    elif model.provider.lower() in ["openai", "nio"]:
        try:
            from core.model.openai_adapter import OpenAIAdapter
            from core.model import ModelConfig as CoreModelConfig
            
            # ✅ 使用数据库中保存的真实 API Key
            api_key_to_use = model.api_key
            
            if not api_key_to_use or api_key_to_use == "***":
                raise HTTPException(
                    status_code=400,
                    detail="OpenAI API 需要 API Key"
                )
            
            logger.info(f"🔑 测试 NIO/OpenAI 连接：{model.name}")
            
            # 创建核心模型配置
            core_config = CoreModelConfig(
                name=model.name,
                provider=model.provider,
                base_url=model.endpoint,
                api_key=api_key_to_use,
            )
            
            # 创建适配器并测试
            adapter = OpenAIAdapter(core_config)
            success = await adapter.health_check()
            
            if success:
                return {
                    "message": "连接测试成功",
                    "model": model.name,
                    "provider": model.provider,
                    "endpoint": model.endpoint,
                }
            else:
                raise HTTPException(
                    status_code=500,
                    detail=f"无法连接到 {model.provider} 服务\n请检查：\n1. API Key 是否正确\n2. Base URL 是否正确\n3. 模型名称是否正确"
                )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    elif model.provider in ["google", "gemini"]:
        try:
            # ✅ 直接使用数据库中保存的真实 API Key（前端传入的值）
            api_key_to_use = model.api_key
            
            if not api_key_to_use or api_key_to_use == "***":
                raise HTTPException(
                    status_code=400,
                    detail="Google Gemini 需要 API Key"
                )
            
            logger.info(f"🔑 使用 API Key: {api_key_to_use[:10]}...")
            
            gemini = GoogleGeminiAdapter(api_key=api_key_to_use)
            success = await gemini.test_connection(model.name)
            
            if success:
                return {
                    "message": "连接测试成功",
                    "model": model.name,
                    "provider": model.provider,
                    "endpoint": model.endpoint or "https://generativelanguage.googleapis.com",
                }
            else:
                raise HTTPException(
                    status_code=500,
                    detail=f"无法连接到 Google Gemini 服务\n请检查：\n1. API Key 是否正确\n2. 模型名称是否正确\n3. 网络连接是否正常"
                )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    else:
        # 其他 provider 的测试（暂时返回成功）
        return {
            "message": "连接测试成功（模拟）",
            "model": model.name,
            "provider": model.provider,
            "endpoint": model.endpoint,
        }
