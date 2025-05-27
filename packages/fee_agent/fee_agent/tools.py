import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List

import numpy as np

from fee_agent.config import settings
from fee_agent.model import ds_model


def analyze_traffic(traffic_data: dict) -> str:
    """
    Uses LLM to analyze traffic patterns for potential DDoS threats.

    Args:
        traffic_data (dict): Traffic data including requests per second, unique IPs, etc.

    Returns:
        str: Analysis result indicating if DDoS is detected
    """
    # 构建提示模板
    prompt_template = """
    分析以下网络流量数据，判断是否存在DDoS攻击风险：
    
    - 每秒请求数: {requests_per_second}
    - 独立IP数量: {unique_ips}
    - 请求模式: {request_pattern}
    
    请根据以下几点进行分析:
    1. 请求频率是否异常
    2. 独立IP数量是否合理
    3. 请求模式是否符合正常流量特征
    
    仅返回"Potential DDoS detected"或"Normal traffic pattern"
    """

    # 填充提示内容
    prompt = prompt_template.format(
        requests_per_second=traffic_data["requests_per_second"],
        unique_ips=traffic_data["unique_ips"],
        request_pattern=traffic_data["request_pattern"],
    )

    # 使用LLM分析
    response = ds_model.complete(prompt)

    # 返回分析结果
    return response.text.strip()


def log_detection(
    incident_id: str, severity: str, message: str, timestamp: datetime
) -> None:
    """
    Log DDoS detection events with detailed information.

    Args:
        incident_id (str): Unique identifier for the incident
        severity (str): Severity level of the incident (high/low)
        message (str): Description or resolution message
        timestamp (datetime): Time when the detection occurred
    """
    # 配置日志格式
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    # 创建日志目录
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # 构建日志信息
    log_entry = {
        "incident_id": incident_id,
        "severity": severity,
        "message": message,
        "timestamp": timestamp.isoformat(),
    }

    # 写入JSON格式日志文件
    json_log_path = log_dir / "ddos_detection.json"
    try:
        if json_log_path.exists():
            with open(json_log_path, "r") as f:
                logs = json.load(f)
        else:
            logs = []

        logs.append(log_entry)

        with open(json_log_path, "w") as f:
            json.dump(logs, f, indent=2)

    except Exception as e:
        logging.error(f"Failed to write JSON log: {str(e)}")

    # 同时使用logging输出到控制台
    log_message = (
        f"DDoS Detection - ID: {incident_id} | Severity: {severity} | {message}"
    )
    if severity == "high":
        logging.warning(log_message)
    else:
        logging.info(log_message)


def rate_limiter(max_requests: int, time_window: int):
    """
    A decorator to limit the number of requests to a function within a specified time window.

    :param max_requests: Maximum number of requests allowed within the time window.
    :param time_window: Time window in seconds for which the requests are counted.
    """
    from collections import defaultdict
    from time import time

    request_times = defaultdict(list)

    def decorator(func):
        def wrapper(*args, **kwargs):
            current_time = time()
            # Clean up old request timestamps
            request_times[args[0]] = [
                t
                for t in request_times[args[0]]
                if current_time - t < time_window
            ]

            if len(request_times[args[0]]) < max_requests:
                request_times[args[0]].append(current_time)
                return func(*args, **kwargs)
            else:
                raise Exception("Rate limit exceeded. Try again later.")

        return wrapper

    return decorator


def calculate_risk_score(traffic_data: Dict) -> float:
    """
    Calculate risk score based on traffic patterns.

    Args:
        traffic_data (dict): Traffic data including requests per second, unique IPs, etc.

    Returns:
        float: Risk score between 0 and 1
    """
    # 权重设置
    weights = {
        "requests_per_second": 0.5,
        "unique_ips": 0.3,
        "pattern_score": 0.2,
    }

    # 计算请求频率分数
    rps_score = min(
        traffic_data["requests_per_second"] / settings.MAX_NORMAL_RPS, 1.0
    )

    # 计算独立IP数量分数
    ip_concentration = traffic_data["requests_per_second"] / (
        traffic_data["unique_ips"] + 1
    )
    ip_score = min(ip_concentration / settings.MAX_NORMAL_IP_CONCENTRATION, 1.0)

    # 计算请求模式分数
    pattern_score = 1.0 if traffic_data["request_pattern"] == "uniform" else 0.0

    # 计算总体风险分数
    risk_score = (
        weights["requests_per_second"] * rps_score
        + weights["unique_ips"] * ip_score
        + weights["pattern_score"] * pattern_score
    )

    return float(np.clip(risk_score, 0, 1))


def block_suspicious_ips() -> List[str]:
    """
    Block IPs that are identified as suspicious.
    在实际生产环境中，这里应该调用网络设备API或防火墙接口

    Returns:
        List[str]: List of blocked IP addresses
    """
    # 这里模拟封禁可疑IP的操作
    suspicious_ips = [
        "192.168.1.100",
        "192.168.1.101",
    ]  # 实际应该从监控系统获取

    for ip in suspicious_ips:
        # 在实际环境中，这里应该调用防火墙API
        print(f"Blocking suspicious IP: {ip}")
        # firewall_api.block_ip(ip)

    return suspicious_ips
