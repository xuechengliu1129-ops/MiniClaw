"""
Skills 技能管理模块单元测试
"""
import pytest
from backend.core.skills import (
    SkillBase,
    SkillMetadata,
    SkillParameter,
    SkillResult,
    SkillManager,
    ExampleSkill,
)


class TestSkillMetadata:
    """测试技能元数据"""
    
    def test_create_metadata(self):
        metadata = SkillMetadata(
            name="test_skill",
            description="测试技能",
            version="1.0.0",
            author="Test Author",
            tags=["test", "demo"],
        )
        
        assert metadata.name == "test_skill"
        assert metadata.description == "测试技能"
        assert metadata.version == "1.0.0"
        assert metadata.author == "Test Author"
        assert metadata.tags == ["test", "demo"]
        assert metadata.enabled is True


class TestSkillParameter:
    """测试技能参数"""
    
    def test_create_parameter(self):
        param = SkillParameter(
            name="message",
            type="str",
            description="消息内容",
            required=True,
            default=None,
        )
        
        assert param.name == "message"
        assert param.type == "str"
        assert param.description == "消息内容"
        assert param.required is True
        assert param.default is None


class TestExampleSkill:
    """测试示例技能"""
    
    @pytest.mark.asyncio
    async def test_execute_success(self):
        skill = ExampleSkill()
        result = await skill.execute(message="Hello", count=3)
        
        assert result.success is True
        assert result.data is not None
        assert result.data["original_message"] == "Hello"
        assert result.data["processed_count"] == 3
    
    @pytest.mark.asyncio
    async def test_execute_with_default_count(self):
        skill = ExampleSkill()
        result = await skill.execute(message="World")
        
        assert result.success is True
        assert result.data["processed_count"] == 1


class TestSkillManager:
    """测试技能管理器"""
    
    def test_register_skill(self):
        manager = SkillManager()
        skill = ExampleSkill()
        
        manager.register_skill(skill)
        
        assert manager.get_skill("example_skill") == skill
        assert len(manager.list_skills()) == 1
    
    def test_unregister_skill(self):
        manager = SkillManager()
        skill = ExampleSkill()
        
        manager.register_skill(skill)
        manager.unregister_skill("example_skill")
        
        assert manager.get_skill("example_skill") is None
    
    @pytest.mark.asyncio
    async def test_execute_skill(self):
        manager = SkillManager()
        skill = ExampleSkill()
        
        manager.register_skill(skill)
        result = await manager.execute_skill("example_skill", message="Test", count=2)
        
        assert result.success is True
        assert result.data["processed_count"] == 2
    
    @pytest.mark.asyncio
    async def test_execute_nonexistent_skill(self):
        manager = SkillManager()
        result = await manager.execute_skill("nonexistent_skill")
        
        assert result.success is False
        assert "技能不存在" in result.error
    
    def test_list_skills(self):
        manager = SkillManager()
        skill = ExampleSkill()
        
        manager.register_skill(skill)
        skills = manager.list_skills()
        
        assert len(skills) == 1
        assert skills[0]["name"] == "example_skill"
        assert skills[0]["description"] == "示例技能：展示技能开发规范"
