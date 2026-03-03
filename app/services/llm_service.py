# app/services/llm_service.py
"""
LLM 服务模块
使用 DeepSeek API 进行评论情绪分析
"""

import os
import requests
import json
import re
from typing import List

class LLMService:
    """DeepSeek 语言大模型服务"""
    
    def __init__(self):
        # DeepSeek API 配置
        self.api_key = os.getenv("DEEPSEEK_API_KEY", "")
        if not self.api_key:
            print("警告: 未设置 DEEPSEEK_API_KEY 环境变量，LLM 分析功能将不可用")
        self.api_base = os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com/v1")
        self.model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
    
    def analyze_comments_sentiment(self, comments: List[dict]) -> str:
        """
        使用 DeepSeek API 分析评论情绪
        
        Args:
            comments: 评论列表，格式 [{"author": "xxx", "content": "xxx"}, ...]
        
        Returns:
            情绪分析结果（JSON 字符串）
        """
        if not comments:
            return json.dumps({
                "summary": "无评论数据", 
                "overall_sentiment": "neutral", 
                "comment_count": 0
            }, ensure_ascii=False)
        
        try:
            return self._deepseek_sentiment_analysis(comments)
        except Exception as e:
            print(f"DeepSeek API 分析失败: {e}")
            import traceback
            traceback.print_exc()
            # 返回错误信息
            return json.dumps({
                "summary": f"分析失败: {str(e)}", 
                "overall_sentiment": "error", 
                "comment_count": len(comments)
            }, ensure_ascii=False)
    
    def _deepseek_sentiment_analysis(self, comments: List[dict]) -> str:
        """使用 DeepSeek API 进行情绪分析"""
        
        # 构建提示词，包含所有评论
        comments_text = "\n".join([
            f"{i+1}. [{c.get('author', 'Unknown')}]: {c.get('content', '')[:150]}"
            for i, c in enumerate(comments[:30])  # 分析前30条评论
        ])
        
        prompt = f"""请分析以下网易云音乐评论的整体情绪倾向，给出详细的情感分析报告。

评论内容（共{len(comments)}条）：
{comments_text}

请严格按照以下 JSON 格式返回分析结果，不要添加任何其他文字：
{{
    "overall_sentiment": "positive/negative/neutral/mixed",
    "sentiment_score": 0.85,
    "positive_ratio": 0.70,
    "negative_ratio": 0.15,
    "neutral_ratio": 0.15,
    "summary": "简短总结评论的主要情绪和主题",
    "key_emotions": ["喜爱", "感动", "怀念"],
    "comment_count": {len(comments)},
    "main_themes": ["对歌曲的喜爱", "情感共鸣"],
    "analysis_method": "deepseek_api"
}}
"""
        
        # 调用 DeepSeek API
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system", 
                    "content": "你是一个专业的中文评论情绪分析专家，擅长分析用户评论的情感倾向、情绪分布和主题。请以 JSON 格式返回分析结果。"
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            "temperature": 0.3,
            "max_tokens": 1000,
            "stream": False
        }
        
        print(f"正在调用 DeepSeek API 分析 {len(comments)} 条评论...")
        
        response = requests.post(
            f"{self.api_base}/chat/completions",
            headers=headers,
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            analysis_result = result['choices'][0]['message']['content']
            
            print(f"DeepSeek API 调用成功")
            
            # 提取 JSON 部分
            json_match = re.search(r'\{.*\}', analysis_result, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                # 验证 JSON 格式
                json.loads(json_str)  # 如果格式错误会抛出异常
                return json_str
            else:
                # 如果没有找到 JSON，尝试直接返回
                return analysis_result
        else:
            error_msg = f"DeepSeek API 返回错误: {response.status_code}, {response.text}"
            print(error_msg)
            raise Exception(error_msg)

# 创建全局实例
llm_service = LLMService()
