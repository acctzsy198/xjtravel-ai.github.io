from typing import List, Dict
import datetime
import json
import zhipuai
import config
from knowledge_base import KnowledgeBase

class Agent:
    def __init__(self):
        zhipuai.api_key = config.ZHIPUAI_API_KEY
        self.conversation_history = []
        self.system_prompt = {"role": "system", "content": config.AGENT_DESCRIPTION}
        self.knowledge_base = KnowledgeBase()
        
    def add_message(self, role: str, content: str):
        """添加消息到对话历史"""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = {
            'role': role,
            'content': content,
            'timestamp': timestamp
        }
        
        if role in ["user", "assistant", "system"]:
            self.conversation_history.append({"role": role, "content": content})
            
        return message
    
    def get_response(self, user_input: str) -> str:
        """生成回复"""
        try:
            # 添加用户输入到历史
            self.add_message("user", user_input)
            
            # 查询知识库
            relevant_docs = self.knowledge_base.query(user_input)
            
            # 构建带有知识库内容的系统提示
            system_prompt = self.system_prompt.copy()
            if relevant_docs:
                knowledge_context = "\n\n相关知识：\n" + "\n".join(relevant_docs)
                system_prompt["content"] += knowledge_context
            
            # 准备对话消息
            messages = [system_prompt] + self.conversation_history[-10:]  # 只保留最近10条消息
            
            # 打印请求信息
            print("\n=== API请求信息 ===")
            print(f"模型: {config.MODEL_NAME}")
            print(f"温度: {config.TEMPERATURE}")
            print(f"最大tokens: {config.MAX_TOKENS}")
            print("\n消息历史:")
            print(json.dumps(messages, ensure_ascii=False, indent=2))
            
            # 调用智谱AI接口
            response = zhipuai.model_api.sse_invoke(
                model=config.MODEL_NAME,
                prompt=[  # 使用正确的消息格式
                    {"role": msg["role"], "content": msg["content"]} 
                    for msg in messages
                ],
                temperature=config.TEMPERATURE,
                top_p=0.7,
                max_tokens=config.MAX_TOKENS,
                incremental=False
            )
            
            # 获取完整的回复内容
            full_response = ""
            for event in response.events():
                if event.event == "add":
                    full_response += event.data
                elif event.event == "error" or event.event == "interrupted":
                    raise Exception(event.data)
                elif event.event == "finish":
                    print(f"\n=== API元信息 ===\n{event.meta}")
                    break
                    
            # 添加助手回复到历史
            self.add_message("assistant", full_response)
            return full_response
                
        except Exception as e:
            error_msg = f"发生错误: {str(e)}"
            print(f"\n异常信息: {error_msg}")
            return f"抱歉，我遇到了一些技术问题：{error_msg}"
    
    def clear_history(self):
        """清空对话历史"""
        self.conversation_history = []
        
    def get_history(self) -> List[Dict]:
        """获取对话历史"""
        formatted_history = []
        for msg in self.conversation_history:
            formatted_history.append({
                'role': msg["role"],
                'content': msg["content"],
                'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
        return formatted_history
