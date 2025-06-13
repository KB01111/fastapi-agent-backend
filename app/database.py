"""Database configuration and models using Supabase."""

import asyncio
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Text, JSON, Boolean
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from supabase import create_client, Client
import structlog

from app.config import settings

logger = structlog.get_logger()

# SQLAlchemy setup
Base = declarative_base()

# Initialize database components with error handling
engine = None
AsyncSessionLocal = None
supabase = None

try:
    engine = create_async_engine(
        settings.database_url,
        echo=settings.debug,
        pool_size=10,
        max_overflow=20
    )
    AsyncSessionLocal = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    logger.info("Database engine initialized successfully")
except Exception as e:
    logger.warning(f"Failed to initialize database engine: {e}")

try:
    # Supabase client
    supabase: Client = create_client(
        settings.supabase_url,
        settings.supabase_anon_key
    )
    logger.info("Supabase client initialized successfully")
except Exception as e:
    logger.warning(f"Failed to initialize Supabase client: {e}")


class AgentSession(Base):
    """Model for storing agent conversation sessions."""
    
    __tablename__ = "agent_sessions"
    
    id = Column(String(255), primary_key=True)
    user_id = Column(String(255), nullable=False, index=True)
    session_name = Column(String(255), nullable=True)
    created_at = Column(DateTime(), default=datetime.utcnow)
    updated_at = Column(DateTime(), default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean(), default=True)
    meta_data = Column(JSON(), default=dict)


class AgentMessage(Base):
    """Model for storing individual agent messages."""
    
    __tablename__ = "agent_messages"
    
    id = Column(String(255), primary_key=True)
    session_id = Column(String(255), nullable=False, index=True)
    user_id = Column(String(255), nullable=False, index=True)
    message_type = Column(String(50), nullable=False)  # 'user', 'assistant', 'system'
    content = Column(Text(), nullable=False)
    created_at = Column(DateTime(), default=datetime.utcnow)
    meta_data = Column(JSON(), default=dict)
    token_count = Column(Integer(), default=0)


class AgentExecution(Base):
    """Model for storing agent execution logs and metrics."""
    
    __tablename__ = "agent_executions"
    
    id = Column(String(255), primary_key=True)
    session_id = Column(String(255), nullable=False, index=True)
    user_id = Column(String(255), nullable=False, index=True)
    agent_type = Column(String(50), nullable=False)  # 'praisonai', 'crewai', 'autogen'
    task = Column(Text(), nullable=False)
    status = Column(String(50), nullable=False)  # 'pending', 'running', 'completed', 'failed'
    result = Column(Text(), nullable=True)
    error_message = Column(Text(), nullable=True)
    execution_time_ms = Column(Integer(), nullable=True)
    token_usage = Column(JSON(), default=dict)
    created_at = Column(DateTime(), default=datetime.utcnow)
    completed_at = Column(DateTime(), nullable=True)
    meta_data = Column(JSON(), default=dict)


async def get_db():
    """
    FastAPI dependency to get database session.
    
    Yields:
        AsyncSession: Database session or None if not available
    """
    if AsyncSessionLocal is None:
        logger.warning("Database not available")
        yield None
        return
        
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_database():
    """Initialize database tables."""
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables initialized successfully")
    except Exception as e:
        logger.error("Failed to initialize database", error=str(e))
        raise


class DatabaseManager:
    """Manager class for database operations."""
    
    def __init__(self):
        self.supabase = supabase
    
    async def create_session(self, user_id: str, session_name: Optional[str] = None) -> str:
        """
        Create a new agent session.
        
        Args:
            user_id: User identifier
            session_name: Optional session name
            
        Returns:
            str: Session ID
        """
        import uuid
        session_id = str(uuid.uuid4())
        
        async with AsyncSessionLocal() as db:
            session = AgentSession(
                id=session_id,
                user_id=user_id,
                session_name=session_name
            )
            db.add(session)
            await db.commit()
            
        logger.info("Created new agent session", 
                   session_id=session_id, user_id=user_id)
        return session_id
    
    async def save_message(
        self,
        session_id: str,
        user_id: str,
        message_type: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        token_count: int = 0
    ) -> str:
        """
        Save a message to the database.
        
        Args:
            session_id: Session identifier
            user_id: User identifier
            message_type: Type of message ('user', 'assistant', 'system')
            content: Message content
            metadata: Optional metadata
            token_count: Token count for the message
            
        Returns:
            str: Message ID
        """
        import uuid
        message_id = str(uuid.uuid4())
        
        async with AsyncSessionLocal() as db:
            message = AgentMessage(
                id=message_id,
                session_id=session_id,
                user_id=user_id,
                message_type=message_type,
                content=content,
                metadata=metadata or {},
                token_count=token_count
            )
            db.add(message)
            await db.commit()
            
        logger.info("Saved message", 
                   message_id=message_id, session_id=session_id, type=message_type)
        return message_id
    
    async def save_execution(
        self,
        session_id: str,
        user_id: str,
        agent_type: str,
        task: str,
        status: str = "pending",
        result: Optional[str] = None,
        error_message: Optional[str] = None,
        execution_time_ms: Optional[int] = None,
        token_usage: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Save an agent execution record.
        
        Args:
            session_id: Session identifier
            user_id: User identifier
            agent_type: Type of agent used
            task: Task description
            status: Execution status
            result: Execution result
            error_message: Error message if failed
            execution_time_ms: Execution time in milliseconds
            token_usage: Token usage statistics
            metadata: Optional metadata
            
        Returns:
            str: Execution ID
        """
        import uuid
        execution_id = str(uuid.uuid4())
        
        async with AsyncSessionLocal() as db:
            execution = AgentExecution(
                id=execution_id,
                session_id=session_id,
                user_id=user_id,
                agent_type=agent_type,
                task=task,
                status=status,
                result=result,
                error_message=error_message,
                execution_time_ms=execution_time_ms,
                token_usage=token_usage or {},
                metadata=metadata or {}
            )
            db.add(execution)
            await db.commit()
            
        logger.info("Saved execution", 
                   execution_id=execution_id, session_id=session_id, agent_type=agent_type)
        return execution_id


# Global database manager instance
db_manager = DatabaseManager() 