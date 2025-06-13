"""
AI Agent Orchestration System

This module provides a unified interface for multiple AI agent frameworks
including PraisonAI, CrewAI, AG2/AutoGen, and direct LLM providers.
"""

import asyncio
import time
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, Optional, List

try:
    import structlog
    logger = structlog.get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

try:
    from pydantic import BaseModel
except ImportError:
    # Fallback to basic dataclass if pydantic not available
    from dataclasses import dataclass as BaseModel

@dataclass
class AgentResponse:
    """Standardized response format for all agents."""
    success: bool
    result: Optional[str] = None
    error: Optional[str] = None
    execution_time_ms: Optional[int] = None
    token_usage: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

class TaskOutput(BaseModel):
    """Structured output format for agent tasks."""
    title: str
    content: str
    summary: str
    key_points: List[str] = []
    metadata: Dict[str, Any] = {}

class BaseAgent(ABC):
    """Abstract base class for all AI agents."""
    
    def __init__(self, name: str):
        self.name = name
        self.available = False
        
    @abstractmethod
    async def execute(self, task: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """Execute a task using the agent."""
        pass
    
    def _measure_execution_time(self, start_time: float) -> int:
        """Calculate execution time in milliseconds."""
        return int((time.time() - start_time) * 1000)

class PraisonAIAgent(BaseAgent):
    """PraisonAI multi-agent framework implementation."""
    
    def __init__(self):
        super().__init__("praisonai")
        try:
            # Try different import patterns for PraisonAI
            try:
                from praisonaiagents import Agent, Task, PraisonAIAgents, Tools
                self.Agent = Agent
                self.Task = Task
                self.PraisonAIAgents = PraisonAIAgents
                self.Tools = Tools
            except ImportError:
                # Try alternative import patterns
                from praisonai import Agent, Task, PraisonAI
                self.Agent = Agent
                self.Task = Task
                self.PraisonAIAgents = PraisonAI
                self.Tools = None
            
            self.available = True
            logger.info("PraisonAI agent initialized successfully")
        except ImportError as e:
            logger.warning(f"PraisonAI not available: {e}")
        except Exception as e:
            logger.error(f"Failed to initialize PraisonAI agent: {e}")
    
    async def execute(self, task: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """Execute task using PraisonAI multi-agent system."""
        if not self.available:
            return AgentResponse(
                success=False,
                error="PraisonAI agent not available"
            )
        
        start_time = time.time()
        
        try:
            # Create analyst agent
            analyst = self.Agent(
                role="Task Analyst",
                goal="Analyze and complete the given task with structured output",
                backstory="Expert analyst capable of breaking down complex tasks and providing structured insights",
                tools=[self.Tools.internet_search] if hasattr(self.Tools, 'internet_search') else [],
                verbose=False
            )
            
            # Create task with structured output
            analysis_task = self.Task(
                description=f"Task: {task}\nContext: {context or 'No additional context provided'}\nProvide a comprehensive analysis with structured output.",
                expected_output="Structured analysis with title, content, summary, and key points",
                agent=analyst,
                output_pydantic=TaskOutput
            )
            
            # Create and run agents
            agents = self.PraisonAIAgents(
                agents=[analyst],
                tasks=[analysis_task],
                process="sequential",
                verbose=0
            )
            
            # Execute in a separate thread to avoid blocking
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(agents.start)
                result = future.result(timeout=60)  # 60 second timeout
            
            execution_time = self._measure_execution_time(start_time)
            
            # Extract structured output
            if hasattr(result, 'pydantic') and result.pydantic:
                structured_output = result.pydantic
                response_content = f"Title: {structured_output.title}\n\nContent: {structured_output.content}\n\nSummary: {structured_output.summary}"
                if structured_output.key_points:
                    response_content += f"\n\nKey Points:\n" + "\n".join(f"- {point}" for point in structured_output.key_points)
            else:
                response_content = str(result) if result else "No response generated"
            
            return AgentResponse(
                success=True,
                result=response_content,
                execution_time_ms=execution_time,
                token_usage={"framework": "praisonai"},
                metadata={"framework": "praisonai", "agents_used": 1}
            )
            
        except Exception as e:
            execution_time = self._measure_execution_time(start_time)
            logger.error(f"PraisonAI execution failed: {e}")
            return AgentResponse(
                success=False,
                error=str(e),
                execution_time_ms=execution_time
            )

class CrewAIAgent(BaseAgent):
    """CrewAI multi-agent framework implementation."""
    
    def __init__(self):
        super().__init__("crewai")
        try:
            from crewai import Agent, Task, Crew, Process
            # Skip SerperDevTool as it may not be available in newer versions
            self.Agent = Agent
            self.Task = Task
            self.Crew = Crew
            self.Process = Process
            self.available = True
            logger.info("CrewAI agent initialized successfully")
        except ImportError as e:
            logger.warning(f"CrewAI not available: {e}")
        except Exception as e:
            logger.error(f"Failed to initialize CrewAI agent: {e}")
    
    async def execute(self, task: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """Execute task using CrewAI multi-agent system."""
        if not self.available:
            return AgentResponse(
                success=False,
                error="CrewAI agent not available"
            )
        
        start_time = time.time()
        
        try:
            # Create researcher agent
            researcher = self.Agent(
                role='Research Analyst',
                goal='Conduct thorough research and analysis',
                backstory='Expert researcher with deep analytical skills',
                verbose=False,
                allow_delegation=False
            )
            
            # Create task
            research_task = self.Task(
                description=f"Research and analyze: {task}\nContext: {context or 'No additional context'}",
                agent=researcher,
                expected_output="Comprehensive analysis with insights and recommendations"
            )
            
            # Create crew
            crew = self.Crew(
                agents=[researcher],
                tasks=[research_task],
                process=self.Process.sequential,
                verbose=0
            )
            
            # Execute in a separate thread
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(crew.kickoff)
                result = future.result(timeout=60)
            
            execution_time = self._measure_execution_time(start_time)
            
            return AgentResponse(
                success=True,
                result=str(result),
                execution_time_ms=execution_time,
                token_usage={"framework": "crewai"},
                metadata={"framework": "crewai", "agents_used": 1}
            )
            
        except Exception as e:
            execution_time = self._measure_execution_time(start_time)
            logger.error(f"CrewAI execution failed: {e}")
            return AgentResponse(
                success=False,
                error=str(e),
                execution_time_ms=execution_time
            )

class AG2Agent(BaseAgent):
    """AG2/AutoGen multi-agent framework implementation."""
    
    def __init__(self):
        super().__init__("ag2")
        try:
            # Try different import patterns for different versions
            try:
                from autogen import ConversableAgent, GroupChat, GroupChatManager
                self.ConversableAgent = ConversableAgent
                self.GroupChat = GroupChat
                self.GroupChatManager = GroupChatManager
            except ImportError:
                # Try alternative import for newer versions
                from autogen.agentchat import ConversableAgent, GroupChat, GroupChatManager
                self.ConversableAgent = ConversableAgent
                self.GroupChat = GroupChat
                self.GroupChatManager = GroupChatManager
            
            self.available = True
            logger.info("AG2/AutoGen agent initialized successfully")
        except ImportError as e:
            logger.warning(f"AG2/AutoGen not available: {e}")
        except Exception as e:
            logger.error(f"Failed to initialize AG2/AutoGen agent: {e}")
    
    async def execute(self, task: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """Execute task using AG2/AutoGen conversation system."""
        if not self.available:
            return AgentResponse(
                success=False,
                error="AG2/AutoGen agent not available"
            )
        
        start_time = time.time()
        
        try:
            # Configure LLM
            llm_config = {
                "model": "gpt-3.5-turbo",
                "temperature": 0.7,
                "timeout": 60,
            }
            
            # Create assistant agent
            assistant = self.ConversableAgent(
                name="assistant",
                system_message="You are a helpful AI assistant that provides comprehensive analysis and insights.",
                llm_config=llm_config,
                human_input_mode="NEVER",
                max_consecutive_auto_reply=1
            )
            
            # Create user proxy
            user_proxy = self.ConversableAgent(
                name="user_proxy",
                system_message="You are a user proxy that initiates conversations.",
                llm_config=False,
                human_input_mode="NEVER",
                max_consecutive_auto_reply=0
            )
            
            # Execute conversation in a separate thread
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(
                    user_proxy.initiate_chat,
                    assistant,
                    message=f"Task: {task}\nContext: {context or 'No additional context'}"
                )
                result = future.result(timeout=60)
            
            execution_time = self._measure_execution_time(start_time)
            
            # Extract the last message from assistant
            chat_history = user_proxy.chat_messages.get(assistant, [])
            if chat_history:
                last_message = chat_history[-1].get('content', 'No response')
            else:
                last_message = "No response generated"
            
            return AgentResponse(
                success=True,
                result=last_message,
                execution_time_ms=execution_time,
                token_usage={"framework": "ag2"},
                metadata={"framework": "ag2", "agents_used": 2}
            )
            
        except Exception as e:
            execution_time = self._measure_execution_time(start_time)
            logger.error(f"AG2/AutoGen execution failed: {e}")
            return AgentResponse(
                success=False,
                error=str(e),
                execution_time_ms=execution_time
            )



class AgentOrchestrator:
    """Orchestrates multiple AI agents with fallback handling."""
    
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self._initialize_agents()
    
    def _initialize_agents(self):
        """Initialize only the core AI agent frameworks."""
        agent_classes = [
            ("praisonai", PraisonAIAgent),
            ("crewai", CrewAIAgent),
            ("ag2", AG2Agent),
        ]
        
        for agent_type, agent_class in agent_classes:
            try:
                agent = agent_class()
                self.agents[agent_type] = agent
                if agent.available:
                    logger.info(f"Agent '{agent_type}' initialized and available")
                else:
                    logger.warning(f"Agent '{agent_type}' initialized but not available")
            except Exception as e:
                logger.error(f"Failed to initialize agent '{agent_type}': {e}")
    
    def get_available_agents(self) -> List[str]:
        """Get list of available agent types."""
        return [
            agent_type for agent_type, agent in self.agents.items()
            if agent.available
        ]
    
    def get_agent_info(self, agent_type: str) -> Dict[str, Any]:
        """Get information about a specific agent."""
        if agent_type not in self.agents:
            return {"error": f"Agent type '{agent_type}' not found"}
        
        agent = self.agents[agent_type]
        return {
            "name": agent.name,
            "available": agent.available,
            "type": agent_type,
            "description": self._get_agent_description(agent_type)
        }
    
    def _get_agent_description(self, agent_type: str) -> str:
        """Get description for agent type."""
        descriptions = {
            "praisonai": "Multi-agent orchestration with structured outputs",
            "crewai": "Collaborative AI agents for complex tasks",
            "ag2": "AutoGen conversation-based multi-agent system"
        }
        return descriptions.get(agent_type, "Unknown agent type")
    
    async def execute_task(
        self, 
        agent_type: str, 
        task: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        """Execute a task using the specified agent type."""
        # Handle legacy agent type mappings
        agent_type_mapping = {
            "autogen": "ag2"    # Map autogen to ag2
        }
        agent_type = agent_type_mapping.get(agent_type, agent_type)
        
        if agent_type not in self.agents:
            return AgentResponse(
                success=False,
                error=f"Agent type '{agent_type}' not found"
            )
        
        agent = self.agents[agent_type]
        if not agent.available:
            # Fallback to mock agent if requested agent is not available
            logger.warning(f"Agent '{agent_type}' not available, falling back to mock")
            agent = self.agents.get("mock")
            if not agent or not agent.available:
                return AgentResponse(
                    success=False,
                    error=f"Agent '{agent_type}' not available and no fallback"
                )
        
        try:
            return await agent.execute(task, context)
        except Exception as e:
            logger.error(f"Agent execution failed: {e}")
            return AgentResponse(
                success=False,
                error=f"Agent execution failed: {str(e)}"
            )

# Global orchestrator instance
orchestrator = AgentOrchestrator() 