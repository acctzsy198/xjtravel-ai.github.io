import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 智谱AI配置
ZHIPUAI_API_KEY = os.getenv("ZHIPUAI_API_KEY")
MODEL_NAME = "glm-4"  # 或使用 "glm-3-turbo"

# AI助手配置
AGENT_NAME = "智能助手"
AGENT_DESCRIPTION = "我是一个智能助手，可以帮助您解答问题、提供建议和参与对话。我会以简洁明了的方式回应，避免重复内容。"

# 回复限制
MAX_TOKENS = 150  # 限制每次回复的长度
MAX_CONTEXT_LENGTH = 1000  # 限制上下文长度
TEMPERATURE = 0.7  # 温度参数，控制回复的随机性

# 消息处理
REMOVE_DUPLICATES = True  # 启用重复内容检测和移除

# 知识库配置
KNOWLEDGE_DIR = "knowledge"  # 知识文件存储目录
VECTOR_DB_PATH = "vector_store"  # 向量数据库存储路径
