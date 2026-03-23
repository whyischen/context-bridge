from core.config import CONFIG
from core.runtimes.qmd_runtime import QMDRuntime
from core.managers.openviking_manager import OpenVikingManager
from core.utils.logger import get_logger

logger = get_logger("factories")

# Singleton instance cache
_context_manager_instance = None

def initialize_system():
    """
    工厂模式：根据配置初始化底层检索引擎 (QMD) 和 上下文管理器 (OpenViking)
    使用单例模式避免重复初始化和模型重复下载
    
    支持自定义嵌入模型配置：
    - gte-small-zh: 阿里达摩院 GTE-Small-Zh ONNX INT8 量化模型（默认）
    - chromadb-default: ChromaDB 内置的 ONNXMiniLM_L6_V2 模型
    """
    global _context_manager_instance
    
    if _context_manager_instance is not None:
        return _context_manager_instance
    
    # 1. 根据配置选择嵌入模型
    embedding_config = CONFIG.get("embedding", {})
    model_type = embedding_config.get("model", "gte-small-zh")  # 默认使用 GTE-Small-Zh
    
    embedding_model = None
    
    if model_type == "gte-small-zh":
        try:
            from core.embeddings.gte_small_zh import GTESmallZhONNX
            logger.info("🚀 Initializing GTE-Small-Zh ONNX embedding model...")
            embedding_model = GTESmallZhONNX()
            logger.info(f"✅ GTE-Small-Zh model loaded (dimension: {embedding_model.get_dimension()})")
        except Exception as e:
            logger.error(f"Failed to load GTE-Small-Zh model: {e}", exc_info=True)
            logger.warning("⚠️ Falling back to ChromaDB default embedding model")
            embedding_model = None
    elif model_type == "chromadb-default":
        logger.info("Using ChromaDB default embedding model (ONNXMiniLM_L6_V2)")
        embedding_model = None
    else:
        logger.warning(f"Unknown embedding model type: {model_type}, using ChromaDB default")
        embedding_model = None
    
    # 2. 实例化底层检索运行时（注入嵌入模型）
    qmd_runtime = QMDRuntime(CONFIG, embedding_model=embedding_model)
    
    # 3. 实例化上下文管理器，并将底层引擎注入进去 (依赖注入)
    viking_manager = OpenVikingManager(search_runtime=qmd_runtime, config=CONFIG)
    
    _context_manager_instance = viking_manager
    return viking_manager
