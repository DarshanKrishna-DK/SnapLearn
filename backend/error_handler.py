"""
Comprehensive Error Handling for SnapLearn API
"""

import logging
import traceback
import asyncio
from typing import Any, Dict, Optional, Callable
from functools import wraps
from fastapi import HTTPException
from datetime import datetime

logger = logging.getLogger(__name__)

class APIError(Exception):
    def __init__(self, message: str, status_code: int = 500, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details or {}

class TimeoutError(APIError):
    def __init__(self, operation: str, timeout_seconds: float):
        super().__init__(
            f"Operation '{operation}' timed out after {timeout_seconds} seconds",
            status_code=408
        )

class ServiceUnavailableError(APIError):
    def __init__(self, service: str):
        super().__init__(
            f"Service '{service}' is temporarily unavailable",
            status_code=503
        )

def handle_api_errors(timeout_seconds: float = None):
    """Decorator for comprehensive API error handling - NO TIMEOUTS as requested by user"""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            operation_name = func.__name__
            start_time = datetime.now()
            
            try:
                # NO TIMEOUT - User specifically requested removal of all timeouts to fix timeout issues
                result = await func(*args, **kwargs)
                
                # Log successful operations
                duration = (datetime.now() - start_time).total_seconds()
                logger.info(f"Operation '{operation_name}' completed in {duration:.2f}s")
                
                return result
                
            except HTTPException:
                # Re-raise HTTP exceptions as-is
                raise
            
            except APIError as e:
                logger.error(f"API error in '{operation_name}': {e.message}")
                raise HTTPException(status_code=e.status_code, detail=e.message)
            
            except Exception as e:
                # Log full traceback for debugging
                error_trace = traceback.format_exc()
                logger.error(f"Unexpected error in '{operation_name}': {str(e)}\n{error_trace}")
                
                # Return user-friendly error
                raise HTTPException(
                    status_code=500,
                    detail=f"An error occurred in {operation_name}. Please try again."
                )
        
        return wrapper
    return decorator

def safe_execute(func: Callable, fallback_value: Any = None, log_errors: bool = True):
    """Safely execute a function with error handling"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if log_errors:
                logger.error(f"Error in {func.__name__}: {e}")
            return fallback_value
    return wrapper

async def safe_execute_async(func: Callable, fallback_value: Any = None, log_errors: bool = True):
    """Safely execute an async function with error handling"""
    try:
        return await func()
    except Exception as e:
        if log_errors:
            logger.error(f"Error in async operation: {e}")
        return fallback_value

def create_error_response(error_type: str, message: str, **kwargs) -> Dict[str, Any]:
    """Create standardized error response"""
    return {
        "error": error_type,
        "message": message,
        "timestamp": datetime.now().isoformat(),
        **kwargs
    }

def create_fallback_analytics() -> Dict[str, Any]:
    """Create fallback analytics data when real data fails"""
    return {
        "total_sessions": 0,
        "total_questions": 0,
        "average_session_duration": 0,
        "skill_mastery": {},
        "learning_progress": [],
        "recent_activities": [],
        "recommendations": [
            "Practice basic arithmetic",
            "Review geometry concepts",
            "Try interactive video lessons"
        ],
        "error": "analytics_temporarily_unavailable",
        "message": "Analytics data is temporarily unavailable. Default values shown."
    }