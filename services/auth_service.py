"""
Authentication Service for Hospital Scheduling System
Handles user authentication, token management, and credential extraction
"""

import requests
import json
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Tuple, List
import logging
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class AuthCredentials:
    """Data class to hold authentication credentials"""
    email: str
    password: str
    tenant_domain: Optional[str] = None
    location_id: Optional[str] = None
    remember_me: bool = True

@dataclass
class TenantLocation:
    """Data class for tenant location information"""
    location_id: str
    location_name: str
    location_type: str
    is_primary: bool
    is_user_primary: bool
    address: str
    city: str
    state: str
    country: str
    is_active: bool

@dataclass
class TenantInfo:
    """Data class for tenant information"""
    tenant_id: str
    tenant_name: str
    role: str
    user_roles: List[str]
    is_primary: bool
    status: str
    subscription_plan: str
    accessible_locations: List[TenantLocation]
    domain: str
    joined_at: str

@dataclass
class UserContext:
    """Data class for complete user context"""
    user_type: str
    current_tenant_id: str
    current_tenant_name: str
    current_location_id: str
    current_location_name: str
    current_role: str
    accessible_tenants: List[TenantInfo]
    has_multiple_tenants: bool
    has_multiple_locations: bool
    session_id: str

@dataclass
class TokenInfo:
    """Data class to hold token information"""
    access_token: str
    refresh_token: Optional[str]
    token_type: str
    expires_in: int
    tenant_id: str
    business_location_id: str
    user_id: str
    expires_at: datetime
    user_context: Optional[UserContext] = None


def _mask_token_for_log(token: str, visible: int = 6) -> str:
    if not token:
        return '<empty>'
    prefix = token[:visible]
    if len(token) <= visible * 2:
        return f"{prefix}..."
    suffix = token[-visible:]
    return f"{prefix}...{suffix}"

class AuthenticationService:
    """
    Handles authentication with the Hospital API
    Provides token management, credential extraction, and session handling
    """
    
    def __init__(self, auth_base_url: str = "https://dev-hv-auth.azurewebsites.net"):
        """
        Initialize the authentication service
        
        Args:
            auth_base_url: Base URL for authentication API
        """
        self.auth_base_url = auth_base_url
        self.login_endpoint = f"{auth_base_url}/api/auth/login"
        self.user_context_endpoint = f"{auth_base_url}/api/Auth/user-context"
        self.current_token_info: Optional[TokenInfo] = None
        
    def decode_jwt_token_simple(self, token: str) -> Dict:
        """
        Simple JWT token decoder that extracts payload without verification
        
        Args:
            token: JWT token string
            
        Returns:
            Decoded token claims
        """
        try:
            # JWT tokens have 3 parts separated by dots: header.payload.signature
            parts = token.split('.')
            if len(parts) != 3:
                raise ValueError("Invalid JWT token format")
            
            # Decode the payload (second part)
            import base64
            payload = parts[1]
            
            # Add padding if needed (JWT base64 encoding may not have padding)
            missing_padding = len(payload) % 4
            if missing_padding:
                payload += '=' * (4 - missing_padding)
            
            # Decode base64
            decoded_bytes = base64.urlsafe_b64decode(payload)
            decoded = json.loads(decoded_bytes.decode('utf-8'))
            
            return decoded
        except Exception as e:
            logger.error(f"Failed to decode JWT token: {str(e)}")
            raise ValueError(f"Invalid JWT token: {str(e)}")
    
    def parse_user_context(self, context_data: Dict) -> UserContext:
        """
        Parse user context response into UserContext object
        
        Args:
            context_data: Raw user context response
            
        Returns:
            UserContext object
        """
        # Parse accessible tenants
        accessible_tenants = []
        for tenant_data in context_data.get("accessibleTenants", []):
            # Parse accessible locations for this tenant
            locations = []
            for loc_data in tenant_data.get("accessibleLocations", []):
                location = TenantLocation(
                    location_id=loc_data.get("locationId", ""),
                    location_name=loc_data.get("locationName", ""),
                    location_type=loc_data.get("locationType", ""),
                    is_primary=loc_data.get("isPrimary", False),
                    is_user_primary=loc_data.get("isUserPrimary", False),
                    address=loc_data.get("address", ""),
                    city=loc_data.get("city", ""),
                    state=loc_data.get("state", ""),
                    country=loc_data.get("country", ""),
                    is_active=loc_data.get("isActive", True)
                )
                locations.append(location)
            
            tenant = TenantInfo(
                tenant_id=tenant_data.get("tenantId", ""),
                tenant_name=tenant_data.get("tenantName", ""),
                role=tenant_data.get("role", ""),
                user_roles=tenant_data.get("userRoles", []),
                is_primary=tenant_data.get("isPrimary", False),
                status=tenant_data.get("status", ""),
                subscription_plan=tenant_data.get("subscriptionPlan", ""),
                accessible_locations=locations,
                domain=tenant_data.get("domain", ""),
                joined_at=tenant_data.get("joinedAt", "")
            )
            accessible_tenants.append(tenant)
        
        current_context = context_data.get("currentContext", {})
        
        return UserContext(
            user_type=context_data.get("userType", ""),
            current_tenant_id=current_context.get("tenantId", ""),
            current_tenant_name=current_context.get("tenantName", ""),
            current_location_id=current_context.get("locationId", ""),
            current_location_name=current_context.get("locationName", ""),
            current_role=current_context.get("role", ""),
            accessible_tenants=accessible_tenants,
            has_multiple_tenants=context_data.get("hasMultipleTenants", False),
            has_multiple_locations=context_data.get("hasMultipleLocations", False),
            session_id=context_data.get("sessionId", "")
        )

    def fetch_user_context(self, access_token: str) -> UserContext:
        """
        Fetch complete user context including all accessible tenants and locations
        
        Args:
            access_token: Access token from login
            
        Returns:
            UserContext object
            
        Raises:
            Exception: If user context fetch fails
        """
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json"
        }
        
        try:
            masked = _mask_token_for_log(access_token)
            logger.info(f"Fetching user context with token {masked}")
            response = requests.get(
                self.user_context_endpoint,
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            
            context_data = response.json()
            user_context = self.parse_user_context(context_data)
            
            logger.info(f"User context fetched successfully for {user_context.current_tenant_name}")
            logger.info(f"Available tenants: {len(user_context.accessible_tenants)}")
            
            return user_context
            
        except requests.RequestException as e:
            logger.error(f"User context request failed: {str(e)}")
            raise Exception(f"Failed to fetch user context: {str(e)}")
        except Exception as e:
            logger.error(f"User context error: {str(e)}")
            raise Exception(f"User context error: {str(e)}")

    def authenticate(self, credentials: AuthCredentials) -> TokenInfo:
        """
        Authenticate user and return token information
        
        Args:
            credentials: User credentials
            
        Returns:
            TokenInfo object containing authentication details
            
        Raises:
            Exception: If authentication fails
        """
        payload = {
            "email": credentials.email,
            "password": credentials.password,
            "rememberMe": credentials.remember_me
        }
        
        # Add optional fields if provided
        if credentials.tenant_domain:
            payload["tenantDomain"] = credentials.tenant_domain
        if credentials.location_id:
            payload["locationId"] = credentials.location_id
            
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        try:
            logger.info(f"Authenticating user: {credentials.email}")
            response = requests.post(
                self.login_endpoint,
                json=payload,
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            
            auth_response = response.json()
            
            # Extract token and other information from response
            access_token = auth_response.get('accessToken')
            refresh_token = auth_response.get('refreshToken')
            token_type = auth_response.get('tokenType', 'Bearer')
            expires_in = auth_response.get('expiresIn', 3600)
            
            if not access_token:
                logger.error(f"No access token found in response: {auth_response}")
                raise ValueError("No access token found in authentication response")
            
            # Calculate expiration time
            expires_at = datetime.now() + timedelta(seconds=expires_in)
            
            # Get tenant and location info from response
            tenant_context = auth_response.get('tenantContext', {})
            tenant_id = tenant_context.get('tenantId')
            business_location_id = tenant_context.get('currentBusinessLocationId') or tenant_context.get('locationId')
            
            # Get user info
            user_info = auth_response.get('user', {})
            user_id = user_info.get('id')
            
            # Fetch complete user context
            user_context = self.fetch_user_context(access_token)
            
            # Use user context for more accurate tenant/location info if available
            if user_context:
                tenant_id = user_context.current_tenant_id or tenant_id
                business_location_id = user_context.current_location_id or business_location_id
            
            # Validate required fields
            if not tenant_id:
                raise ValueError("tenant_id not found in response")
            if not business_location_id:
                raise ValueError("business_location_id not found in response")
            if not user_id:
                raise ValueError("user_id not found in response")
            
            token_info = TokenInfo(
                access_token=access_token,
                refresh_token=refresh_token,
                token_type=token_type,
                expires_in=expires_in,
                tenant_id=tenant_id,
                business_location_id=business_location_id,
                user_id=user_id,
                expires_at=expires_at,
                user_context=user_context
            )
            
            self.current_token_info = token_info
            logger.info(f"Authentication successful for user: {credentials.email}")
            logger.info(f"Tenant ID: {tenant_id}, Location ID: {business_location_id}")
            
            return token_info
            
        except requests.RequestException as e:
            logger.error(f"Authentication request failed: {str(e)}")
            raise Exception(f"Authentication failed: {str(e)}")
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            raise Exception(f"Authentication error: {str(e)}")
    
    def initialize_with_access_token(self, access_token: str, token_type: str = "Bearer") -> TokenInfo:
        """Initialize the authentication service using an existing bearer token."""

        if not access_token:
            raise ValueError("Access token is required to initialize authentication service")

        logger.info("Initializing authentication context from provided access token")

        token_claims: Dict[str, Any] = {}
        expires_at = datetime.now() + timedelta(minutes=55)
        user_id: Optional[str] = None
        tenant_id: Optional[str] = None
        business_location_id: Optional[str] = None

        try:
            token_claims = self.decode_jwt_token_simple(access_token)

            exp_timestamp = token_claims.get("exp")
            if exp_timestamp:
                expires_at = datetime.fromtimestamp(int(exp_timestamp))

            user_id = (
                token_claims.get("sub")
                or token_claims.get("nameid")
                or token_claims.get("userId")
                or token_claims.get("oid")
            )

            tenant_id = (
                token_claims.get("tenantId")
                or token_claims.get("tenant_id")
                or token_claims.get("tid")
                or token_claims.get("tenant")
            )

            business_location_id = (
                token_claims.get("businessLocationId")
                or token_claims.get("currentBusinessLocationId")
                or token_claims.get("locationId")
            )

        except Exception as decode_error:
            logger.warning(f"Failed to decode JWT access token: {decode_error}")

        user_context: Optional[UserContext] = None
        try:
            user_context = self.fetch_user_context(access_token)
            if user_context:
                tenant_id = user_context.current_tenant_id or tenant_id
                business_location_id = user_context.current_location_id or business_location_id

                if not user_id and token_claims:
                    user_id = token_claims.get("sub") or token_claims.get("nameid")

        except Exception as context_error:
            logger.error(f"Unable to fetch user context using provided token: {context_error}")
            raise

        if not tenant_id and user_context and user_context.accessible_tenants:
            tenant_id = user_context.accessible_tenants[0].tenant_id

        if not business_location_id and user_context and user_context.accessible_tenants:
            first_tenant = user_context.accessible_tenants[0]
            if first_tenant.accessible_locations:
                business_location_id = first_tenant.accessible_locations[0].location_id

        if not tenant_id:
            raise ValueError("Tenant ID could not be resolved from token or user context")

        if not business_location_id:
            raise ValueError("Location ID could not be resolved from token or user context")

        if not user_id:
            raise ValueError("User ID could not be resolved from token")

        expires_in = max(int((expires_at - datetime.now()).total_seconds()), 0)

        token_info = TokenInfo(
            access_token=access_token,
            refresh_token=None,
            token_type=token_type,
            expires_in=expires_in,
            tenant_id=tenant_id,
            business_location_id=business_location_id,
            user_id=user_id,
            expires_at=expires_at,
            user_context=user_context
        )

        self.current_token_info = token_info

        logger.info(
            "Authentication context initialized - tenant: %s, location: %s",
            tenant_id,
            business_location_id
        )

        return token_info

    def is_token_valid(self) -> bool:
        """
        Check if current token is still valid
        
        Returns:
            True if token is valid, False otherwise
        """
        if not self.current_token_info:
            return False
        
        # Check if token is expired (with 5-minute buffer)
        buffer_time = datetime.now() + timedelta(minutes=5)
        return self.current_token_info.expires_at > buffer_time
    
    def get_auth_headers(self) -> Dict[str, str]:
        """
        Get authorization headers for API requests
        
        Returns:
            Dictionary containing authorization headers
            
        Raises:
            Exception: If no valid token is available
        """
        if not self.current_token_info or not self.is_token_valid():
            raise Exception("No valid authentication token available. Please authenticate first.")
        
        return {
            "Authorization": f"{self.current_token_info.token_type} {self.current_token_info.access_token}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
    
    def get_all_accessible_tenants_and_locations(self) -> List[Dict[str, str]]:
        """
        Get all accessible tenant and location combinations
        
        Returns:
            List of dictionaries with tenant_id, tenant_name, location_id, location_name
        """
        if not self.current_token_info or not self.current_token_info.user_context:
            raise Exception("No user context available. Please authenticate first.")
        
        combinations = []
        user_context = self.current_token_info.user_context
        
        for tenant in user_context.accessible_tenants:
            for location in tenant.accessible_locations:
                combinations.append({
                    "tenant_id": tenant.tenant_id,
                    "tenant_name": tenant.tenant_name,
                    "location_id": location.location_id,
                    "location_name": location.location_name,
                    "is_current": (tenant.tenant_id == user_context.current_tenant_id and 
                                 location.location_id == user_context.current_location_id)
                })
        
        return combinations

    def get_credentials(self) -> Tuple[str, str]:
        """
        Get current tenant_id and business_location_id
        
        Returns:
            Tuple of (tenant_id, business_location_id)
            
        Raises:
            Exception: If no valid token is available
        """
        if not self.current_token_info or not self.is_token_valid():
            raise Exception("No valid authentication token available. Please authenticate first.")
        
        return (
            self.current_token_info.tenant_id,
            self.current_token_info.business_location_id
        )
    
    def refresh_token_if_needed(self, credentials: AuthCredentials) -> bool:
        """
        Refresh token if it's about to expire
        
        Args:
            credentials: User credentials for re-authentication
            
        Returns:
            True if token was refreshed, False if still valid
        """
        if self.is_token_valid():
            return False
        
        logger.info("Token expired or about to expire, refreshing...")
        self.authenticate(credentials)
        return True

# Convenience function for quick authentication
def authenticate_user(email: str, password: str, tenant_domain: str = None, location_id: str = None) -> AuthenticationService:
    """
    Convenience function to authenticate a user
    
    Args:
        email: User email
        password: User password
        tenant_domain: Optional tenant domain
        location_id: Optional location ID
        
    Returns:
        Authenticated AuthenticationService instance
    """
    auth_service = AuthenticationService()
    credentials = AuthCredentials(
        email=email,
        password=password,
        tenant_domain=tenant_domain,
        location_id=location_id
    )
    auth_service.authenticate(credentials)
    return auth_service

if __name__ == "__main__":
    # Example usage
    try:
        # Test authentication (replace with actual credentials)
        auth_service = authenticate_user(
            email="sailokesh7780@gmail.com",
            password="your_password_here"
        )
        
        print("Authentication successful!")
        print(f"Tenant ID: {auth_service.current_token_info.tenant_id}")
        print(f"Business Location ID: {auth_service.current_token_info.business_location_id}")
        print(f"Token expires at: {auth_service.current_token_info.expires_at}")
        
    except Exception as e:
        print(f"Authentication failed: {str(e)}")