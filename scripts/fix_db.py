"""
数据库清理脚本 - 修复重复激活模型问题
"""
import sys
import os

# 添加后端目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from sqlalchemy import create_engine, update
from sqlalchemy.orm import Session
from db.models import ModelConfig

# 创建数据库引擎
engine = create_engine(
    "sqlite:///./miniclaw.db",
    echo=True,
)

def fix_duplicate_active_models():
    """修复重复激活模型问题，只保留第一个激活的模型"""
    with Session(engine) as session:
        # 查询所有激活的模型
        active_models = session.query(ModelConfig).filter(
            ModelConfig.is_active == True
        ).all()
        
        if len(active_models) == 0:
            print("✅ 没有激活的模型")
            return
        
        if len(active_models) == 1:
            print(f"✅ 只有一个激活模型：{active_models[0].name}")
            return
        
        # 有多个激活模型，只保留第一个
        print(f"⚠️  发现 {len(active_models)} 个激活模型，将只保留第一个")
        for i, model in enumerate(active_models):
            if i == 0:
                print(f"  ✓ 保留：{model.name} (ID: {model.id})")
            else:
                print(f"  ✗ 取消激活：{model.name} (ID: {model.id})")
                model.is_active = False
        
        session.commit()
        print(f"✅ 修复完成！保留了 {active_models[0].name} 作为默认模型")


if __name__ == "__main__":
    try:
        fix_duplicate_active_models()
    except Exception as e:
        print(f"❌ 清理失败：{e}")
        sys.exit(1)
