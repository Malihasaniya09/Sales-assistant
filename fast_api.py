"""
REST API Module: AI Sales Assistant with Guardrails
FastAPI-based REST endpoints for the refrigerator sales chatbot
"""

from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, List
import os
import uvicorn
from dotenv import load_dotenv

# Import from your existing modules
from api import (
    SecureSalesAssistant, 
    get_api_key_from_env,
    get_security_features,
    CreativeResponseHandler
)
from assist import ensure_catalog_exists, get_catalog_stats

# Load environment
load_dotenv()

# ====================
# FASTAPI APP SETUP
# ====================

app = FastAPI(
    title="AI Refrigerator Sales Assistant API",
    description="Secure REST API with Guardrails AI protection",
    version="3.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ====================
# REQUEST/RESPONSE MODELS
# ====================

class ChatRequest(BaseModel):
    """Chat request model"""
    message: str = Field(..., min_length=1, max_length=1000, description="User message")
    session_id: Optional[str] = Field(None, description="Session ID for conversation context")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "I need a refrigerator for a family of 4",
                "session_id": "user_12345"
            }
        }

class ChatResponse(BaseModel):
    """Chat response model"""
    response: str = Field(..., description="AI assistant response")
    session_id: str = Field(..., description="Session ID")
    message_count: int = Field(..., description="Total messages in session")
    security_validated: bool = Field(True, description="Security validation status")

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    security_enabled: bool
    catalog_loaded: bool

class SessionInfo(BaseModel):
    """Session information"""
    session_id: str
    message_count: int
    active: bool

class ErrorResponse(BaseModel):
    """Error response model"""
    error: str
    detail: Optional[str] = None

# ====================
# SESSION MANAGEMENT
# ====================

class SessionManager:
    """Manage multiple chat sessions"""
    def __init__(self):
        self.sessions: Dict[str, SecureSalesAssistant] = {}
        self.message_counts: Dict[str, int] = {}
    
    def get_or_create_session(self, session_id: str, api_key: str) -> SecureSalesAssistant:
        """Get existing session or create new one"""
        if session_id not in self.sessions:
            pdf_path = ensure_catalog_exists()
            self.sessions[session_id] = SecureSalesAssistant(pdf_path, api_key)
            self.message_counts[session_id] = 0
        return self.sessions[session_id]
    
    def increment_message_count(self, session_id: str):
        """Increment message count for session"""
        if session_id in self.message_counts:
            self.message_counts[session_id] += 1
        else:
            self.message_counts[session_id] = 1
    
    def get_message_count(self, session_id: str) -> int:
        """Get message count for session"""
        return self.message_counts.get(session_id, 0)
    
    def clear_session(self, session_id: str) -> bool:
        """Clear a specific session"""
        if session_id in self.sessions:
            self.sessions[session_id].clear_memory()
            del self.sessions[session_id]
            self.message_counts[session_id] = 0
            return True
        return False
    
    def list_sessions(self) -> List[SessionInfo]:
        """List all active sessions"""
        return [
            SessionInfo(
                session_id=sid,
                message_count=self.message_counts.get(sid, 0),
                active=True
            )
            for sid in self.sessions.keys()
        ]

# Global session manager
session_manager = SessionManager()

# ====================
# DEPENDENCY INJECTION
# ====================

def get_api_key() -> str:
    """Dependency to get API key"""
    try:
        return get_api_key_from_env()
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))

def verify_api_token(x_api_token: Optional[str] = Header(None)) -> bool:
    """Optional API token verification for production"""
    # In production, implement proper token validation
    # For now, just return True
    return True

# ====================
# API ENDPOINTS
# ====================

@app.get("/", tags=["General"])
async def root():
    """Root endpoint - API information"""
    return {
        "message": "AI Refrigerator Sales Assistant REST API",
        "version": "3.0.0",
        "docs": "/docs",
        "endpoints": {
            "health": "/health",
            "chat": "/chat",
            "catalog": "/catalog",
            "security": "/security-features",
            "sessions": "/sessions"
        }
    }

@app.get("/health", response_model=HealthResponse, tags=["General"])
async def health_check():
    """Health check endpoint"""
    try:
        api_key = get_api_key_from_env()
        catalog_exists = os.path.exists("refrigerator_catalog.pdf")
        
        return HealthResponse(
            status="healthy",
            version="3.0.0",
            security_enabled=True,
            catalog_loaded=catalog_exists
        )
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")

@app.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(
    request: ChatRequest,
    api_key: str = Depends(get_api_key),
    authenticated: bool = Depends(verify_api_token)
):
    """
    Main chat endpoint - Send a message and get AI response
    
    - **message**: User's question or message
    - **session_id**: Optional session ID to maintain conversation context
    """
    try:
        # Generate session ID if not provided
        session_id = request.session_id or f"session_{os.urandom(8).hex()}"
        
        # Get or create session
        bot = session_manager.get_or_create_session(session_id, api_key)
        
        # Process message
        response = bot.chat(request.message)
        
        # Update message count
        session_manager.increment_message_count(session_id)
        
        return ChatResponse(
            response=response,
            session_id=session_id,
            message_count=session_manager.get_message_count(session_id),
            security_validated=True
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

@app.get("/catalog", tags=["Product Information"])
async def get_catalog():
    """Get refrigerator catalog statistics"""
    try:
        stats = get_catalog_stats()
        return {
            "status": "success",
            "data": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/security-features", tags=["Security"])
async def get_security():
    """Get information about security features"""
    try:
        features = get_security_features()
        return {
            "status": "success",
            "security_features": features,
            "guardrails_enabled": True,
            "pii_detection": True,
            "toxic_language_filter": True,
            "creative_responses": True
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sessions", response_model=List[SessionInfo], tags=["Session Management"])
async def list_sessions(authenticated: bool = Depends(verify_api_token)):
    """List all active chat sessions"""
    return session_manager.list_sessions()

@app.delete("/sessions/{session_id}", tags=["Session Management"])
async def clear_session(
    session_id: str,
    authenticated: bool = Depends(verify_api_token)
):
    """Clear a specific chat session"""
    success = session_manager.clear_session(session_id)
    if success:
        return {
            "status": "success",
            "message": f"Session {session_id} cleared",
            "session_id": session_id
        }
    else:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")

@app.delete("/sessions", tags=["Session Management"])
async def clear_all_sessions(authenticated: bool = Depends(verify_api_token)):
    """Clear all chat sessions"""
    session_ids = list(session_manager.sessions.keys())
    for session_id in session_ids:
        session_manager.clear_session(session_id)
    
    return {
        "status": "success",
        "message": f"Cleared {len(session_ids)} sessions",
        "cleared_count": len(session_ids)
    }

@app.post("/test-security", tags=["Testing"])
async def test_security(
    request: ChatRequest,
    api_key: str = Depends(get_api_key)
):
    """
    Test security features with various inputs
    (For demonstration purposes)
    """
    session_id = "test_session"
    bot = session_manager.get_or_create_session(session_id, api_key)
    
    response = bot.chat(request.message)
    
    return {
        "status": "success",
        "input": request.message,
        "response": response,
        "security_validated": True,
        "note": "This is a test endpoint to demonstrate security features"
    }

# ====================
# ERROR HANDLERS
# ====================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler"""
    return {
        "error": exc.detail,
        "status_code": exc.status_code
    }

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """General exception handler"""
    return {
        "error": "Internal server error",
        "detail": str(exc),
        "status_code": 500
    }

# ====================
# STARTUP/SHUTDOWN EVENTS
# ====================

@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    print("🚀 Starting AI Refrigerator Sales Assistant REST API")
    print("📚 Ensuring catalog exists...")
    ensure_catalog_exists()
    print("✅ API ready to serve requests")
    print("📖 API docs available at: http://localhost:8000/docs")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print("🛑 Shutting down API...")
    # Clear all sessions
    for session_id in list(session_manager.sessions.keys()):
        session_manager.clear_session(session_id)
    print("✅ Cleanup complete")

# ====================
# RUN SERVER
# ====================

if __name__ == "__main__":
    print("="*50)
    print("🚀 AI Refrigerator Sales Assistant REST API")
    print("="*50)
    print("\n📖 API Documentation:")
    print("   Swagger UI: http://localhost:8000/docs")
    print("   ReDoc:      http://localhost:8000/redoc")
    print("\n🔌 Endpoints:")
    print("   GET  /health              - Health check")
    print("   POST /chat                - Chat with AI")
    print("   GET  /catalog             - Product catalog")
    print("   GET  /security-features   - Security info")
    print("   GET  /sessions            - List sessions")
    print("   DELETE /sessions/{id}     - Clear session")
    print("\n" + "="*50 + "\n")
    
    uvicorn.run(
        "fast_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )