"""Agent API endpoints for executing AI tasks."""

import uuid
from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.auth import get_current_user, ClerkUser
from app.agents import orchestrator, AgentResponse
from app.database import db_manager
from app.monitoring import monitor_execution_time, log_request_info, log_error, metrics_collector
import structlog

logger = structlog.get_logger()

router = APIRouter(prefix="/v1", tags=["agent"])


class AgentRequest(BaseModel):
    """Request model for agent execution."""
    task: str = Field(..., description="Task description for the agent to execute")
    agent_type: str = Field(default="praisonai", description="Type of agent to use (praisonai, crewai, ag2)")
    session_id: Optional[str] = Field(None, description="Optional session ID to continue conversation")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Optional context for execution")


class AgentResponseModel(BaseModel):
    """Response model for agent execution."""
    success: bool
    result: Optional[str] = None
    error: Optional[str] = None
    execution_time_ms: Optional[int] = None
    session_id: str
    message_id: str
    agent_type: str
    metadata: Optional[Dict[str, Any]] = None


class SessionResponse(BaseModel):
    """Response model for session creation."""
    session_id: str
    created_at: str


class AgentInfoResponse(BaseModel):
    """Response model for agent information."""
    available_agents: list[str]
    agent_details: Dict[str, Dict[str, Any]]


@router.post("/answer", response_model=AgentResponseModel)
@monitor_execution_time("agent_answer_endpoint")
async def answer(
    request: AgentRequest,
    current_user: ClerkUser = Depends(get_current_user)
) -> AgentResponseModel:
    """
    Main agent endpoint for executing AI tasks.
    
    This is the primary endpoint that clients will call to get AI agent responses.
    Supports multiple agent types and maintains conversation sessions.
    
    Args:
        request: Agent request with task and configuration
        current_user: Authenticated user from Clerk JWT
        
    Returns:
        AgentResponseModel: Agent execution result
    """
    request_id = str(uuid.uuid4())
    
    try:
        # Log request info
        log_request_info(
            request_id=request_id,
            user_id=current_user.user_id,
            agent_type=request.agent_type,
            task_length=len(request.task),
            session_id=request.session_id
        )
        
        # Create or use existing session
        if request.session_id:
            session_id = request.session_id
            logger.info("Using existing session", session_id=session_id, user_id=current_user.user_id)
        else:
            session_id = await db_manager.create_session(
                user_id=current_user.user_id,
                session_name=f"Agent Task - {request.task[:50]}..."
            )
            logger.info("Created new session", session_id=session_id, user_id=current_user.user_id)
        
        # Save user message to database
        await db_manager.save_message(
            session_id=session_id,
            user_id=current_user.user_id,
            message_type="user",
            content=request.task,
            metadata={"agent_type": request.agent_type, "context": request.context}
        )
        
        # Execute agent task
        agent_response: AgentResponse = await orchestrator.execute_task(
            task=request.task,
            agent_type=request.agent_type,
            context=request.context
        )
        
        # Record execution metrics
        metrics_collector.record_agent_execution(
            agent_type=request.agent_type,
            status="success" if agent_response.success else "failure",
            duration=agent_response.execution_time_ms / 1000 if agent_response.execution_time_ms else None,
            token_usage=agent_response.token_usage
        )
        
        # Save agent response to database
        message_id = await db_manager.save_message(
            session_id=session_id,
            user_id=current_user.user_id,
            message_type="assistant",
            content=agent_response.result or agent_response.error or "No response",
            metadata={
                "agent_type": request.agent_type,
                "execution_time_ms": agent_response.execution_time_ms,
                "success": agent_response.success,
                **(agent_response.metadata or {})
            },
            token_count=agent_response.token_usage.get("total", 0) if agent_response.token_usage else 0
        )
        
        # Save execution record
        await db_manager.save_execution(
            session_id=session_id,
            user_id=current_user.user_id,
            agent_type=request.agent_type,
            task=request.task,
            status="completed" if agent_response.success else "failed",
            result=agent_response.result,
            error_message=agent_response.error,
            execution_time_ms=agent_response.execution_time_ms,
            token_usage=agent_response.token_usage,
            metadata=agent_response.metadata
        )
        
        logger.info("Agent task completed", 
                   request_id=request_id,
                   session_id=session_id,
                   success=agent_response.success,
                   execution_time_ms=agent_response.execution_time_ms)
        
        return AgentResponseModel(
            success=agent_response.success,
            result=agent_response.result,
            error=agent_response.error,
            execution_time_ms=agent_response.execution_time_ms,
            session_id=session_id,
            message_id=message_id,
            agent_type=request.agent_type,
            metadata=agent_response.metadata
        )
        
    except Exception as e:
        # Log error
        log_error(e, context={
            "request_id": request_id,
            "user_id": current_user.user_id,
            "agent_type": request.agent_type,
            "session_id": request.session_id
        })
        
        # Record failed execution
        metrics_collector.record_agent_execution(
            agent_type=request.agent_type,
            status="error"
        )
        
        logger.error("Agent task failed", 
                    request_id=request_id,
                    error=str(e))
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent execution failed: {str(e)}"
        )


@router.post("/sessions", response_model=SessionResponse)
async def create_session(
    session_name: Optional[str] = None,
    current_user: ClerkUser = Depends(get_current_user)
) -> SessionResponse:
    """
    Create a new agent conversation session.
    
    Args:
        session_name: Optional name for the session
        current_user: Authenticated user from Clerk JWT
        
    Returns:
        SessionResponse: Created session information
    """
    try:
        session_id = await db_manager.create_session(
            user_id=current_user.user_id,
            session_name=session_name
        )
        
        logger.info("Session created", 
                   session_id=session_id,
                   user_id=current_user.user_id,
                   session_name=session_name)
        
        return SessionResponse(
            session_id=session_id,
            created_at=str(uuid.uuid1().time)  # Simple timestamp
        )
        
    except Exception as e:
        log_error(e, context={
            "user_id": current_user.user_id,
            "session_name": session_name
        })
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create session: {str(e)}"
        )


@router.get("/agents", response_model=AgentInfoResponse)
async def get_agents(
    current_user: ClerkUser = Depends(get_current_user)
) -> AgentInfoResponse:
    """
    Get information about available agents.
    
    Args:
        current_user: Authenticated user from Clerk JWT
        
    Returns:
        AgentInfoResponse: Available agents and their details
    """
    try:
        available_agents = orchestrator.get_available_agents()
        agent_details = orchestrator.get_agent_info()
        
        logger.info("Agent info requested", 
                   user_id=current_user.user_id,
                   available_agents=available_agents)
        
        return AgentInfoResponse(
            available_agents=available_agents,
            agent_details=agent_details
        )
        
    except Exception as e:
        log_error(e, context={"user_id": current_user.user_id})
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get agent info: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring.
    
    Returns:
        dict: Health status
    """
    return {
        "status": "healthy",
        "service": "fastapi-agent-backend",
        "version": "1.0.0"
    } 