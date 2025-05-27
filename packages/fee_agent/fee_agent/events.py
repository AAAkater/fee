from datetime import datetime

from llama_index.core.workflow import Event, StartEvent


class TrafficMonitorEvent(StartEvent):
    ip_address: str
    request_count: int
    traffic_data: dict
    timestamp: datetime


class TrafficAnalysisEvent(Event):
    alert_message: str
    risk_score: float
    analysis_details: dict


class ThresholdValidationEvent(Event):
    is_exceeded: bool
    current_value: float
    threshold: float
    validation_type: str


class MitigationEvent(Event):
    action_taken: str
    blocked_ips: list
    mitigation_time: datetime


class DetectionResultEvent(Event):
    resolution_message: str
    incident_id: str
    detection_time: datetime
    severity: str
