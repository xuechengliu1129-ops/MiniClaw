"""
记忆管理模块单元测试
"""
import pytest
from datetime import datetime, timedelta
from backend.core.memory import (
    MemoryManager,
    MemoryRecord,
    MemoryLevel,
    MemorySearchRequest,
)


class TestMemoryRecord:
    """测试记忆记录"""
    
    def test_create_memory(self):
        memory = MemoryRecord(
            content="这是一条测试记忆",
            level=MemoryLevel.USER,
            user_id=1,
            importance=0.8,
        )
        
        assert memory.content == "这是一条测试记忆"
        assert memory.level == MemoryLevel.USER
        assert memory.user_id == 1
        assert memory.importance == 0.8
        assert memory.id is None  # 未保存前 ID 为 None


class TestMemoryManager:
    """测试记忆管理器"""
    
    @pytest.mark.asyncio
    async def test_add_memory(self):
        manager = MemoryManager()
        memory = MemoryRecord(
            content="测试添加记忆",
            level=MemoryLevel.USER,
            user_id=1,
        )
        
        result = await manager.add_memory(memory)
        
        assert result.id is not None
        assert manager.memories[result.id] == result
    
    @pytest.mark.asyncio
    async def test_get_memory(self):
        manager = MemoryManager()
        memory = MemoryRecord(
            content="测试获取记忆",
            level=MemoryLevel.USER,
            user_id=1,
        )
        
        saved = await manager.add_memory(memory)
        retrieved = await manager.get_memory(saved.id)
        
        assert retrieved == saved
        assert retrieved.content == "测试获取记忆"
    
    @pytest.mark.asyncio
    async def test_search_memories(self):
        manager = MemoryManager()
        
        # 添加多条记忆
        await manager.add_memory(MemoryRecord(content="重要记忆 1", level=MemoryLevel.USER, user_id=1, importance=0.9))
        await manager.add_memory(MemoryRecord(content="普通记忆 2", level=MemoryLevel.USER, user_id=1, importance=0.5))
        await manager.add_memory(MemoryRecord(content="全局记忆", level=MemoryLevel.GLOBAL, importance=0.7))
        
        # 按用户搜索
        request = MemorySearchRequest(user_id=1, top_k=10)
        results = await manager.search_memories(request)
        
        assert len(results) == 2
        assert all(m.user_id == 1 for m in results)
        
        # 按级别搜索
        request = MemorySearchRequest(level=MemoryLevel.GLOBAL, top_k=10)
        results = await manager.search_memories(request)
        
        assert len(results) == 1
        assert results[0].level == MemoryLevel.GLOBAL
        
        # 按重要性搜索
        request = MemorySearchRequest(min_importance=0.8, top_k=10)
        results = await manager.search_memories(request)
        
        assert len(results) == 1
        assert results[0].importance >= 0.8
    
    @pytest.mark.asyncio
    async def test_update_memory(self):
        manager = MemoryManager()
        memory = MemoryRecord(
            content="原始内容",
            level=MemoryLevel.USER,
            user_id=1,
        )
        
        saved = await manager.add_memory(memory)
        
        # 更新
        updated = await manager.update_memory(saved.id, {
            "content": "更新后的内容",
            "importance": 0.9,
        })
        
        assert updated is True
        updated_memory = await manager.get_memory(saved.id)
        assert updated_memory.content == "更新后的内容"
        assert updated_memory.importance == 0.9
    
    @pytest.mark.asyncio
    async def test_delete_memory(self):
        manager = MemoryManager()
        memory = MemoryRecord(
            content="待删除记忆",
            level=MemoryLevel.USER,
            user_id=1,
        )
        
        saved = await manager.add_memory(memory)
        deleted = await manager.delete_memory(saved.id)
        
        assert deleted is True
        assert saved.id not in manager.memories
    
    @pytest.mark.asyncio
    async def test_memory_sorting_by_importance(self):
        manager = MemoryManager()
        
        # 添加不同重要性的记忆
        await manager.add_memory(MemoryRecord(content="低重要性", level=MemoryLevel.USER, importance=0.3))
        await manager.add_memory(MemoryRecord(content="高重要性", level=MemoryLevel.USER, importance=0.9))
        await manager.add_memory(MemoryRecord(content="中重要性", level=MemoryLevel.USER, importance=0.6))
        
        request = MemorySearchRequest(top_k=10)
        results = await manager.search_memories(request)
        
        # 验证按重要性降序排列
        assert results[0].importance >= results[1].importance
        assert results[1].importance >= results[2].importance
