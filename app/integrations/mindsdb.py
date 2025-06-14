
"""
MindsDB Integration Module

This module provides functionality to connect to and interact with MindsDB,
allowing the application to leverage machine learning capabilities.
"""

import asyncio
from typing import Dict, Any, Optional, List
import structlog
from pydantic import BaseModel

logger = structlog.get_logger(__name__)

class MindsDBConfig(BaseModel):
    """Configuration for MindsDB connection."""
    host: str
    port: int = 47334
    user: Optional[str] = None
    password: Optional[str] = None
    use_https: bool = True
    
    @property
    def connection_string(self) -> str:
        """Get the connection string for MindsDB."""
        protocol = "https" if self.use_https else "http"
        auth = f"{self.user}:{self.password}@" if self.user and self.password else ""
        return f"{protocol}://{auth}{self.host}:{self.port}"

class MindsDBClient:
    """Client for interacting with MindsDB."""
    
    def __init__(self, config: MindsDBConfig):
        self.config = config
        self.client = None
        self.available = False
        self._initialize()
    
    def _initialize(self):
        """Initialize the MindsDB client."""
        try:
            # Import mindsdb_sdk if available
            try:
                import mindsdb_sdk
                self.mindsdb_sdk = mindsdb_sdk
            except ImportError:
                logger.warning("mindsdb_sdk not installed. Using HTTP API fallback.")
                self.mindsdb_sdk = None
            
            # Initialize client based on available libraries
            if self.mindsdb_sdk:
                self.client = self.mindsdb_sdk.connect(
                    host=self.config.host,
                    port=self.config.port,
                    user=self.config.user,
                    password=self.config.password,
                    use_https=self.config.use_https
                )
            else:
                # Fallback to requests for HTTP API
                import requests
                self.client = requests.Session()
                # Test connection
                response = self.client.get(
                    f"{self.config.connection_string}/api/status",
                    timeout=5
                )
                if response.status_code != 200:
                    raise ConnectionError(f"Failed to connect to MindsDB: {response.text}")
            
            self.available = True
            logger.info("MindsDB client initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to initialize MindsDB client: {e}")
            self.available = False
    
    async def query(self, sql: str) -> Dict[str, Any]:
        """
        Execute a SQL query against MindsDB.
        
        Args:
            sql: SQL query to execute
            
        Returns:
            Dict containing query results
        """
        if not self.available:
            return {"error": "MindsDB client not available"}
        
        try:
            # Execute in a separate thread to avoid blocking
            loop = asyncio.get_event_loop()
            if self.mindsdb_sdk:
                result = await loop.run_in_executor(None, lambda: self.client.query(sql))
                return {"success": True, "data": result.fetch_all()}
            else:
                # HTTP API fallback
                response = await loop.run_in_executor(
                    None,
                    lambda: self.client.post(
                        f"{self.config.connection_string}/api/sql/query",
                        json={"query": sql},
                        timeout=30
                    )
                )
                if response.status_code != 200:
                    return {"error": f"Query failed: {response.text}"}
                return {"success": True, "data": response.json()}
        except Exception as e:
            logger.error(f"MindsDB query failed: {e}")
            return {"error": str(e)}
    
    async def get_models(self) -> List[Dict[str, Any]]:
        """Get list of available models in MindsDB."""
        result = await self.query("SHOW MODELS")
        if "error" in result:
            return []
        return result.get("data", [])
    
    async def predict(self, model_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make a prediction using a MindsDB model.
        
        Args:
            model_name: Name of the model to use
            data: Input data for prediction
            
        Returns:
            Dict containing prediction results
        """
        # Convert data to SQL WHERE clause format
        conditions = []
        for key, value in data.items():
            if isinstance(value, str):
                conditions.append(f"{key}='{value}'")
            else:
                conditions.append(f"{key}={value}")
        
        where_clause = " AND ".join(conditions)
        sql = f"SELECT * FROM {model_name} WHERE {where_clause}"
        
        return await self.query(sql)

# Factory function to create a client with configuration
def create_mindsdb_client(
    host: str,
    port: int = 47334,
    user: Optional[str] = None,
    password: Optional[str] = None,
    use_https: bool = True
) -> MindsDBClient:
    """
    Create a MindsDB client with the given configuration.
    
    Args:
        host: MindsDB host
        port: MindsDB port
        user: MindsDB username
        password: MindsDB password
        use_https: Whether to use HTTPS
        
    Returns:
        MindsDBClient instance
    """
    config = MindsDBConfig(
        host=host,
        port=port,
        user=user,
        password=password,
        use_https=use_https
    )
    return MindsDBClient(config)