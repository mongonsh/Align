"""
IntegrationConcept: Partner team integration and API gateway
Purpose: Enable tight integration with partner team's systems
"""

import uuid
import json
import hmac
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import aiohttp
import asyncio


@dataclass
class PartnerTeam:
    """Represents a partner team configuration."""
    team_id: str
    team_name: str
    api_endpoint: str
    api_key: str
    webhook_url: Optional[str]
    shared_secret: str
    permissions: List[str]
    integration_type: str  # 'plugin', 'api', 'webhook', 'chrome_extension'
    is_active: bool = True


@dataclass
class IntegrationEvent:
    """Represents an integration event between teams."""
    event_id: str
    team_id: str
    event_type: str
    data: dict
    timestamp: datetime
    status: str = "pending"


class IntegrationConcept:
    """
    Manages partner team integrations and cross-team workflows.
    Supports multiple integration patterns: plugins, APIs, webhooks, Chrome extensions.
    """

    def __init__(self):
        self.partner_teams: Dict[str, PartnerTeam] = {}
        self.integration_events: List[IntegrationEvent] = []
        self.shared_state: Dict[str, Any] = {}
        self.webhook_handlers: Dict[str, callable] = {}
        
        # Register default webhook handlers
        self._register_default_handlers()

    def _register_default_handlers(self):
        """Register default webhook handlers for common events."""
        self.webhook_handlers.update({
            "mockup_generated": self._handle_mockup_generated,
            "feature_request_created": self._handle_feature_request,
            "collaboration_invite": self._handle_collaboration_invite,
            "state_sync": self._handle_state_sync
        })

    async def register_partner_team(
        self,
        team_name: str,
        api_endpoint: str,
        integration_type: str,
        permissions: List[str],
        webhook_url: Optional[str] = None
    ) -> PartnerTeam:
        """Register a new partner team for integration."""
        team_id = str(uuid.uuid4())
        api_key = self._generate_api_key()
        shared_secret = self._generate_shared_secret()
        
        partner = PartnerTeam(
            team_id=team_id,
            team_name=team_name,
            api_endpoint=api_endpoint,
            api_key=api_key,
            webhook_url=webhook_url,
            shared_secret=shared_secret,
            permissions=permissions,
            integration_type=integration_type
        )
        
        self.partner_teams[team_id] = partner
        
        # Send registration confirmation to partner
        await self._notify_partner(team_id, "team_registered", {
            "team_id": team_id,
            "api_key": api_key,
            "webhook_secret": shared_secret,
            "available_endpoints": self._get_available_endpoints(permissions)
        })
        
        return partner

    async def sync_state_with_partner(
        self,
        team_id: str,
        state_key: str,
        state_data: Any,
        sync_type: str = "update"
    ) -> dict:
        """Synchronize state with partner team."""
        if team_id not in self.partner_teams:
            raise ValueError("Partner team not found")
        
        partner = self.partner_teams[team_id]
        
        # Update shared state
        if sync_type == "update":
            self.shared_state[f"{team_id}:{state_key}"] = state_data
        elif sync_type == "merge":
            existing = self.shared_state.get(f"{team_id}:{state_key}", {})
            if isinstance(existing, dict) and isinstance(state_data, dict):
                existing.update(state_data)
                self.shared_state[f"{team_id}:{state_key}"] = existing
        
        # Notify partner of state change
        await self._notify_partner(team_id, "state_sync", {
            "state_key": state_key,
            "state_data": state_data,
            "sync_type": sync_type,
            "timestamp": datetime.now().isoformat()
        })
        
        return {
            "status": "synced",
            "team_id": team_id,
            "state_key": state_key
        }

    async def create_cross_team_workflow(
        self,
        workflow_name: str,
        participating_teams: List[str],
        workflow_steps: List[dict]
    ) -> dict:
        """Create a workflow that spans multiple teams."""
        workflow_id = str(uuid.uuid4())
        
        workflow = {
            "workflow_id": workflow_id,
            "name": workflow_name,
            "teams": participating_teams,
            "steps": workflow_steps,
            "current_step": 0,
            "status": "active",
            "created_at": datetime.now().isoformat()
        }
        
        # Notify all participating teams
        for team_id in participating_teams:
            await self._notify_partner(team_id, "workflow_created", workflow)
        
        return workflow

    async def handle_partner_webhook(
        self,
        team_id: str,
        event_type: str,
        payload: dict,
        signature: str
    ) -> dict:
        """Handle incoming webhook from partner team."""
        # Verify webhook signature
        if not self._verify_webhook_signature(team_id, payload, signature):
            raise ValueError("Invalid webhook signature")
        
        # Create integration event
        event = IntegrationEvent(
            event_id=str(uuid.uuid4()),
            team_id=team_id,
            event_type=event_type,
            data=payload,
            timestamp=datetime.now()
        )
        
        self.integration_events.append(event)
        
        # Handle the event
        if event_type in self.webhook_handlers:
            result = await self.webhook_handlers[event_type](team_id, payload)
            event.status = "processed"
        else:
            result = {"status": "unknown_event_type"}
            event.status = "failed"
        
        return result

    async def _handle_mockup_generated(self, team_id: str, payload: dict) -> dict:
        """Handle mockup generated event from partner."""
        # Partner team generated a mockup, sync it to our system
        mockup_data = payload.get("mockup_data", {})
        
        # Store in shared state
        await self.sync_state_with_partner(
            team_id,
            f"mockup_{mockup_data.get('mockup_id')}",
            mockup_data
        )
        
        return {"status": "mockup_synced"}

    async def _handle_feature_request(self, team_id: str, payload: dict) -> dict:
        """Handle feature request from partner team."""
        # Create feature request in our system
        from .feature_request import FeatureRequestConcept
        
        # This would be injected in real implementation
        feature_concept = FeatureRequestConcept()
        
        request_data = payload.get("request_data", {})
        await feature_concept.create_request(
            title=request_data.get("title", "Partner Team Request"),
            description=request_data.get("description", ""),
            user_id=f"partner_{team_id}",
            partner_team=self.partner_teams[team_id].team_name
        )
        
        return {"status": "feature_request_created"}

    async def _handle_collaboration_invite(self, team_id: str, payload: dict) -> dict:
        """Handle collaboration invitation from partner."""
        session_data = payload.get("session_data", {})
        
        # Auto-join collaboration session
        from .collaboration import CollaborationConcept
        
        # This would be injected in real implementation
        collab_concept = CollaborationConcept()
        
        session_id = session_data.get("session_id")
        user_id = f"partner_{team_id}"
        
        if session_id:
            await collab_concept.join_session(session_id, user_id)
        
        return {"status": "collaboration_joined"}

    async def _handle_state_sync(self, team_id: str, payload: dict) -> dict:
        """Handle state synchronization from partner."""
        state_updates = payload.get("state_updates", {})
        
        for key, value in state_updates.items():
            self.shared_state[f"{team_id}:{key}"] = value
        
        return {"status": "state_updated"}

    async def _notify_partner(self, team_id: str, event_type: str, data: dict):
        """Send notification to partner team via webhook."""
        if team_id not in self.partner_teams:
            return
        
        partner = self.partner_teams[team_id]
        if not partner.webhook_url:
            return
        
        payload = {
            "event_type": event_type,
            "data": data,
            "timestamp": datetime.now().isoformat(),
            "source_team": "align"
        }
        
        # Sign the payload
        signature = self._sign_payload(partner.shared_secret, payload)
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    partner.webhook_url,
                    json=payload,
                    headers={
                        "X-Webhook-Signature": signature,
                        "Content-Type": "application/json"
                    }
                ) as response:
                    if response.status != 200:
                        print(f"Failed to notify partner {team_id}: {response.status}")
        except Exception as e:
            print(f"Error notifying partner {team_id}: {e}")

    def _generate_api_key(self) -> str:
        """Generate API key for partner team."""
        return f"align_{uuid.uuid4().hex[:16]}"

    def _generate_shared_secret(self) -> str:
        """Generate shared secret for webhook signing."""
        return uuid.uuid4().hex

    def _sign_payload(self, secret: str, payload: dict) -> str:
        """Sign webhook payload with HMAC."""
        payload_bytes = json.dumps(payload, sort_keys=True).encode()
        signature = hmac.new(
            secret.encode(),
            payload_bytes,
            hashlib.sha256
        ).hexdigest()
        return f"sha256={signature}"

    def _verify_webhook_signature(self, team_id: str, payload: dict, signature: str) -> bool:
        """Verify webhook signature from partner."""
        if team_id not in self.partner_teams:
            return False
        
        partner = self.partner_teams[team_id]
        expected_signature = self._sign_payload(partner.shared_secret, payload)
        
        return hmac.compare_digest(signature, expected_signature)

    def _get_available_endpoints(self, permissions: List[str]) -> List[str]:
        """Get available API endpoints based on permissions."""
        endpoint_map = {
            "read_mockups": ["/api/mockup/{mockup_id}", "/api/mockups"],
            "create_mockups": ["/api/generate"],
            "read_features": ["/api/feature-requests"],
            "create_features": ["/api/feature-requests"],
            "collaborate": ["/api/collaboration/sessions"],
            "sync_state": ["/api/integration/sync"]
        }
        
        available = []
        for permission in permissions:
            available.extend(endpoint_map.get(permission, []))
        
        return available

    # Chrome Extension Integration Methods
    async def register_chrome_extension(
        self,
        extension_id: str,
        team_id: str,
        permissions: List[str]
    ) -> dict:
        """Register Chrome extension for partner team."""
        # Generate extension-specific API key
        extension_key = f"ext_{uuid.uuid4().hex[:12]}"
        
        # Store extension registration
        extension_data = {
            "extension_id": extension_id,
            "team_id": team_id,
            "api_key": extension_key,
            "permissions": permissions,
            "registered_at": datetime.now().isoformat()
        }
        
        self.shared_state[f"extension_{extension_id}"] = extension_data
        
        return {
            "status": "registered",
            "api_key": extension_key,
            "cors_origins": ["chrome-extension://" + extension_id],
            "available_endpoints": self._get_available_endpoints(permissions)
        }

    async def handle_extension_message(
        self,
        extension_id: str,
        message_type: str,
        data: dict
    ) -> dict:
        """Handle message from Chrome extension."""
        extension_key = f"extension_{extension_id}"
        
        if extension_key not in self.shared_state:
            raise ValueError("Extension not registered")
        
        extension_data = self.shared_state[extension_key]
        
        # Handle different message types
        if message_type == "capture_screenshot":
            return await self._handle_extension_screenshot(extension_id, data)
        elif message_type == "sync_mockup":
            return await self._handle_extension_mockup_sync(extension_id, data)
        elif message_type == "get_state":
            return await self._handle_extension_state_request(extension_id, data)
        else:
            return {"status": "unknown_message_type"}

    async def _handle_extension_screenshot(self, extension_id: str, data: dict) -> dict:
        """Handle screenshot capture from extension."""
        # Process screenshot data from extension
        screenshot_data = data.get("screenshot")
        page_url = data.get("url")
        
        # Store for processing
        capture_id = str(uuid.uuid4())
        self.shared_state[f"capture_{capture_id}"] = {
            "extension_id": extension_id,
            "screenshot": screenshot_data,
            "url": page_url,
            "captured_at": datetime.now().isoformat()
        }
        
        return {
            "status": "captured",
            "capture_id": capture_id,
            "next_step": "describe_changes"
        }

    async def _handle_extension_mockup_sync(self, extension_id: str, data: dict) -> dict:
        """Handle mockup synchronization with extension."""
        mockup_id = data.get("mockup_id")
        
        # Get mockup data (would integrate with MockupConcept)
        mockup_data = self.shared_state.get(f"mockup_{mockup_id}")
        
        if mockup_data:
            return {
                "status": "synced",
                "mockup_html": mockup_data.get("html"),
                "preview_url": f"/api/mockup/{mockup_id}/preview"
            }
        else:
            return {"status": "not_found"}

    async def _handle_extension_state_request(self, extension_id: str, data: dict) -> dict:
        """Handle state request from extension."""
        state_keys = data.get("keys", [])
        
        result = {}
        for key in state_keys:
            full_key = f"extension_{extension_id}:{key}"
            if full_key in self.shared_state:
                result[key] = self.shared_state[full_key]
        
        return {"status": "success", "state": result}

    def get_integration_stats(self) -> dict:
        """Get integration statistics."""
        return {
            "partner_teams": len(self.partner_teams),
            "active_integrations": len([p for p in self.partner_teams.values() if p.is_active]),
            "total_events": len(self.integration_events),
            "shared_state_keys": len(self.shared_state),
            "integration_types": list(set(p.integration_type for p in self.partner_teams.values()))
        }