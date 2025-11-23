"""API 分析器"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import defaultdict
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class APIAnalyzer:
    """API 分析器"""

    def __init__(self, log_file: Path):
        self.log_file = Path(log_file)
        self.requests: List[Dict[str, Any]] = []
        self.responses: List[Dict[str, Any]] = []
        
    def load_logs(self) -> bool:
        """加载日志文件"""
        if not self.log_file.exists():
            logger.error(f"日志文件不存在: {self.log_file}")
            return False
        
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        entry = json.loads(line)
                        if entry.get('type') == 'request':
                            self.requests.append(entry)
                        elif entry.get('type') == 'response':
                            self.responses.append(entry)
                    except json.JSONDecodeError as e:
                        logger.warning(f"解析日志行失败: {e}")
                        continue
            
            logger.info(f"加载了 {len(self.requests)} 个请求和 {len(self.responses)} 个响应")
            return True
        except Exception as e:
            logger.error(f"加载日志文件失败: {e}")
            return False
    
    def analyze(self) -> Dict[str, Any]:
        """执行分析"""
        if not self.requests:
            return {"error": "没有可分析的请求"}
        
        analysis = {
            "summary": self._analyze_summary(),
            "endpoints": self._analyze_endpoints(),
            "auth_headers": self._analyze_auth_headers(),
            "request_bodies": self._analyze_request_bodies(),
            "ai_requests": self._analyze_ai_requests(),
            "token_locations": self._analyze_token_locations(),
        }
        
        return analysis
    
    def _analyze_summary(self) -> Dict[str, Any]:
        """分析摘要"""
        total_requests = len(self.requests)
        total_responses = len(self.responses)
        
        methods = defaultdict(int)
        domains = defaultdict(int)
        status_codes = defaultdict(int)
        
        for req in self.requests:
            methods[req.get('method', 'UNKNOWN')] += 1
            domains[req.get('host', 'unknown')] += 1
        
        for resp in self.responses:
            status_codes[resp.get('status_code', 0)] += 1
        
        return {
            "total_requests": total_requests,
            "total_responses": total_responses,
            "methods": dict(methods),
            "domains": dict(domains),
            "status_codes": dict(status_codes),
        }
    
    def _analyze_endpoints(self) -> List[Dict[str, Any]]:
        """分析 API 端点"""
        endpoints = defaultdict(lambda: {
            "method": "",
            "path": "",
            "host": "",
            "count": 0,
            "status_codes": defaultdict(int),
        })
        
        for req in self.requests:
            key = f"{req.get('method')} {req.get('path')}"
            endpoints[key]["method"] = req.get('method', '')
            endpoints[key]["path"] = req.get('path', '')
            endpoints[key]["host"] = req.get('host', '')
            endpoints[key]["count"] += 1
        
        # 关联响应状态码
        for resp in self.responses:
            key = f"{resp.get('method')} {resp.get('path')}"
            if key in endpoints:
                endpoints[key]["status_codes"][resp.get('status_code', 0)] += 1
        
        result = []
        for key, data in sorted(endpoints.items(), key=lambda x: x[1]["count"], reverse=True):
            result.append({
                "method": data["method"],
                "path": data["path"],
                "host": data["host"],
                "url": f"{data['host']}{data['path']}",
                "count": data["count"],
                "status_codes": dict(data["status_codes"]),
            })
        
        return result
    
    def _analyze_auth_headers(self) -> Dict[str, Any]:
        """分析认证相关的 Header"""
        auth_headers = defaultdict(list)
        auth_patterns = {
            "Authorization": [],
            "X-API-Key": [],
            "X-Auth-Token": [],
            "Cookie": [],
        }
        
        for req in self.requests:
            headers = req.get('headers', {})
            for header_name, header_value in headers.items():
                header_lower = header_name.lower()
                if 'authorization' in header_lower:
                    auth_headers["Authorization"].append({
                        "url": req.get('url'),
                        "value_preview": header_value[:50] if len(header_value) > 50 else header_value,
                    })
                elif 'api-key' in header_lower or 'apikey' in header_lower:
                    auth_headers["X-API-Key"].append({
                        "url": req.get('url'),
                        "value_preview": header_value[:50] if len(header_value) > 50 else header_value,
                    })
                elif 'auth-token' in header_lower or 'token' in header_lower:
                    auth_headers["X-Auth-Token"].append({
                        "url": req.get('url'),
                        "value_preview": header_value[:50] if len(header_value) > 50 else header_value,
                    })
                elif 'cookie' in header_lower:
                    auth_headers["Cookie"].append({
                        "url": req.get('url'),
                        "value_preview": header_value[:100] if len(header_value) > 100 else header_value,
                    })
        
        # 分析 Authorization Header 格式
        auth_formats = defaultdict(int)
        for auth_entry in auth_headers.get("Authorization", []):
            value = auth_entry.get("value_preview", "")
            if value.startswith("Bearer "):
                auth_formats["Bearer Token"] += 1
            elif value.startswith("Basic "):
                auth_formats["Basic Auth"] += 1
            elif value.startswith("Token "):
                auth_formats["Token"] += 1
            else:
                auth_formats["Other"] += 1
        
        return {
            "headers_found": {k: len(v) for k, v in auth_headers.items()},
            "auth_formats": dict(auth_formats),
            "details": {k: v[:10] for k, v in auth_headers.items()},  # 只保留前10个示例
        }
    
    def _analyze_request_bodies(self) -> Dict[str, Any]:
        """分析请求体结构"""
        json_bodies = []
        text_bodies = []
        empty_bodies = 0
        
        for req in self.requests:
            body = req.get('body')
            if not body:
                empty_bodies += 1
                continue
            
            body_type = body.get('type')
            body_data = body.get('data')
            
            if body_type == 'json' and isinstance(body_data, dict):
                json_bodies.append({
                    "url": req.get('url'),
                    "method": req.get('method'),
                    "schema": self._extract_json_schema(body_data),
                })
            elif body_type == 'text':
                text_bodies.append({
                    "url": req.get('url'),
                    "method": req.get('method'),
                    "preview": str(body_data)[:200],
                })
        
        # 提取常见的 JSON 字段
        common_fields = defaultdict(int)
        for json_body in json_bodies:
            schema = json_body.get('schema', {})
            for field in schema.keys():
                common_fields[field] += 1
        
        return {
            "total_with_body": len(json_bodies) + len(text_bodies),
            "empty_bodies": empty_bodies,
            "json_bodies_count": len(json_bodies),
            "text_bodies_count": len(text_bodies),
            "common_fields": dict(sorted(common_fields.items(), key=lambda x: x[1], reverse=True)[:20]),
            "json_examples": json_bodies[:5],  # 只保留前5个示例
        }
    
    def _extract_json_schema(self, data: Any, prefix: str = "") -> Dict[str, Any]:
        """提取 JSON schema"""
        if isinstance(data, dict):
            schema = {}
            for key, value in data.items():
                full_key = f"{prefix}.{key}" if prefix else key
                if isinstance(value, dict):
                    schema[key] = self._extract_json_schema(value, full_key)
                elif isinstance(value, list) and value and isinstance(value[0], dict):
                    schema[key] = [self._extract_json_schema(value[0], full_key)]
                else:
                    schema[key] = type(value).__name__
            return schema
        elif isinstance(data, list) and data:
            if isinstance(data[0], dict):
                return [self._extract_json_schema(data[0], prefix)]
            else:
                return [type(data[0]).__name__]
        else:
            return type(data).__name__
    
    def _analyze_ai_requests(self) -> Dict[str, Any]:
        """分析 AI 服务相关请求"""
        ai_paths = ['/ai/', '/multi-agent', '/chat', '/completion']
        ai_requests = []
        
        for req in self.requests:
            path = req.get('path', '')
            if any(ai_path in path for ai_path in ai_paths):
                ai_requests.append({
                    "url": req.get('url'),
                    "method": req.get('method'),
                    "path": path,
                    "has_body": req.get('body') is not None,
                })
        
        return {
            "count": len(ai_requests),
            "requests": ai_requests,
        }
    
    def _analyze_token_locations(self) -> Dict[str, Any]:
        """分析 Token 位置"""
        locations = {
            "headers": [],
            "body": [],
        }
        
        for req in self.requests:
            # 检查 Header 中的 Token
            headers = req.get('headers', {})
            for header_name, header_value in headers.items():
                if any(keyword in header_name.lower() for keyword in ['authorization', 'token', 'api-key']):
                    locations["headers"].append({
                        "header": header_name,
                        "url": req.get('url'),
                        "method": req.get('method'),
                    })
            
            # 检查请求体中的 Token
            body = req.get('body')
            if body and body.get('type') == 'json':
                body_data = body.get('data', {})
                if isinstance(body_data, dict):
                    for key, value in body_data.items():
                        if any(keyword in key.lower() for keyword in ['token', 'auth', 'session', 'api_key']):
                            locations["body"].append({
                                "field": key,
                                "url": req.get('url'),
                                "method": req.get('method'),
                            })
        
        return {
            "header_tokens": len(locations["headers"]),
            "body_tokens": len(locations["body"]),
            "details": locations,
        }

