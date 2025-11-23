"""报告生成器"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class ReportGenerator:
    """报告生成器"""

    def __init__(self, analysis_data: Dict[str, Any]):
        self.analysis = analysis_data
    
    def generate_markdown(self) -> str:
        """生成 Markdown 格式报告"""
        lines = []
        
        # 标题
        lines.append("# Warp.dev API 分析报告")
        lines.append("")
        lines.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        
        # 摘要
        summary = self.analysis.get("summary", {})
        lines.append("## 摘要")
        lines.append("")
        lines.append(f"- 总请求数: {summary.get('total_requests', 0)}")
        lines.append(f"- 总响应数: {summary.get('total_responses', 0)}")
        lines.append("")
        
        # 请求方法分布
        methods = summary.get("methods", {})
        if methods:
            lines.append("### 请求方法分布")
            lines.append("")
            lines.append("| 方法 | 数量 |")
            lines.append("|------|------|")
            for method, count in sorted(methods.items(), key=lambda x: x[1], reverse=True):
                lines.append(f"| {method} | {count} |")
            lines.append("")
        
        # 域名分布
        domains = summary.get("domains", {})
        if domains:
            lines.append("### 域名分布")
            lines.append("")
            lines.append("| 域名 | 请求数 |")
            lines.append("|------|--------|")
            for domain, count in sorted(domains.items(), key=lambda x: x[1], reverse=True):
                lines.append(f"| {domain} | {count} |")
            lines.append("")
        
        # API 端点
        endpoints = self.analysis.get("endpoints", [])
        if endpoints:
            lines.append("## API 端点列表")
            lines.append("")
            lines.append("| 方法 | 路径 | 主机 | 请求数 | 状态码 |")
            lines.append("|------|------|------|--------|--------|")
            for endpoint in endpoints[:50]:  # 只显示前50个
                method = endpoint.get("method", "")
                path = endpoint.get("path", "")
                host = endpoint.get("host", "")
                count = endpoint.get("count", 0)
                status_codes = endpoint.get("status_codes", {})
                status_str = ", ".join([f"{code}({cnt})" for code, cnt in sorted(status_codes.items())])
                lines.append(f"| {method} | `{path}` | {host} | {count} | {status_str} |")
            lines.append("")
        
        # 认证 Header 分析
        auth_headers = self.analysis.get("auth_headers", {})
        if auth_headers:
            lines.append("## 认证 Header 分析")
            lines.append("")
            
            headers_found = auth_headers.get("headers_found", {})
            if headers_found:
                lines.append("### 发现的认证 Header")
                lines.append("")
                lines.append("| Header | 出现次数 |")
                lines.append("|--------|----------|")
                for header, count in sorted(headers_found.items(), key=lambda x: x[1], reverse=True):
                    lines.append(f"| {header} | {count} |")
                lines.append("")
            
            auth_formats = auth_headers.get("auth_formats", {})
            if auth_formats:
                lines.append("### Authorization Header 格式")
                lines.append("")
                lines.append("| 格式 | 数量 |")
                lines.append("|------|------|")
                for fmt, count in sorted(auth_formats.items(), key=lambda x: x[1], reverse=True):
                    lines.append(f"| {fmt} | {count} |")
                lines.append("")
            
            details = auth_headers.get("details", {})
            if details:
                lines.append("### 认证 Header 示例")
                lines.append("")
                for header_name, examples in details.items():
                    if examples:
                        lines.append(f"#### {header_name}")
                        lines.append("")
                        for i, example in enumerate(examples[:3], 1):
                            lines.append(f"{i}. URL: `{example.get('url', '')}`")
                            lines.append(f"   值预览: `{example.get('value_preview', '')}`")
                            lines.append("")
        
        # 请求体分析
        request_bodies = self.analysis.get("request_bodies", {})
        if request_bodies:
            lines.append("## 请求体分析")
            lines.append("")
            lines.append(f"- 带请求体的请求: {request_bodies.get('total_with_body', 0)}")
            lines.append(f"- 空请求体: {request_bodies.get('empty_bodies', 0)}")
            lines.append(f"- JSON 格式: {request_bodies.get('json_bodies_count', 0)}")
            lines.append(f"- 文本格式: {request_bodies.get('text_bodies_count', 0)}")
            lines.append("")
            
            common_fields = request_bodies.get("common_fields", {})
            if common_fields:
                lines.append("### 常见字段")
                lines.append("")
                lines.append("| 字段名 | 出现次数 |")
                lines.append("|--------|----------|")
                for field, count in list(common_fields.items())[:20]:
                    lines.append(f"| `{field}` | {count} |")
                lines.append("")
            
            json_examples = request_bodies.get("json_examples", [])
            if json_examples:
                lines.append("### JSON 请求体示例")
                lines.append("")
                for i, example in enumerate(json_examples[:3], 1):
                    lines.append(f"#### 示例 {i}")
                    lines.append("")
                    lines.append(f"URL: `{example.get('url', '')}`")
                    lines.append(f"方法: {example.get('method', '')}")
                    lines.append("")
                    lines.append("```json")
                    lines.append(json.dumps(example.get("schema", {}), indent=2, ensure_ascii=False))
                    lines.append("```")
                    lines.append("")
        
        # AI 请求分析
        ai_requests = self.analysis.get("ai_requests", {})
        if ai_requests:
            lines.append("## AI 服务请求分析")
            lines.append("")
            lines.append(f"- AI 相关请求数: {ai_requests.get('count', 0)}")
            lines.append("")
            
            requests = ai_requests.get("requests", [])
            if requests:
                lines.append("### AI 请求列表")
                lines.append("")
                lines.append("| 方法 | 路径 | URL |")
                lines.append("|------|------|-----|")
                for req in requests[:20]:
                    method = req.get("method", "")
                    path = req.get("path", "")
                    url = req.get("url", "")
                    lines.append(f"| {method} | `{path}` | `{url}` |")
                lines.append("")
        
        # Token 位置分析
        token_locations = self.analysis.get("token_locations", {})
        if token_locations:
            lines.append("## Token 位置分析")
            lines.append("")
            lines.append(f"- Header 中的 Token: {token_locations.get('header_tokens', 0)}")
            lines.append(f"- 请求体中的 Token: {token_locations.get('body_tokens', 0)}")
            lines.append("")
            
            details = token_locations.get("details", {})
            if details:
                header_tokens = details.get("headers", [])
                if header_tokens:
                    lines.append("### Header 中的 Token")
                    lines.append("")
                    lines.append("| Header | 方法 | URL |")
                    lines.append("|--------|------|-----|")
                    for token in header_tokens[:10]:
                        header = token.get("header", "")
                        method = token.get("method", "")
                        url = token.get("url", "")
                        lines.append(f"| {header} | {method} | `{url}` |")
                    lines.append("")
                
                body_tokens = details.get("body", [])
                if body_tokens:
                    lines.append("### 请求体中的 Token")
                    lines.append("")
                    lines.append("| 字段名 | 方法 | URL |")
                    lines.append("|--------|------|-----|")
                    for token in body_tokens[:10]:
                        field = token.get("field", "")
                        method = token.get("method", "")
                        url = token.get("url", "")
                        lines.append(f"| `{field}` | {method} | `{url}` |")
                    lines.append("")
        
        return "\n".join(lines)
    
    def generate_json(self) -> str:
        """生成 JSON 格式报告"""
        return json.dumps(self.analysis, indent=2, ensure_ascii=False)
    
    def generate_console(self) -> str:
        """生成控制台格式报告"""
        lines = []
        
        lines.append("=" * 80)
        lines.append("Warp.dev API 分析报告")
        lines.append("=" * 80)
        lines.append("")
        
        # 摘要
        summary = self.analysis.get("summary", {})
        lines.append(f"总请求数: {summary.get('total_requests', 0)}")
        lines.append(f"总响应数: {summary.get('total_responses', 0)}")
        lines.append("")
        
        # 请求方法
        methods = summary.get("methods", {})
        if methods:
            lines.append("请求方法分布:")
            for method, count in sorted(methods.items(), key=lambda x: x[1], reverse=True):
                lines.append(f"  {method}: {count}")
            lines.append("")
        
        # 域名
        domains = summary.get("domains", {})
        if domains:
            lines.append("域名分布:")
            for domain, count in sorted(domains.items(), key=lambda x: x[1], reverse=True):
                lines.append(f"  {domain}: {count}")
            lines.append("")
        
        # 端点（前10个）
        endpoints = self.analysis.get("endpoints", [])
        if endpoints:
            lines.append("主要 API 端点 (前10个):")
            for i, endpoint in enumerate(endpoints[:10], 1):
                method = endpoint.get("method", "")
                path = endpoint.get("path", "")
                count = endpoint.get("count", 0)
                lines.append(f"  {i}. {method} {path} ({count} 次)")
            lines.append("")
        
        # 认证 Header
        auth_headers = self.analysis.get("auth_headers", {})
        if auth_headers:
            headers_found = auth_headers.get("headers_found", {})
            if headers_found:
                lines.append("发现的认证 Header:")
                for header, count in sorted(headers_found.items(), key=lambda x: x[1], reverse=True):
                    lines.append(f"  {header}: {count} 次")
                lines.append("")
        
        # AI 请求
        ai_requests = self.analysis.get("ai_requests", {})
        if ai_requests:
            count = ai_requests.get("count", 0)
            lines.append(f"AI 相关请求: {count} 个")
            lines.append("")
        
        # Token 位置
        token_locations = self.analysis.get("token_locations", {})
        if token_locations:
            lines.append("Token 位置:")
            lines.append(f"  Header 中: {token_locations.get('header_tokens', 0)} 个")
            lines.append(f"  请求体中: {token_locations.get('body_tokens', 0)} 个")
            lines.append("")
        
        lines.append("=" * 80)
        
        return "\n".join(lines)
    
    def save(self, output_path: Path, format_type: str = "markdown"):
        """保存报告到文件"""
        output_path = Path(output_path)
        
        if format_type == "markdown":
            content = self.generate_markdown()
            output_path = output_path.with_suffix('.md')
        elif format_type == "json":
            content = self.generate_json()
            output_path = output_path.with_suffix('.json')
        else:
            content = self.generate_console()
            output_path = output_path.with_suffix('.txt')
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"报告已保存到: {output_path}")
        return output_path

