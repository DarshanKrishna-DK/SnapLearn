"""
Integration Hub with Webhooks and External APIs - Phase 5
Comprehensive integration system for third-party connectivity
"""

import os
import logging
import asyncio
import json
import uuid
import hmac
import hashlib
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime, timedelta
from pathlib import Path
from enum import Enum
from dataclasses import dataclass, asdict
import aiohttp
from fastapi import BackgroundTasks

from utils import schedule_async_init

logger = logging.getLogger(__name__)

class EventType(str, Enum):
    """Webhook event types"""
    STUDENT_REGISTERED = "student.registered"
    ASSESSMENT_COMPLETED = "assessment.completed"
    VIDEO_GENERATED = "video.generated"
    CONVERSATION_STARTED = "conversation.started"
    LEARNING_MILESTONE = "learning.milestone"
    DIFFICULTY_ADAPTED = "difficulty.adapted"
    BATCH_COMPLETED = "batch.completed"
    CERTIFICATION_EARNED = "certification.earned"
    ERROR_OCCURRED = "error.occurred"

class IntegrationStatus(str, Enum):
    """Integration connection status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    PENDING = "pending"

class ExternalSystem(str, Enum):
    """Supported external systems"""
    GOOGLE_CLASSROOM = "google_classroom"
    CANVAS_LMS = "canvas_lms"
    BLACKBOARD = "blackboard"
    MOODLE = "moodle"
    SCHOOLOGY = "schoology"
    SLACK = "slack"
    MICROSOFT_TEAMS = "microsoft_teams"
    ZOOM = "zoom"
    SALESFORCE = "salesforce"
    HUBSPOT = "hubspot"
    ZAPIER = "zapier"
    CUSTOM_API = "custom_api"

@dataclass
class WebhookEndpoint:
    """Webhook endpoint configuration"""
    endpoint_id: str
    org_id: str
    url: str
    secret_key: str
    events: List[EventType]
    is_active: bool = True
    created_at: datetime = None
    last_triggered: Optional[datetime] = None
    success_count: int = 0
    failure_count: int = 0
    retry_policy: Dict[str, Any] = None

@dataclass
class ExternalIntegration:
    """External system integration configuration"""
    integration_id: str
    org_id: str
    system_type: ExternalSystem
    name: str
    config: Dict[str, Any]
    credentials: Dict[str, Any]
    status: IntegrationStatus
    created_at: datetime
    last_sync: Optional[datetime] = None
    sync_settings: Dict[str, Any] = None
    error_log: List[str] = None

@dataclass
class WebhookEvent:
    """Webhook event data"""
    event_id: str
    event_type: EventType
    org_id: str
    data: Dict[str, Any]
    timestamp: datetime
    source: str = "snaplearn_ai"
    metadata: Dict[str, Any] = None

class IntegrationHub:
    """Comprehensive integration hub with webhooks and external API connectivity"""
    
    def __init__(self):
        self.integrations_dir = Path("../integrations")
        self.webhooks_dir = Path("../webhooks")
        self.logs_dir = Path("../integration_logs")
        
        # Create directories
        for directory in [self.integrations_dir, self.webhooks_dir, self.logs_dir]:
            directory.mkdir(exist_ok=True)
        
        # Webhook endpoints and integrations
        self.webhook_endpoints: Dict[str, WebhookEndpoint] = {}
        self.external_integrations: Dict[str, ExternalIntegration] = {}
        
        # Event queue and processing
        self.event_queue: List[WebhookEvent] = []
        self.event_handlers: Dict[EventType, List[Callable]] = {}
        self.is_processing_events = False
        
        # HTTP client for external requests
        self.http_session: Optional[aiohttp.ClientSession] = None
        
        # Integration analytics
        self.integration_analytics = {
            "total_webhooks": 0,
            "successful_deliveries": 0,
            "failed_deliveries": 0,
            "integrations_active": 0,
            "events_processed": 0,
            "average_response_time": 0.0
        }
        
        # Initialize system
        self._init_default_integrations()
        self._init_event_handlers()
        
        # Start background tasks
        schedule_async_init(self._init_http_session())
        schedule_async_init(self._event_processor())
        
        logger.info("Integration Hub initialized with webhook and external API support")
    
    async def _init_http_session(self):
        """Initialize HTTP session for external requests"""
        try:
            timeout = aiohttp.ClientTimeout(total=30, connect=10)
            self.http_session = aiohttp.ClientSession(timeout=timeout)
            logger.info("HTTP session initialized for external integrations")
        except Exception as e:
            logger.error(f"Error initializing HTTP session: {e}")
    
    def _init_default_integrations(self):
        """Initialize default integration templates"""
        
        # Google Classroom integration template
        self.integration_templates = {
            ExternalSystem.GOOGLE_CLASSROOM: {
                "name": "Google Classroom",
                "description": "Sync students, assignments, and grades with Google Classroom",
                "required_credentials": ["client_id", "client_secret", "refresh_token"],
                "supported_features": ["student_sync", "assignment_creation", "grade_sync"],
                "webhook_events": [EventType.ASSESSMENT_COMPLETED, EventType.CERTIFICATION_EARNED],
                "api_endpoints": {
                    "base_url": "https://classroom.googleapis.com/v1",
                    "auth_type": "oauth2"
                }
            },
            
            ExternalSystem.SLACK: {
                "name": "Slack Integration",
                "description": "Send learning notifications and updates to Slack channels",
                "required_credentials": ["bot_token", "webhook_url"],
                "supported_features": ["notifications", "progress_updates", "achievement_alerts"],
                "webhook_events": [EventType.LEARNING_MILESTONE, EventType.CERTIFICATION_EARNED],
                "api_endpoints": {
                    "base_url": "https://slack.com/api",
                    "auth_type": "bearer_token"
                }
            },
            
            ExternalSystem.ZAPIER: {
                "name": "Zapier Integration",
                "description": "Connect SnapLearn AI with 5000+ apps through Zapier",
                "required_credentials": ["webhook_url"],
                "supported_features": ["workflow_automation", "data_sync", "notifications"],
                "webhook_events": list(EventType),
                "api_endpoints": {
                    "base_url": "custom",
                    "auth_type": "webhook"
                }
            }
        }
    
    def _init_event_handlers(self):
        """Initialize event handlers for different event types"""
        
        # Register default event handlers
        self.register_event_handler(EventType.ASSESSMENT_COMPLETED, self._handle_assessment_completed)
        self.register_event_handler(EventType.VIDEO_GENERATED, self._handle_video_generated)
        self.register_event_handler(EventType.CERTIFICATION_EARNED, self._handle_certification_earned)
        self.register_event_handler(EventType.LEARNING_MILESTONE, self._handle_learning_milestone)
    
    # Webhook Management
    
    async def create_webhook_endpoint(
        self,
        org_id: str,
        url: str,
        events: List[EventType],
        name: Optional[str] = None,
        retry_policy: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create new webhook endpoint"""
        
        try:
            endpoint_id = f"webhook_{uuid.uuid4().hex[:12]}"
            secret_key = secrets.token_urlsafe(32)
            
            webhook = WebhookEndpoint(
                endpoint_id=endpoint_id,
                org_id=org_id,
                url=url,
                secret_key=secret_key,
                events=events,
                created_at=datetime.now(),
                retry_policy=retry_policy or {
                    "max_retries": 3,
                    "retry_delay_seconds": [1, 5, 15],
                    "timeout_seconds": 30
                }
            )
            
            self.webhook_endpoints[endpoint_id] = webhook
            
            # Update analytics
            self.integration_analytics["total_webhooks"] += 1
            
            logger.info(f"Created webhook endpoint: {endpoint_id} for organization: {org_id}")
            
            return endpoint_id
            
        except Exception as e:
            logger.error(f"Error creating webhook endpoint: {str(e)}")
            raise Exception(f"Webhook creation failed: {str(e)}")
    
    async def trigger_webhook_event(
        self,
        event_type: EventType,
        org_id: str,
        data: Dict[str, Any],
        source: str = "snaplearn_ai",
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Trigger webhook event for organization"""
        
        try:
            # Create event
            event = WebhookEvent(
                event_id=f"event_{uuid.uuid4().hex[:12]}",
                event_type=event_type,
                org_id=org_id,
                data=data,
                timestamp=datetime.now(),
                source=source,
                metadata=metadata or {}
            )
            
            # Add to processing queue
            self.event_queue.append(event)
            
            # Update analytics
            self.integration_analytics["events_processed"] += 1
            
            logger.info(f"Webhook event queued: {event.event_id} - {event_type.value}")
            
        except Exception as e:
            logger.error(f"Error triggering webhook event: {str(e)}")
    
    async def _event_processor(self):
        """Background task to process webhook events"""
        
        while True:
            try:
                if not self.event_queue or self.is_processing_events:
                    await asyncio.sleep(1)
                    continue
                
                self.is_processing_events = True
                
                # Process events in batches
                batch_size = 10
                events_to_process = self.event_queue[:batch_size]
                self.event_queue = self.event_queue[batch_size:]
                
                # Process events concurrently
                tasks = [self._process_single_event(event) for event in events_to_process]
                await asyncio.gather(*tasks, return_exceptions=True)
                
                self.is_processing_events = False
                
            except Exception as e:
                logger.error(f"Error in event processor: {str(e)}")
                self.is_processing_events = False
                await asyncio.sleep(5)  # Wait before retrying
    
    async def _process_single_event(self, event: WebhookEvent):
        """Process a single webhook event"""
        
        try:
            # Find relevant webhook endpoints
            relevant_endpoints = [
                webhook for webhook in self.webhook_endpoints.values()
                if webhook.org_id == event.org_id 
                and event.event_type in webhook.events
                and webhook.is_active
            ]
            
            if not relevant_endpoints:
                logger.debug(f"No webhooks configured for event: {event.event_type} in org: {event.org_id}")
                return
            
            # Send to each endpoint
            for endpoint in relevant_endpoints:
                await self._deliver_webhook(endpoint, event)
            
            # Run internal event handlers
            await self._run_event_handlers(event)
            
        except Exception as e:
            logger.error(f"Error processing event {event.event_id}: {str(e)}")
    
    async def _deliver_webhook(self, endpoint: WebhookEndpoint, event: WebhookEvent):
        """Deliver webhook to external endpoint"""
        
        if not self.http_session:
            logger.error("HTTP session not available for webhook delivery")
            return
        
        try:
            # Prepare webhook payload
            payload = {
                "event_id": event.event_id,
                "event_type": event.event_type.value,
                "timestamp": event.timestamp.isoformat(),
                "org_id": event.org_id,
                "data": event.data,
                "metadata": event.metadata
            }
            
            # Generate signature
            signature = self._generate_webhook_signature(
                json.dumps(payload, sort_keys=True),
                endpoint.secret_key
            )
            
            headers = {
                "Content-Type": "application/json",
                "X-SnapLearn-Event": event.event_type.value,
                "X-SnapLearn-Signature": signature,
                "X-SnapLearn-Timestamp": str(int(event.timestamp.timestamp())),
                "User-Agent": "SnapLearnAI-Webhooks/5.0.0"
            }
            
            # Attempt delivery with retries
            retry_policy = endpoint.retry_policy
            max_retries = retry_policy.get("max_retries", 3)
            retry_delays = retry_policy.get("retry_delay_seconds", [1, 5, 15])
            timeout = retry_policy.get("timeout_seconds", 30)
            
            for attempt in range(max_retries + 1):
                try:
                    start_time = datetime.now()
                    
                    async with self.http_session.post(
                        endpoint.url,
                        json=payload,
                        headers=headers,
                        timeout=aiohttp.ClientTimeout(total=timeout)
                    ) as response:
                        response_time = (datetime.now() - start_time).total_seconds()
                        
                        if response.status < 400:
                            # Success
                            endpoint.success_count += 1
                            endpoint.last_triggered = datetime.now()
                            
                            self.integration_analytics["successful_deliveries"] += 1
                            self._update_response_time(response_time)
                            
                            logger.info(f"Webhook delivered successfully: {endpoint.endpoint_id}")
                            return
                        else:
                            # HTTP error
                            error_text = await response.text()
                            raise aiohttp.ClientResponseError(
                                request_info=response.request_info,
                                history=response.history,
                                status=response.status,
                                message=error_text
                            )
                
                except Exception as e:
                    if attempt == max_retries:
                        # Final attempt failed
                        endpoint.failure_count += 1
                        self.integration_analytics["failed_deliveries"] += 1
                        
                        await self._log_webhook_failure(endpoint, event, str(e))
                        logger.error(f"Webhook delivery failed after {max_retries} retries: {endpoint.endpoint_id}")
                        break
                    else:
                        # Retry with delay
                        delay = retry_delays[min(attempt, len(retry_delays) - 1)]
                        await asyncio.sleep(delay)
                        logger.warning(f"Webhook delivery attempt {attempt + 1} failed, retrying in {delay}s")
        
        except Exception as e:
            logger.error(f"Error in webhook delivery: {str(e)}")
    
    def _generate_webhook_signature(self, payload: str, secret: str) -> str:
        """Generate HMAC signature for webhook verification"""
        return hmac.new(
            secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
    
    def _update_response_time(self, response_time: float):
        """Update average response time analytics"""
        
        current_avg = self.integration_analytics["average_response_time"]
        successful_deliveries = self.integration_analytics["successful_deliveries"]
        
        if successful_deliveries == 1:
            self.integration_analytics["average_response_time"] = response_time
        else:
            # Calculate rolling average
            self.integration_analytics["average_response_time"] = (
                (current_avg * (successful_deliveries - 1) + response_time) / successful_deliveries
            )
    
    async def _log_webhook_failure(self, endpoint: WebhookEndpoint, event: WebhookEvent, error: str):
        """Log webhook delivery failure"""
        
        failure_log = {
            "timestamp": datetime.now().isoformat(),
            "endpoint_id": endpoint.endpoint_id,
            "event_id": event.event_id,
            "event_type": event.event_type.value,
            "error": error,
            "url": endpoint.url
        }
        
        log_file = self.logs_dir / f"webhook_failures_{datetime.now().strftime('%Y%m')}.json"
        
        # Append to log file
        existing_logs = []
        if log_file.exists():
            with open(log_file, 'r') as f:
                existing_logs = json.load(f)
        
        existing_logs.append(failure_log)
        
        with open(log_file, 'w') as f:
            json.dump(existing_logs, f, indent=2)
    
    # Event Handling System
    
    def register_event_handler(self, event_type: EventType, handler: Callable):
        """Register event handler for internal processing"""
        
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        
        self.event_handlers[event_type].append(handler)
        logger.info(f"Registered event handler for: {event_type.value}")
    
    async def _run_event_handlers(self, event: WebhookEvent):
        """Run internal event handlers"""
        
        handlers = self.event_handlers.get(event.event_type, [])
        
        for handler in handlers:
            try:
                await handler(event)
            except Exception as e:
                logger.error(f"Event handler error for {event.event_type}: {e}")
    
    async def _handle_assessment_completed(self, event: WebhookEvent):
        """Handle assessment completion event"""
        
        data = event.data
        logger.info(f"Assessment completed: {data.get('assessment_id')} - Score: {data.get('score', 'N/A')}")
        
        # Trigger LMS grade sync if configured
        await self._sync_grade_to_lms(event.org_id, data)
        
        # Send achievement notifications
        if data.get("score", 0) >= 90:
            await self._send_achievement_notification(event.org_id, data, "high_score")
    
    async def _handle_video_generated(self, event: WebhookEvent):
        """Handle video generation completion event"""
        
        data = event.data
        logger.info(f"Video generated: {data.get('video_id')} - Topic: {data.get('topic', 'Unknown')}")
        
        # Auto-share to configured platforms
        await self._auto_share_content(event.org_id, data, "video")
    
    async def _handle_certification_earned(self, event: WebhookEvent):
        """Handle certification earned event"""
        
        data = event.data
        logger.info(f"Certification earned: {data.get('certificate_id')} by student: {data.get('student_id')}")
        
        # Send congratulations through configured channels
        await self._send_certification_notification(event.org_id, data)
        
        # Update external credentialing systems
        await self._sync_certification_external(event.org_id, data)
    
    async def _handle_learning_milestone(self, event: WebhookEvent):
        """Handle learning milestone achievement event"""
        
        data = event.data
        logger.info(f"Learning milestone: {data.get('milestone')} reached by: {data.get('student_id')}")
        
        # Trigger celebration workflows
        await self._trigger_milestone_celebration(event.org_id, data)
    
    # External Integration Management
    
    async def create_integration(
        self,
        org_id: str,
        system_type: ExternalSystem,
        name: str,
        credentials: Dict[str, Any],
        config: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create new external system integration"""
        
        try:
            integration_id = f"int_{system_type.value}_{uuid.uuid4().hex[:8]}"
            
            # Validate credentials
            is_valid = await self._validate_integration_credentials(system_type, credentials)
            
            integration = ExternalIntegration(
                integration_id=integration_id,
                org_id=org_id,
                system_type=system_type,
                name=name,
                config=config or {},
                credentials=self._encrypt_credentials(credentials),  # Encrypt sensitive data
                status=IntegrationStatus.ACTIVE if is_valid else IntegrationStatus.ERROR,
                created_at=datetime.now(),
                sync_settings={
                    "auto_sync": True,
                    "sync_interval_minutes": 60,
                    "batch_size": 50
                },
                error_log=[]
            )
            
            self.external_integrations[integration_id] = integration
            
            if is_valid:
                self.integration_analytics["integrations_active"] += 1
            
            logger.info(f"Created integration: {integration_id} for {system_type.value}")
            
            return integration_id
            
        except Exception as e:
            logger.error(f"Error creating integration: {str(e)}")
            raise Exception(f"Integration creation failed: {str(e)}")
    
    async def _validate_integration_credentials(
        self,
        system_type: ExternalSystem,
        credentials: Dict[str, Any]
    ) -> bool:
        """Validate credentials for external system"""
        
        template = self.integration_templates.get(system_type)
        if not template:
            return False
        
        # Check required credentials
        required_creds = template["required_credentials"]
        for cred in required_creds:
            if cred not in credentials or not credentials[cred]:
                logger.warning(f"Missing required credential: {cred}")
                return False
        
        # Test connection (simplified validation)
        try:
            if system_type == ExternalSystem.SLACK:
                return await self._test_slack_connection(credentials)
            elif system_type == ExternalSystem.GOOGLE_CLASSROOM:
                return await self._test_google_classroom_connection(credentials)
            elif system_type == ExternalSystem.ZAPIER:
                return await self._test_zapier_webhook(credentials)
            else:
                return True  # Assume valid for other systems
        except Exception as e:
            logger.error(f"Credential validation failed for {system_type}: {e}")
            return False
    
    async def _test_slack_connection(self, credentials: Dict[str, Any]) -> bool:
        """Test Slack connection"""
        
        if not self.http_session:
            return False
        
        try:
            headers = {"Authorization": f"Bearer {credentials['bot_token']}"}
            
            async with self.http_session.get(
                "https://slack.com/api/auth.test",
                headers=headers
            ) as response:
                data = await response.json()
                return data.get("ok", False)
        
        except Exception:
            return False
    
    async def _test_google_classroom_connection(self, credentials: Dict[str, Any]) -> bool:
        """Test Google Classroom connection"""
        
        # This would implement OAuth2 token validation
        # For demo, return True if credentials look valid
        return bool(
            credentials.get("client_id") and 
            credentials.get("client_secret") and
            credentials.get("refresh_token")
        )
    
    async def _test_zapier_webhook(self, credentials: Dict[str, Any]) -> bool:
        """Test Zapier webhook URL"""
        
        if not self.http_session:
            return False
        
        try:
            test_payload = {
                "test": True,
                "timestamp": datetime.now().isoformat(),
                "message": "SnapLearn AI connection test"
            }
            
            async with self.http_session.post(
                credentials["webhook_url"],
                json=test_payload,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                return response.status < 400
        
        except Exception:
            return False
    
    def _encrypt_credentials(self, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """Encrypt sensitive credential data"""
        
        # In production, use proper encryption
        # For demo, just mark as encrypted
        encrypted = {}
        for key, value in credentials.items():
            if isinstance(value, str) and len(value) > 10:
                encrypted[key] = f"encrypted:{hashlib.sha256(value.encode()).hexdigest()[:16]}"
            else:
                encrypted[key] = value
        
        return encrypted
    
    # Specialized Integration Handlers
    
    async def _sync_grade_to_lms(self, org_id: str, assessment_data: Dict[str, Any]):
        """Sync assessment grade to external LMS"""
        
        # Find LMS integrations for organization
        lms_integrations = [
            integration for integration in self.external_integrations.values()
            if integration.org_id == org_id
            and integration.system_type in [ExternalSystem.GOOGLE_CLASSROOM, ExternalSystem.CANVAS_LMS]
            and integration.status == IntegrationStatus.ACTIVE
        ]
        
        for integration in lms_integrations:
            try:
                await self._sync_to_specific_lms(integration, assessment_data)
            except Exception as e:
                logger.error(f"LMS sync failed for {integration.integration_id}: {e}")
    
    async def _sync_to_specific_lms(self, integration: ExternalIntegration, data: Dict[str, Any]):
        """Sync data to specific LMS system"""
        
        if integration.system_type == ExternalSystem.GOOGLE_CLASSROOM:
            await self._sync_to_google_classroom(integration, data)
        elif integration.system_type == ExternalSystem.CANVAS_LMS:
            await self._sync_to_canvas(integration, data)
    
    async def _sync_to_google_classroom(self, integration: ExternalIntegration, data: Dict[str, Any]):
        """Sync assessment result to Google Classroom"""
        
        logger.info(f"Syncing to Google Classroom: Assessment {data.get('assessment_id')}")
        # Implementation would use Google Classroom API
        # For demo, just log the sync
    
    async def _send_achievement_notification(
        self,
        org_id: str,
        data: Dict[str, Any],
        achievement_type: str
    ):
        """Send achievement notification through configured channels"""
        
        # Find notification integrations
        notification_integrations = [
            integration for integration in self.external_integrations.values()
            if integration.org_id == org_id
            and integration.system_type in [ExternalSystem.SLACK, ExternalSystem.MICROSOFT_TEAMS]
            and integration.status == IntegrationStatus.ACTIVE
        ]
        
        message = self._format_achievement_message(data, achievement_type)
        
        for integration in notification_integrations:
            try:
                await self._send_notification_to_channel(integration, message)
            except Exception as e:
                logger.error(f"Notification failed for {integration.integration_id}: {e}")
    
    def _format_achievement_message(self, data: Dict[str, Any], achievement_type: str) -> str:
        """Format achievement message for notifications"""
        
        student_id = data.get("student_id", "Student")
        score = data.get("score", "N/A")
        topic = data.get("topic", "assessment")
        
        if achievement_type == "high_score":
            return f"🎉 Excellent work! {student_id} scored {score}% on {topic}!"
        elif achievement_type == "certification":
            return f"🏆 Congratulations! {student_id} earned certification in {topic}!"
        elif achievement_type == "milestone":
            return f"🌟 Milestone achieved! {student_id} completed {topic}!"
        else:
            return f"✅ Great progress by {student_id} in {topic}!"
    
    async def _send_notification_to_channel(
        self,
        integration: ExternalIntegration,
        message: str
    ):
        """Send notification to external channel"""
        
        if integration.system_type == ExternalSystem.SLACK:
            await self._send_slack_message(integration, message)
        elif integration.system_type == ExternalSystem.MICROSOFT_TEAMS:
            await self._send_teams_message(integration, message)
    
    async def _send_slack_message(self, integration: ExternalIntegration, message: str):
        """Send message to Slack channel"""
        
        webhook_url = integration.config.get("webhook_url")
        if not webhook_url or not self.http_session:
            return
        
        try:
            payload = {
                "text": message,
                "username": "SnapLearn AI",
                "icon_emoji": ":books:"
            }
            
            async with self.http_session.post(webhook_url, json=payload) as response:
                if response.status == 200:
                    logger.info("Slack notification sent successfully")
                else:
                    logger.warning(f"Slack notification failed: {response.status}")
        
        except Exception as e:
            logger.error(f"Slack notification error: {e}")
    
    # API Integration Management
    
    async def sync_with_external_system(
        self,
        integration_id: str,
        sync_type: str = "full"
    ) -> Dict[str, Any]:
        """Sync data with external system"""
        
        if integration_id not in self.external_integrations:
            raise ValueError("Integration not found")
        
        integration = self.external_integrations[integration_id]
        
        try:
            sync_start = datetime.now()
            
            # Perform sync based on system type
            if integration.system_type == ExternalSystem.GOOGLE_CLASSROOM:
                sync_result = await self._sync_google_classroom_data(integration, sync_type)
            elif integration.system_type == ExternalSystem.CANVAS_LMS:
                sync_result = await self._sync_canvas_data(integration, sync_type)
            else:
                sync_result = {"status": "not_implemented", "system": integration.system_type.value}
            
            # Update integration status
            integration.last_sync = datetime.now()
            integration.status = IntegrationStatus.ACTIVE
            
            sync_duration = (datetime.now() - sync_start).total_seconds()
            
            return {
                "integration_id": integration_id,
                "sync_type": sync_type,
                "status": "completed",
                "duration_seconds": sync_duration,
                "result": sync_result
            }
            
        except Exception as e:
            # Update error status
            integration.status = IntegrationStatus.ERROR
            if integration.error_log is None:
                integration.error_log = []
            integration.error_log.append(f"{datetime.now().isoformat()}: {str(e)}")
            
            logger.error(f"Sync failed for integration {integration_id}: {e}")
            raise Exception(f"Sync failed: {str(e)}")
    
    async def _sync_google_classroom_data(self, integration: ExternalIntegration, sync_type: str) -> Dict[str, Any]:
        """Sync data with Google Classroom"""
        
        # This would implement actual Google Classroom API integration
        # For demo, return simulated sync result
        
        return {
            "students_synced": 25,
            "assignments_created": 3,
            "grades_updated": 18,
            "last_sync": datetime.now().isoformat()
        }
    
    # Analytics and Monitoring
    
    async def get_integration_analytics(self) -> Dict[str, Any]:
        """Get comprehensive integration analytics"""
        
        # Calculate webhook success rate
        total_deliveries = (
            self.integration_analytics["successful_deliveries"] + 
            self.integration_analytics["failed_deliveries"]
        )
        
        success_rate = (
            self.integration_analytics["successful_deliveries"] / total_deliveries
            if total_deliveries > 0 else 1.0
        )
        
        return {
            "webhook_analytics": {
                **self.integration_analytics,
                "success_rate": success_rate,
                "active_endpoints": len([w for w in self.webhook_endpoints.values() if w.is_active])
            },
            "integration_status": {
                "total_integrations": len(self.external_integrations),
                "active_integrations": len([i for i in self.external_integrations.values() if i.status == IntegrationStatus.ACTIVE]),
                "error_integrations": len([i for i in self.external_integrations.values() if i.status == IntegrationStatus.ERROR])
            },
            "system_performance": {
                "event_queue_size": len(self.event_queue),
                "processing_status": "active" if self.is_processing_events else "idle",
                "average_webhook_response_time": self.integration_analytics["average_response_time"]
            }
        }
    
    async def get_webhook_logs(
        self,
        endpoint_id: Optional[str] = None,
        days: int = 7
    ) -> Dict[str, Any]:
        """Get webhook delivery logs"""
        
        logs = []
        
        # For demo, return sample logs
        sample_logs = [
            {
                "timestamp": (datetime.now() - timedelta(hours=2)).isoformat(),
                "endpoint_id": endpoint_id or "webhook_demo_123",
                "event_type": "assessment.completed",
                "status": "success",
                "response_time_ms": 245
            },
            {
                "timestamp": (datetime.now() - timedelta(hours=5)).isoformat(),
                "endpoint_id": endpoint_id or "webhook_demo_123",
                "event_type": "video.generated",
                "status": "success",
                "response_time_ms": 189
            }
        ]
        
        return {
            "logs": sample_logs,
            "summary": {
                "total_events": len(sample_logs),
                "success_rate": 1.0,
                "average_response_time": 217
            }
        }
    
    # Utility Methods
    
    def get_integration_template(self, system_type: ExternalSystem) -> Optional[Dict[str, Any]]:
        """Get integration template for external system"""
        return self.integration_templates.get(system_type)
    
    def list_supported_systems(self) -> List[Dict[str, Any]]:
        """List all supported external systems"""
        
        return [
            {
                "system_type": system.value,
                "template": template
            }
            for system, template in self.integration_templates.items()
        ]
    
    async def test_webhook_endpoint(self, endpoint_id: str) -> Dict[str, Any]:
        """Send test webhook to endpoint"""
        
        if endpoint_id not in self.webhook_endpoints:
            raise ValueError("Webhook endpoint not found")
        
        endpoint = self.webhook_endpoints[endpoint_id]
        
        # Send test event
        test_event = WebhookEvent(
            event_id=f"test_{uuid.uuid4().hex[:8]}",
            event_type=EventType.ERROR_OCCURRED,  # Use error type for tests
            org_id=endpoint.org_id,
            data={"test": True, "message": "SnapLearn AI webhook test"},
            timestamp=datetime.now(),
            source="webhook_test"
        )
        
        await self._deliver_webhook(endpoint, test_event)
        
        return {
            "endpoint_id": endpoint_id,
            "test_sent": True,
            "timestamp": datetime.now().isoformat()
        }
    
    def is_healthy(self) -> bool:
        """Check if integration hub is healthy"""
        return (
            len(self.event_queue) < 1000 and  # Queue not overloaded
            not (self.is_processing_events and len(self.event_queue) > 100)  # Processing keeping up
        )