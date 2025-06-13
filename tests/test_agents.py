"""Tests for agent functionality."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from app.agents import AgentOrchestrator, AgentResponse


@pytest.fixture
def mock_orchestrator():
    """Create a mock orchestrator for testing."""
    orchestrator = AgentOrchestrator()
    # Mock the agents to avoid actual AI API calls
    orchestrator.agents = {
        "test_agent": MagicMock()
    }
    return orchestrator


@pytest.mark.asyncio
async def test_agent_execution_success(mock_orchestrator):
    """Test successful agent execution."""
    # Mock successful response
    mock_response = AgentResponse(
        success=True,
        result="Test response",
        execution_time_ms=100,
        metadata={"agent_type": "test_agent"}
    )
    
    mock_orchestrator.agents["test_agent"].execute = AsyncMock(return_value=mock_response)
    
    # Execute task
    result = await mock_orchestrator.execute_task(
        task="Test task",
        agent_type="test_agent"
    )
    
    # Assertions
    assert result.success is True
    assert result.result == "Test response"
    assert result.execution_time_ms == 100


@pytest.mark.asyncio
async def test_agent_execution_failure(mock_orchestrator):
    """Test agent execution failure."""
    # Mock failed response
    mock_response = AgentResponse(
        success=False,
        error="Test error",
        execution_time_ms=50,
        metadata={"agent_type": "test_agent"}
    )
    
    mock_orchestrator.agents["test_agent"].execute = AsyncMock(return_value=mock_response)
    
    # Execute task
    result = await mock_orchestrator.execute_task(
        task="Test task",
        agent_type="test_agent"
    )
    
    # Assertions
    assert result.success is False
    assert result.error == "Test error"
    assert result.execution_time_ms == 50


@pytest.mark.asyncio
async def test_invalid_agent_type(mock_orchestrator):
    """Test execution with invalid agent type."""
    result = await mock_orchestrator.execute_task(
        task="Test task",
        agent_type="nonexistent_agent"
    )
    
    # Assertions
    assert result.success is False
    assert "not found" in result.error
    assert "nonexistent_agent" in result.error


def test_get_available_agents(mock_orchestrator):
    """Test getting available agents."""
    agents = mock_orchestrator.get_available_agents()
    assert "test_agent" in agents


def test_get_agent_info(mock_orchestrator):
    """Test getting agent information."""
    info = mock_orchestrator.get_agent_info("test_agent")
    assert "name" in info
    assert "available" in info
    assert "type" in info 