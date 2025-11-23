"""AI 状态监控处理器"""

import logging
from mitmproxy import http
from typing import Optional
from ..core.interceptor import BaseInterceptor

logger = logging.getLogger(__name__)


class AIMonitorHandler(BaseInterceptor):
    """AI 状态监控处理器"""

    def __init__(self):
        super().__init__("AIMonitorHandler")
        self.ai_requests = 0
        self.ai_responses = 0

    def request(self, flow: http.HTTPFlow) -> Optional[http.HTTPFlow]:
        """监控 AI 相关请求"""
        url = flow.request.pretty_url
        path = flow.request.path
        
        # 检测 AI 相关请求（根据路径判断）
        if "/ai/" in path or "multi-agent" in path:
            self.ai_requests += 1
            logger.debug(f"🤖 AI Request #{self.ai_requests}: {flow.request.method} {url}")
        
        return None

    def response(self, flow: http.HTTPFlow) -> Optional[http.HTTPFlow]:
        """监控 AI 相关响应"""
        if flow.response:
            url = flow.request.pretty_url
            path = flow.request.path
            
            # 检测 AI 相关响应
            if "/ai/" in path or "multi-agent" in path:
                self.ai_responses += 1
                status = flow.response.status_code
                logger.debug(f"🤖 AI Response #{self.ai_responses}: {url} [{status}]")
        
        return None

    def get_stats(self) -> dict:
        """获取 AI 请求统计"""
        return {
            "ai_requests": self.ai_requests,
            "ai_responses": self.ai_responses,
        }

