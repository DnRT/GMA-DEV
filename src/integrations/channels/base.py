from abc import ABC, abstractmethod
from src.core.models import Incident, ReportSummary


class NotificationChannel(ABC):
    """Abstract Base Class for OpsSentinel Notification Channels."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Returns the channel identifier."""
        pass

    @abstractmethod
    async def send_incident(self, incident: Incident) -> bool:
        """Dispatches an incident alert to the destination channel."""
        pass

    @abstractmethod
    async def send_report(self, report: ReportSummary) -> bool:
        """Dispatches an aggregated statistics/health report to the destination channel."""
        pass
