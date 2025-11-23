"""日志分析命令行工具"""

import sys
import argparse
import logging
from pathlib import Path

from .api_analyzer import APIAnalyzer
from .report_generator import ReportGenerator


def setup_logging(verbose: bool = False):
    """设置日志"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="分析 WarpGateway 日志文件，生成 API 分析报告"
    )
    parser.add_argument(
        "log_file",
        type=str,
        help="要分析的日志文件路径（JSONL 格式）"
    )
    parser.add_argument(
        "--format",
        "-f",
        choices=["markdown", "json", "console"],
        default="markdown",
        help="输出格式 (默认: markdown)"
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        help="输出文件路径（如果不指定，将输出到控制台或默认文件名）"
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="显示详细日志"
    )
    
    args = parser.parse_args()
    
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)
    
    # 检查日志文件
    log_file = Path(args.log_file)
    if not log_file.exists():
        logger.error(f"日志文件不存在: {log_file}")
        sys.exit(1)
    
    logger.info(f"开始分析日志文件: {log_file}")
    
    # 创建分析器
    analyzer = APIAnalyzer(log_file)
    
    # 加载日志
    if not analyzer.load_logs():
        logger.error("加载日志失败")
        sys.exit(1)
    
    # 执行分析
    logger.info("执行分析...")
    analysis_data = analyzer.analyze()
    
    if "error" in analysis_data:
        logger.error(analysis_data["error"])
        sys.exit(1)
    
    # 生成报告
    logger.info("生成报告...")
    generator = ReportGenerator(analysis_data)
    
    # 确定输出路径
    if args.output:
        output_path = Path(args.output)
    else:
        if args.format == "console":
            # 控制台输出，直接打印
            print(generator.generate_console())
            sys.exit(0)
        else:
            # 默认文件名
            output_path = log_file.parent / f"analysis_report_{log_file.stem}"
    
    # 保存报告
    if args.format != "console":
        output_path = generator.save(output_path, args.format)
        print(f"✅ 分析报告已生成: {output_path}")
    else:
        print(generator.generate_console())


if __name__ == "__main__":
    main()

