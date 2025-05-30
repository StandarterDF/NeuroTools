import os
import os.path


BaseDir = os.path.dirname(__file__)

OpenAI_API_Providers = {
    "Local": {
        "base_url": "http://192.168.0.124:1234/v1", 
        "api_key": "sk-nokeyrequired", 
        "model": "qwen3-30b-a3b",
    }
}
OpenAI_API_Default = "Local"

OpenAI_API_BaseURL = "http://192.168.0.124:1234/v1"
OpenAI_API_Key = "sk-nokeyrequired"
OpenAI_API_Model = "qwen3-30b-a3b"
OpenAI_API_Embedding = "text-embedding-nomic-embed-text-v1.5"

TopicText_AutoGenerator = True
