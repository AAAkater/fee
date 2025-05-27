import uuid
from datetime import datetime

from llama_index.core.workflow import StopEvent, Workflow, step

from fee_agent.config import settings
from fee_agent.events import (
    DetectionResultEvent,
    MitigationEvent,
    ThresholdValidationEvent,
    TrafficAnalysisEvent,
    TrafficMonitorEvent,
)
from fee_agent.tools import (
    analyze_traffic,
    block_suspicious_ips,
    calculate_risk_score,
    log_detection,
    rate_limiter,
)


class DDoSDetectionWorkflow(Workflow):
    @step()
    def monitor_traffic(self, ev: TrafficMonitorEvent) -> TrafficAnalysisEvent:
        # Initialize rate limiter
        d_rate_limiter = rate_limiter(
            max_requests=settings.DDOS_THRESHOLD,
            time_window=settings.RATE_LIMIT_WINDOW,
        )
        # Analyze incoming traffic
        traffic_analysis = analyze_traffic(ev.traffic_data)
        return TrafficAnalysisEvent(
            alert_message=f"Traffic analysis result: {traffic_analysis}",
            risk_score=calculate_risk_score(ev.traffic_data),
            analysis_details={
                "timestamp": ev.timestamp,
                "source_ip": ev.ip_address,
                "analysis_result": traffic_analysis,
            },
        )

    @step()
    def validate_thresholds(
        self, ev: TrafficAnalysisEvent
    ) -> ThresholdValidationEvent:
        is_exceeded = ev.risk_score > settings.RISK_THRESHOLD
        return ThresholdValidationEvent(
            is_exceeded=is_exceeded,
            current_value=ev.risk_score,
            threshold=settings.RISK_THRESHOLD,
            validation_type="risk_score",
        )

    @step()
    def apply_mitigation(self, ev: ThresholdValidationEvent) -> MitigationEvent:
        if ev.is_exceeded:
            blocked_ips = block_suspicious_ips()
            return MitigationEvent(
                action_taken="ip_blocking",
                blocked_ips=blocked_ips,
                mitigation_time=datetime.now(),
            )
        return MitigationEvent(
            action_taken="none",
            blocked_ips=[],
            mitigation_time=datetime.now(),
        )

    @step()
    def complete_detection(self, ev: MitigationEvent) -> DetectionResultEvent:
        return DetectionResultEvent(
            resolution_message="DDoS attack mitigated"
            if ev.blocked_ips
            else "Traffic normal",
            incident_id=str(uuid.uuid4()),
            detection_time=datetime.now(),
            severity="high" if ev.blocked_ips else "low",
        )

    @step()
    def finalize(self, ev: DetectionResultEvent) -> StopEvent:
        log_detection(
            incident_id=ev.incident_id,
            severity=ev.severity,
            message=ev.resolution_message,
            timestamp=ev.detection_time,
        )
        return StopEvent()


if __name__ == "__main__":
    initial_event = TrafficMonitorEvent(
        ip_address="192.168.1.100",
        request_count=1000,
        traffic_data={
            "requests_per_second": 500,
            "unique_ips": 5,
            "request_pattern": "uniform",
        },
        timestamp=datetime.now(),
    )

    workflow = DDoSDetectionWorkflow()
    workflow.run(initial_event)
