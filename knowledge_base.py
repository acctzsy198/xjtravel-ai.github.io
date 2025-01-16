import os
import chromadb
from chromadb.config import Settings
import config

class KnowledgeBase:
    def __init__(self):
        self.client = chromadb.Client(Settings(
            persist_directory=config.VECTOR_DB_PATH
        ))
        self.collection = self.client.get_or_create_collection(
            name="knowledge_base",
            metadata={"description": "General knowledge base for the agent"}
        )
        
    def add_document(self, text, metadata=None):
        """添加文档到知识库"""
        if metadata is None:
            metadata = {}
            
        # 生成唯一ID
        doc_id = str(len(self.collection.get()["ids"]) + 1)
        
        self.collection.add(
            documents=[text],
            metadatas=[metadata],
            ids=[doc_id]
        )
        
    def query(self, query_text, n_results=5):
        """查询知识库"""
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results
        )
        
        return results["documents"][0]  # 返回匹配的文档列表
        
    def clear(self):
        """清空知识库"""
        self.client.delete_collection("knowledge_base")
        self.collection = self.client.get_or_create_collection(
            name="knowledge_base",
            metadata={"description": "General knowledge base for the agent"}
        )
