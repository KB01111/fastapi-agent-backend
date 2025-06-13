"""
Test suite for AI framework integration.

Tests the core AI agent frameworks: PraisonAI, CrewAI, and AG2/AutoGen.
"""

import pytest
import os
from unittest.mock import patch, MagicMock

# Set test environment variables
os.environ["OPENAI_API_KEY"] = "test-key"
os.environ["ANTHROPIC_API_KEY"] = "test-key"

from app.agents import (
    AgentOrchestrator, 
    PraisonAIAgent, 
    CrewAIAgent, 
    AG2Agent,
    AgentResponse
)


class TestFrameworkIntegration:
    """Test suite for AI framework integration."""
    
    def test_agent_orchestrator_initialization(self):
        """Test that the orchestrator initializes all agents."""
        orchestrator = AgentOrchestrator()
        
        # Check that all expected agent types are registered
        expected_agents = ["praisonai", "crewai", "ag2"]
        for agent_type in expected_agents:
            assert agent_type in orchestrator.agents
            assert orchestrator.agents[agent_type] is not None
    
    def test_get_available_agents(self):
        """Test getting list of available agents."""
        orchestrator = AgentOrchestrator()
        available_agents = orchestrator.get_available_agents()
        
        # Should return a list of available agents
        assert isinstance(available_agents, list)
        # Should contain at least one of our core agents
        core_agents = ["praisonai", "crewai", "ag2"]
        assert any(agent in available_agents for agent in core_agents)
    
    def test_get_agent_info(self):
        """Test getting agent information."""
        orchestrator = AgentOrchestrator()
        
        # Test with a core agent that should exist
        info = orchestrator.get_agent_info("praisonai")
        assert "name" in info
        assert "available" in info
        assert "type" in info
        assert "description" in info
        
        # Test invalid agent
        info = orchestrator.get_agent_info("nonexistent")
        assert "error" in info
        assert info.get("error") is not None
    
    @pytest.mark.asyncio
    async def test_agent_type_mapping(self):
        """Test legacy agent type mappings."""
        orchestrator = AgentOrchestrator()
        
        # Test AG2 agent (direct test)
        response = await orchestrator.execute_task(
            agent_type="ag2",
            task="Test task"
        )
        assert isinstance(response, AgentResponse)
        
        # Test autogen -> ag2 mapping
        response = await orchestrator.execute_task(
            agent_type="autogen",
            task="Test task"
        )
        # Should either succeed or fail gracefully
        assert isinstance(response, AgentResponse)
    
    @pytest.mark.asyncio
    async def test_fallback_behavior(self):
        """Test fallback behavior when agent type doesn't exist."""
        orchestrator = AgentOrchestrator()
        
        # Test with unavailable agent type
        response = await orchestrator.execute_task(
            agent_type="nonexistent",
            task="Test task"
        )
        
        assert isinstance(response, AgentResponse)
        assert response.success is False
        assert response.error is not None


class TestPraisonAIAgent:
    """Test PraisonAI agent specifically."""
    
    def test_praisonai_agent_initialization(self):
        """Test PraisonAI agent initialization."""
        agent = PraisonAIAgent()
        assert agent.name == "praisonai"
        # Available status depends on whether praisonaiagents is installed
    
    @pytest.mark.asyncio
    async def test_praisonai_agent_execution_unavailable(self):
        """Test PraisonAI agent when unavailable."""
        agent = PraisonAIAgent()
        if not agent.available:
            response = await agent.execute("Test task")
            assert response.success is False
            assert response.error is not None
            assert "not available" in str(response.error)


class TestCrewAIAgent:
    """Test CrewAI agent specifically."""
    
    def test_crewai_agent_initialization(self):
        """Test CrewAI agent initialization."""
        agent = CrewAIAgent()
        assert agent.name == "crewai"
        # Available status depends on whether crewai is installed
    
    @pytest.mark.asyncio
    async def test_crewai_agent_execution_unavailable(self):
        """Test CrewAI agent when unavailable."""
        agent = CrewAIAgent()
        if not agent.available:
            response = await agent.execute("Test task")
            assert response.success is False
            assert response.error is not None
            assert "not available" in str(response.error)


class TestAG2Agent:
    """Test AG2/AutoGen agent specifically."""
    
    def test_ag2_agent_initialization(self):
        """Test AG2 agent initialization."""
        agent = AG2Agent()
        assert agent.name == "ag2"
        # Available status depends on whether autogen is installed
    
    @pytest.mark.asyncio
    async def test_ag2_agent_execution_unavailable(self):
        """Test AG2 agent when unavailable."""
        agent = AG2Agent()
        if not agent.available:
            response = await agent.execute("Test task")
            assert response.success is False
            assert response.error is not None
            assert "not available" in str(response.error)


# Integration test for basic functionality
@pytest.mark.asyncio
async def test_basic_agent_execution():
    """Test basic agent execution with all available agents."""
    orchestrator = AgentOrchestrator()
    available_agents = orchestrator.get_available_agents()
    
    # Test each available agent
    for agent_type in available_agents:
        response = await orchestrator.execute_task(
            agent_type=agent_type,
            task="Hello, this is a test task",
            context={"test": True}
        )
        
        assert isinstance(response, AgentResponse)
        assert response.execution_time_ms is not None
        assert response.execution_time_ms >= 0
        
        # Either successful execution or graceful failure
        if response.success:
            assert response.result is not None
            assert response.metadata is not None
        else:
            assert response.error is not None 