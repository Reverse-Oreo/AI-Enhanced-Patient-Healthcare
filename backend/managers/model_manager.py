import asyncio
import logging
import os
import time
from typing import Optional, Dict, Any
from threading import Lock

from adapters.local_model_adapter import LocalModelAdapter
from adapters.skinlesion_efficientNet_adapter import EfficientNetAdapter
from adapters.embedder_adapter import EmbedderAdapter

logger = logging.getLogger(__name__)

class ModelManager:
    """Singleton model manager to ensure models are loaded only once"""
    
    _instance: Optional['ModelManager'] = None
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
        
        # Model paths
        self.multipurpose_model_path = "ai_models/Llama-3.1-8B-UltraMedical.Q8_0.gguf"
        self.skin_model_path = "ai_models/skin_lesion_efficientnetb0.pth"
        self.embedding_model_name = "sentence-transformers/all-MiniLM-L6-v2"
        
        # Adapter instances (will be created once)
        self.local_adapter: Optional[LocalModelAdapter] = None
        self.efficientnet_adapter: Optional[EfficientNetAdapter] = None
        self.embedder_adapter: Optional[EmbedderAdapter] = None
        
        # Loading stats
        self.load_start_time: Optional[float] = None
        self.load_end_time: Optional[float] = None
        
        logger.info("🏗️ ModelManager singleton created")
    
    async def load_all_models(self) -> Dict[str, Any]:
        """Load all models once. Thread-safe and async-safe."""
        
        async with self._loading_lock:
            if self._models_loaded:
                logger.info("✅ Models already loaded, returning existing instances")
                return self._get_model_info()
            
            logger.info("🚀 Starting model loading process...")
            self.load_start_time = time.time()
            
            try:
                # Create adapters
                logger.info("📦 Creating model adapters...")
                self.local_adapter = LocalModelAdapter(llm_path=self.multipurpose_model_path)
                self.efficientnet_adapter = EfficientNetAdapter(model_path=self.skin_model_path)
                self.embedder_adapter = EmbedderAdapter(model_name=self.embedding_model_name)
                
                # Load models concurrently for faster startup
                logger.info("⏳ Loading models concurrently...")
                await asyncio.gather(
                    self._load_llm_model(),
                    self._load_skin_model(),
                    self._load_embedding_model(),
                    return_exceptions=True
                )
                
                self.load_end_time = time.time()
                self._models_loaded = True
                
                load_time = self.load_end_time - self.load_start_time
                logger.info(f"✅ All models loaded successfully in {load_time:.2f}s")
                
                return self._get_model_info()
                
            except Exception as e:
                logger.error(f"❌ Model loading failed: {e}")
                raise
    
    async def _load_llm_model(self):
        """Load LLM model with error handling"""
        try:
            logger.info("🧠 Loading LLM model...")
            await self.local_adapter.load_model()
            logger.info("✅ LLM model loaded")
        except Exception as e:
            logger.error(f"❌ LLM model loading failed: {e}")
            # Don't raise - allow other models to load
    
    async def _load_skin_model(self):
        """Load skin lesion model with error handling"""
        try:
            logger.info("🔬 Loading skin lesion model...")
            await self.efficientnet_adapter.load_model()
            logger.info("✅ Skin lesion model loaded")
        except Exception as e:
            logger.error(f"❌ Skin lesion model loading failed: {e}")
            # Don't raise - allow other models to load
    
    async def _load_embedding_model(self):
        """Load embedding model with error handling"""
        try:
            logger.info("📊 Loading embedding model...")
            await self.embedder_adapter.load_model()
            logger.info("✅ Embedding model loaded")
        except Exception as e:
            logger.error(f"❌ Embedding model loading failed: {e}")
            # Don't raise - allow other models to load
    
    def _get_model_info(self) -> Dict[str, Any]:
        """Get model loading information"""
        load_time = (self.load_end_time - self.load_start_time) if self.load_start_time and self.load_end_time else 0
        
        return {
            "models_loaded": self._models_loaded,
            "load_time_seconds": round(load_time, 2),
            "local_adapter_loaded": self.local_adapter is not None and hasattr(self.local_adapter, 'model') and self.local_adapter.model is not None,
            "skin_adapter_loaded": self.efficientnet_adapter is not None and hasattr(self.efficientnet_adapter, 'model') and self.efficientnet_adapter.model is not None,
            "embedding_adapter_loaded": self.embedder_adapter is not None and hasattr(self.embedder_adapter, 'model') and self.embedder_adapter.model is not None,
            "adapters": {
                "local": self.local_adapter,
                "efficientnet": self.efficientnet_adapter,
                "embedder": self.embedder_adapter
            }
        }
    
    def get_local_adapter(self) -> Optional[LocalModelAdapter]:
        """Get the LLM adapter instance"""
        if not self._models_loaded:
            logger.warning("⚠️ Models not loaded yet. Call load_all_models() first.")
            return None
        return self.local_adapter
    
    def get_efficientnet_adapter(self) -> Optional[EfficientNetAdapter]:
        """Get the skin lesion adapter instance"""
        if not self._models_loaded:
            logger.warning("⚠️ Models not loaded yet. Call load_all_models() first.")
            return None
        return self.efficientnet_adapter
    
    def get_embedder_adapter(self) -> Optional[EmbedderAdapter]:
        """Get the embedding adapter instance"""
        if not self._models_loaded:
            logger.warning("⚠️ Models not loaded yet. Call load_all_models() first.")
            return None
        return self.embedder_adapter
    
    def is_loaded(self) -> bool:
        """Check if models are loaded"""
        return self._models_loaded
    
    async def cleanup(self):
        """Cleanup all models"""
        logger.info("🧹 Cleaning up models...")
        
        if self.local_adapter:
            # Add cleanup method to LocalModelAdapter if needed
            pass
            
        if self.efficientnet_adapter:
            await self.efficientnet_adapter.cleanup()
            
        if self.embedder_adapter:
            # Add cleanup method to EmbedderAdapter if needed
            pass
        
        self._models_loaded = False
        logger.info("✅ Model cleanup complete")

# Global instance
model_manager = ModelManager()