"""
Authentication middleware and context management
"""
from fastapi import HTTPException, Header
from dataclasses import dataclass
from typing import Optional, Dict, Any
import logging

from services.auth_service import AuthenticationService, TokenInfo
from services.scheduling_tools import create_scheduling_tools
from config import API_ENDPOINTS

logger = logging.getLogger(__name__)


@dataclass
class RequestContext:
    """Container for request context including auth and tools"""
    auth_service: AuthenticationService
    scheduling_tools: Dict[str, Any]
    token_info: TokenInfo
    tenant_id: str
    location_id: str
    access_token: str


def _require_bearer_token(authorization: Optional[str]) -> str:
    """Extract and validate Bearer token from Authorization header"""
    if not authorization:
        raise HTTPException(status_code=401, detail='Authorization header is required')
    if not authorization.lower().startswith('bearer '):
        raise HTTPException(status_code=401, detail='Authorization header must use Bearer scheme')
    token = authorization.split(' ', 1)[1].strip()
    if not token:
        raise HTTPException(status_code=401, detail='Bearer token value is missing')
    return token


async def get_request_context(authorization: str = Header(None)) -> RequestContext:
    """
    Dependency to extract and validate JWT token, initialize auth context and tools
    
    This function handles the complete authentication flow:
    1. Extracts Bearer token from Authorization header
    2. Validates token with authentication service
    3. Initializes scheduling tools with auth context
    4. Returns complete request context
    
    Args:
        authorization: Authorization header containing Bearer token
        
    Returns:
        RequestContext: Complete context with auth service, tools, and token info
        
    Raises:
        HTTPException: If authentication fails or token is invalid
    """
    access_token = _require_bearer_token(authorization)

    # Initialize auth service with token
    auth_service_instance = AuthenticationService(auth_base_url=API_ENDPOINTS['auth_base_url'])
    try:
        token_info = auth_service_instance.initialize_with_access_token(access_token)
    except Exception as exc:
        logger.error(f'Failed to initialize auth context from bearer token: {exc}')
        raise HTTPException(status_code=401, detail='Invalid or expired access token') from exc

    # Initialize scheduling tools with authenticated context
    tools = create_scheduling_tools(auth_service_instance)

    logger.info("Initialized request context", extra={
        'tenant_id': token_info.tenant_id,
        'location_id': token_info.business_location_id,
        'user_id': token_info.user_id
    })

    return RequestContext(
        auth_service=auth_service_instance,
        scheduling_tools=tools,
        token_info=token_info,
        tenant_id=token_info.tenant_id,
        location_id=token_info.business_location_id,
        access_token=access_token,
    )