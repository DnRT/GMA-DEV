import logging
from abc import ABC, abstractmethod
from typing import List
from src.core.models import Incident, ReportSummary

logger = logging.getLogger("PluginManager")


class BasePlugin(ABC):
    """Abstract Base Class for OpsSentinel Lifecycle Plugins."""

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    async def on_incident_pre_sanitize(self, incident: Incident) -> Incident:
        """Called before the incident is sanitized."""
        return incident

    async def on_incident_post_sanitize(self, incident: Incident) -> Incident:
        """Called after the incident is sanitized and before channel dispatch."""
        return incident

    async def on_report_generate(self, report: ReportSummary) -> ReportSummary:
        """Called when an aggregated periodic report is generated."""
        return report


class PluginManager:
    """Manages plugin registration and lifecycle hook dispatch."""

    def __init__(self):
        self._plugins: List[BasePlugin] = []

    def register(self, plugin: BasePlugin):
        logger.info(f"Registered OpsSentinel Plugin: {plugin.name}")
        self._plugins.append(plugin)

    async def apply_incident_post_sanitize(self, incident: Incident) -> Incident:
        current = incident
        for plugin in self._plugins:
            try:
                current = await plugin.on_incident_post_sanitize(current)
            except Exception as e:
                logger.error(f"Plugin {plugin.name} failed during on_incident_post_sanitize: {str(e)}")
        return current

    async def apply_report_generate(self, report: ReportSummary) -> ReportSummary:
        current = report
        for plugin in self._plugins:
            try:
                current = await plugin.on_report_generate(current)
            except Exception as e:
                logger.error(f"Plugin {plugin.name} failed during on_report_generate: {str(e)}")
        return current


plugin_manager = PluginManager()
