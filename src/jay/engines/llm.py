import threading

_llama_instance = None
_llama_lock = threading.Lock()

def get_llama():
    """
    Returns a singleton instance of the native Llama model.
    Compiled with Metal support, it will load the model directly into unified GPU memory.
    """
    global _llama_instance
    if _llama_instance is None:
        with _llama_lock:
            if _llama_instance is None:
                from jay.config import get_settings
                try:
                    from llama_cpp import Llama
                except ImportError:
                    raise RuntimeError("llama-cpp-python is not installed. Please install it to use the native model.")
                
                settings = get_settings()
                _llama_instance = Llama(
                    model_path=settings.llm_model_path,
                    n_gpu_layers=-1,  # -1 means load all layers into Metal (GPU)
                    n_ctx=4096,       # 4K context window
                    verbose=False     # Supress heavy C++ logging
                )
    return _llama_instance

def generate_chat(messages, **kwargs):
    """Thread-safe chat completion wrapper to prevent C++ crashes on concurrent generation."""
    llama = get_llama()
    with _llama_lock:
        return llama.create_chat_completion(messages=messages, **kwargs)
