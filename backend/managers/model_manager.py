import asyncio
import logging
import os
import time
from typing import Optional, Dict, Any
from threading import Lock

from adapters.bedrock_model_adapter import BedrockModelAdapter
from adapters.skinlesion_efficientNet_adapter import EfficientNetAdapter
from adapters.embedder_adapter import EmbedderAdapter

logger = logging.getLogger(__name__)

MODEL_ID = "us.meta.llama3-1-8b-instruct-v1:0"

class ModelManager:
    """Singleton model manager to ensure models are loaded only once"""
    
    _instance: 'ModelManager' = None
    _lock = Lock()
    
    def __new__(cls) -> 'ModelManager':
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        # Only initialize once
        if hasattr(self, '_initialized'):
            return
            
        self._initialized = True
        self._models_loaded = False
        self._loading_lock = asyncio.Lock()
        
        # Bedrock configuration with credential handling
        self.bedrock_model_id = MODEL_ID
        self.bedrock_region = "us-east-1"
        
        # Try to get credentials from environment
        self.aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
        self.aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        self.aws_region = os.getenv('AWS_DEFAULT_REGION', self.bedrock_region)
        
        # Local model paths for other adapters
        self.skin_model_path = "ai_models/skin_lesion_efficientnetb0.pth"
        self.embedding_model_name = "sentence-transformers/all-MiniLM-L6-v2"
        
        # Adapter instances (will be created once)
        self.bedrock_adapter: Optional[BedrockModelAdapter] = None
        self.efficientnet_adapter: Optional[EfficientNetAdapter] = None
        self.embedder_adapter: Optional[EmbedderAdapter] = None
        
        # Loading stats
        self.load_start_time: Optional[float] = None
        self.load_end_time: Optional[float] = None
        
        logger.info("🏗️ ModelManager singleton created (Bedrock-enabled)")
        
        # Check credentials availability
        if self.aws_access_key and self.aws_secret_key:
            logger.info("✅ AWS credentials found in environment")
        else:
            logger.warning("⚠️ AWS credentials not found in environment variables")
            logger.info("💡 Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables")
    
    async def load_all_models(self) -> Dict[str, Any]:
        """Load only Bedrock LLM model initially. Skin/embedding models loaded on demand."""
        
        async with self._loading_lock:
            if self._models_loaded:
                logger.info("✅ Models already loaded, returning existing instances")
                return self._get_model_info()
            
            logger.info("🚀 Starting model loading process...")
            self.load_start_time = time.time()
            
            try:
                # Check credentials before creating adapter
                if not self._check_aws_credentials():
                    logger.warning("⚠️ AWS credentials not configured, but continuing with adapter creation")
                
                # Create Bedrock adapter (cloud-based, always needed)
                # FIXED: Remove aws_access_key_id and aws_secret_access_key parameters
                logger.info("📦 Creating Bedrock model adapter...")
                self.bedrock_adapter = BedrockModelAdapter(
                    model_id=self.bedrock_model_id,
                    region_name=self.aws_region
                )
                
                # Only load Bedrock model initially
                logger.info("⏳ Loading Bedrock LLM model...")
                await self._load_bedrock_model()
                
                # Create other adapters but don't load them yet
                logger.info("📦 Creating skin and embedding adapters (not loading yet)...")
                self.efficientnet_adapter = EfficientNetAdapter(model_path=self.skin_model_path)
                self.embedder_adapter = EmbedderAdapter(model_name=self.embedding_model_name)
                
                self.load_end_time = time.time()
                self._models_loaded = True
                
                load_time = self.load_end_time - self.load_start_time
                logger.info(f"✅ Bedrock LLM model loaded successfully in {load_time:.2f}s")
                logger.info("📋 Skin and embedding models will be loaded on demand")
                
                return self._get_model_info()
                
            except Exception as e:
                logger.error(f"❌ Model loading failed: {e}")
                # Don't raise exception - let API start without models
                logger.warning("⚠️ API will start but Bedrock model will not be available")
                return self._get_model_info()
    
    def _check_aws_credentials(self) -> bool:
        """Check if AWS credentials are available"""
        # Check environment variables
        if os.getenv('AWS_ACCESS_KEY_ID') and os.getenv('AWS_SECRET_ACCESS_KEY'):
            return True
        
        # Check if AWS CLI is configured
        try:
            import boto3
            session = boto3.Session()
            credentials = session.get_credentials()
            if credentials and credentials.access_key and credentials.secret_key:
                logger.info("✅ Found AWS credentials from AWS CLI/profile")
                return True
        except Exception as e:
            logger.debug(f"No AWS CLI credentials: {e}")
        
        return False

    async def _load_bedrock_model(self):
        """Load Bedrock model with error handling"""
        try:
            logger.info("🧠 Loading Bedrock LLM model...")
            await self.bedrock_adapter.load_model()
            logger.info("✅ Bedrock LLM model loaded")
        except Exception as e:
            logger.error(f"❌ Bedrock LLM model loading failed: {e}")
            raise  
    
    async def _load_skin_model(self):
        """Load skin lesion model on demand"""
        try:
            if not hasattr(self.efficientnet_adapter, 'model') or self.efficientnet_adapter.model is None:
                logger.info("🔬 Loading skin lesion model on demand...")
                await self.efficientnet_adapter.load_model()
                logger.info("✅ Skin lesion model loaded")
        except Exception as e:
            logger.error(f"❌ Skin lesion model loading failed: {e}")
            raise
    
    async def _load_embedding_model(self):
        """Load embedding model on demand"""
        try:
            if not hasattr(self.embedder_adapter, 'model') or self.embedder_adapter.model is None:
                logger.info("📊 Loading embedding model on demand...")
                await self.embedder_adapter.load_model()
                logger.info("✅ Embedding model loaded")
        except Exception as e:
            logger.error(f"❌ Embedding model loading failed: {e}")
            raise
    
    def _get_model_info(self) -> Dict[str, Any]:
        """Get model loading information"""
        load_time = (self.load_end_time - self.load_start_time) if self.load_start_time and self.load_end_time else 0
        
        return {
            "models_loaded": self._models_loaded,
            "load_time_seconds": round(load_time, 2),
            "bedrock_adapter_loaded": self.bedrock_adapter is not None and hasattr(self.bedrock_adapter, 'client') and self.bedrock_adapter.client is not None,
            "skin_adapter_loaded": self.efficientnet_adapter is not None and hasattr(self.efficientnet_adapter, 'model') and self.efficientnet_adapter.model is not None,
            "embedding_adapter_loaded": self.embedder_adapter is not None and hasattr(self.embedder_adapter, 'model') and self.embedder_adapter.model is not None,
            "aws_credentials_available": self._check_aws_credentials(),
            "adapters": {
                "bedrock": self.bedrock_adapter,
                "efficientnet": self.efficientnet_adapter,
                "embedder": self.embedder_adapter
            },
            "bedrock_config": {
                "model_id": self.bedrock_model_id,
                "region": self.aws_region
            }
        }
    
    def get_bedrock_adapter(self) -> Optional[BedrockModelAdapter]:
        """Get the Bedrock LLM adapter instance"""
        if not self._models_loaded:
            logger.warning("⚠️ Models not loaded yet. Call load_all_models() first.")
            return None
        return self.bedrock_adapter
    
    # Alias for backward compatibility
    def get_local_adapter(self) -> Optional[BedrockModelAdapter]:
        """Get the LLM adapter instance (now Bedrock-based) - backward compatibility"""
        logger.info("ℹ️ get_local_adapter() is deprecated. Use get_bedrock_adapter() instead.")
        return self.get_bedrock_adapter()
    
    async def get_efficientnet_adapter(self) -> Optional[EfficientNetAdapter]:
        """Get the skin lesion adapter instance (load on demand)"""
        if not self._models_loaded:
            logger.warning("⚠️ Models not loaded yet. Call load_all_models() first.")
            return None
        
        # Load on demand
        if not hasattr(self.efficientnet_adapter, 'model') or self.efficientnet_adapter.model is None:
            await self._load_skin_model()
        
        return self.efficientnet_adapter
    
    async def get_embedder_adapter(self) -> Optional[EmbedderAdapter]:
        """Get the embedding adapter instance (load on demand)"""
        if not self._models_loaded:
            logger.warning("⚠️ Models not loaded yet. Call load_all_models() first.")
            return None
        
        # Load on demand
        if not hasattr(self.embedder_adapter, 'model') or self.embedder_adapter.model is None:
            await self._load_embedding_model()
        
        return self.embedder_adapter
    
    def is_loaded(self) -> bool:
        """Check if models are loaded"""
        return self._models_loaded
    
    def get_bedrock_config(self) -> Dict[str, str]:
        """Get Bedrock configuration"""
        return {
            "model_id": self.bedrock_model_id,
            "region": self.aws_region,
            "provider": "AWS Bedrock",
            "model_name": "Llama 3.1 8B Instruct",
            "credentials_configured": str(self._check_aws_credentials())
        }
    
    async def cleanup(self):
        """Cleanup all models"""
        logger.info("🧹 Cleaning up models...")
        
        if self.bedrock_adapter:
            # Bedrock client doesn't need explicit cleanup
            # Connection will be closed automatically
            logger.info("🔧 Bedrock adapter cleanup complete")
            
        if self.efficientnet_adapter:
            await self.efficientnet_adapter.cleanup()
            
        if self.embedder_adapter:
            # Add cleanup method to EmbedderAdapter if needed
            logger.info("📊 Embedder adapter cleanup complete")
        
        self._models_loaded = False
        logger.info("✅ Model cleanup complete")

# Global instance
model_manager = ModelManager()