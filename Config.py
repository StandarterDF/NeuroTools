import os
import os.path


BaseDir = os.path.dirname(__file__)

OpenAI_API_Providers = {
    "Local": {"base_url": "http://192.168.0.124:1234/v1", "key": "sk-nokeyrequired", "model": "qwen3-30b-a3b"},
    "OpenRouter": {"base_url": "https://openrouter.ai/api/v1", "key": "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", "model": "meta-llama/llama-4-maverick:free"},
}
OpenAI_API_Default = "OpenRouter"

OpenAI_API_BaseURL = "http://192.168.0.124:1234/v1"
OpenAI_API_Key = "sk-nokeyrequired"
OpenAI_API_Model = "qwen3-30b-a3b"
OpenAI_API_Embedding = "text-embedding-nomic-embed-text-v1.5"

TopicText_AutoGenerator = True