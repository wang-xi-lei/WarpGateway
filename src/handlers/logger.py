"""日志记录处理器"""

import json
import base64
import logging
from datetime import datetime
from pathlib import Path
from mitmproxy import http
from typing import Optional, Dict, Any
from urllib.parse import urlparse
from ..core.interceptor import BaseInterceptor

logger = logging.getLogger(__name__)


class LoggerHandler(BaseInterceptor):
    """日志记录处理器"""

    def __init__(self, log_dir: str = "logs", config=None):
        super().__init__("LoggerHandler")
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        self.config = config
        
        # 创建请求日志文件
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = self.log_dir / f"requests_{timestamp}.jsonl"
        
        logger.info(f"📁 Request log file: {self.log_file}")
    
    def _should_log(self, url: str) -> bool:
        """判断是否应该记录此请求"""
        if not self.config or not self.config.analysis_enabled:
            return True  # 如果没有配置，记录所有请求
        
        # 检查域名是否在分析列表中
        parsed = urlparse(url)
        host = parsed.netloc.split(':')[0]  # 移除端口
        
        for domain in self.config.analysis_domains:
            if domain in host or host.endswith('.' + domain):
                return True
        
        return False
    
    def _mask_sensitive_data(self, headers: Dict[str, str]) -> Dict[str, str]:
        """脱敏敏感信息"""
        if not self.config or not self.config.analysis_mask_sensitive:
            return headers
        
        masked = headers.copy()
        sensitive_headers = self.config.analysis_sensitive_headers
        
        for header_name in sensitive_headers:
            if header_name in masked:
                value = masked[header_name]
                if len(value) > 10:
                    masked[header_name] = value[:10] + "..." + value[-4:]
                else:
                    masked[header_name] = "***"
        
        return masked
    
    def _encode_body(self, content: bytes) -> Dict[str, Any]:
        """编码请求体或响应体"""
        if not content:
            return {"type": "empty", "data": None}
        
        # 检查大小限制
        max_size = self.config.analysis_max_body_size if self.config else 1048576
        if len(content) > max_size:
            return {
                "type": "binary",
                "data": base64.b64encode(content[:max_size]).decode('utf-8'),
                "truncated": True,
                "original_size": len(content)
            }
        
        # 尝试解析 JSON
        try:
            text = content.decode('utf-8')
            json_data = json.loads(text)
            return {"type": "json", "data": json_data}
        except (UnicodeDecodeError, json.JSONDecodeError):
            # 尝试作为文本
            try:
                text = content.decode('utf-8')
                return {"type": "text", "data": text}
            except UnicodeDecodeError:
                # 二进制数据，base64 编码
                return {
                    "type": "binary",
                    "data": base64.b64encode(content).decode('utf-8')
                }

    def request(self, flow: http.HTTPFlow) -> Optional[http.HTTPFlow]:
        """记录请求"""
        try:
            url = flow.request.pretty_url
            
            # 检查是否需要记录
            if not self._should_log(url):
                return None
            
            # 处理 Headers
            headers = dict(flow.request.headers)
            headers = self._mask_sensitive_data(headers)
            
            # 处理请求体
            body = None
            if flow.request.content:
                body = self._encode_body(flow.request.content)
            
            request_data = {
                "timestamp": datetime.now().isoformat(),
                "type": "request",
                "method": flow.request.method,
                "url": url,
                "host": flow.request.host,
                "path": flow.request.path,
                "headers": headers,
                "content_length": len(flow.request.content) if flow.request.content else 0,
                "body": body,
            }
            
            self._write_log(request_data)
        except Exception as e:
            logger.error(f"❌ Failed to log request: {e}")
        
        return None

    def response(self, flow: http.HTTPFlow) -> Optional[http.HTTPFlow]:
        """记录响应"""
        if not flow.response:
            return None
        
        try:
            url = flow.request.pretty_url
            
            # 检查是否需要记录
            if not self._should_log(url):
                return None
            
            # 处理 Headers
            headers = dict(flow.response.headers)
            headers = self._mask_sensitive_data(headers)
            
            # 处理响应体
            body = None
            if flow.response.content:
                body = self._encode_body(flow.response.content)
            
            response_data = {
                "timestamp": datetime.now().isoformat(),
                "type": "response",
                "method": flow.request.method,
                "url": url,
                "host": flow.request.host,
                "path": flow.request.path,
                "status_code": flow.response.status_code,
                "headers": headers,
                "content_length": len(flow.response.content) if flow.response.content else 0,
                "body": body,
            }
            
            self._write_log(response_data)
        except Exception as e:
            logger.error(f"❌ Failed to log response: {e}")
        
        return None

    def _write_log(self, data: dict):
        """写入日志文件"""
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(data, ensure_ascii=False) + "\n")
