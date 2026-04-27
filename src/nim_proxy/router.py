from .config import settings

class ModelRouter:
    @staticmethod
    def resolve(claude_model: str) -> str:
        model_id = claude_model.lower()
        
        if "opus" in model_id:
            return settings.MODEL_OPUS
        if "sonnet" in model_id:
            return settings.MODEL_SONNET
        if "haiku" in model_id:
            return settings.MODEL_HAIKU
            
        return settings.MODEL_FALLBACK
