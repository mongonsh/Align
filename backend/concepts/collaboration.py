"""
CollaborationConcept: Multi-user real-time collaboration
Purpose: Multiple users edit same mockup -> Sync state across devices
"""

import uuid
import json
from datetime import datetime
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, asdict
import asyncio


@dataclass
class CollaborationSession:
    """Represents an active collaboration session."""
    session_id: str
    mockup_id: str
    created_by: str
    created_at: datetime
    participants: Set[str]
    is_active: bool = True


@dataclass
class CollaborationEvent:
    """Represents a collaboration event (edit, cursor, etc.)."""
    event_id: str
    session_id: str
    user_id: str
    event_type: str  # 'edit', 'cursor', 'selection', 'comment'
    data: dict
    timestamp: datetime


class CollaborationConcept:
    """
    Manages real-time collaboration sessions.
    Handles multi-user editing, conflict resolution, and state synchronization.
    """

    def __init__(self):
        self.sessions: Dict[str, CollaborationSession] = {}
        self.events: Dict[str, List[CollaborationEvent]] = {}
        self.user_sessions: Dict[str, Set[str]] = {}  # user_id -> session_ids
        self.websocket_connections: Dict[str, List] = {}  # session_id -> websockets
        
    async def create_session(
        self,
        mockup_id: str,
        created_by: str,
        session_name: Optional[str] = None
    ) -> CollaborationSession:
        """Create a new collaboration session."""
        session_id = str(uuid.uuid4())
        
        session = CollaborationSession(
            session_id=session_id,
            mockup_id=mockup_id,
            created_by=created_by,
            created_at=datetime.now(),
            participants={created_by}
        )
        
        self.sessions[session_id] = session
        self.events[session_id] = []
        
        # Track user sessions
        if created_by not in self.user_sessions:
            self.user_sessions[created_by] = set()
        self.user_sessions[created_by].add(session_id)
        
        return session

    async def join_session(self, session_id: str, user_id: str) -> bool:
        """Join an existing collaboration session."""
        if session_id not in self.sessions:
            return False
            
        session = self.sessions[session_id]
        if not session.is_active:
            return False
            
        session.participants.add(user_id)
        
        # Track user sessions
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = set()
        self.user_sessions[user_id].add(session_id)
        
        # Broadcast join event
        await self._broadcast_event(session_id, {
            "type": "user_joined",
            "user_id": user_id,
            "participants": list(session.participants)
        })
        
        return True

    async def leave_session(self, session_id: str, user_id: str) -> bool:
        """Leave a collaboration session."""
        if session_id not in self.sessions:
            return False
            
        session = self.sessions[session_id]
        session.participants.discard(user_id)
        
        # Remove from user sessions
        if user_id in self.user_sessions:
            self.user_sessions[user_id].discard(session_id)
            
        # Broadcast leave event
        await self._broadcast_event(session_id, {
            "type": "user_left",
            "user_id": user_id,
            "participants": list(session.participants)
        })
        
        # Close session if no participants
        if not session.participants:
            session.is_active = False
            
        return True

    async def add_event(
        self,
        session_id: str,
        user_id: str,
        event_type: str,
        data: dict
    ) -> CollaborationEvent:
        """Add a collaboration event and broadcast to participants."""
        if session_id not in self.sessions:
            raise ValueError("Session not found")
            
        event = CollaborationEvent(
            event_id=str(uuid.uuid4()),
            session_id=session_id,
            user_id=user_id,
            event_type=event_type,
            data=data,
            timestamp=datetime.now()
        )
        
        self.events[session_id].append(event)
        
        # Broadcast to all participants except sender
        await self._broadcast_event(session_id, {
            "type": "collaboration_event",
            "event": asdict(event)
        }, exclude_user=user_id)
        
        return event

    async def get_session_state(self, session_id: str) -> dict:
        """Get current state of collaboration session."""
        if session_id not in self.sessions:
            raise ValueError("Session not found")
            
        session = self.sessions[session_id]
        recent_events = self.events[session_id][-50:]  # Last 50 events
        
        return {
            "session": asdict(session),
            "recent_events": [asdict(event) for event in recent_events],
            "active_participants": len(session.participants)
        }

    async def apply_operational_transform(
        self,
        session_id: str,
        operation: dict,
        user_id: str
    ) -> dict:
        """
        Apply operational transformation for conflict resolution.
        Simplified OT for text editing conflicts.
        """
        # This is a simplified OT implementation
        # In production, you'd use a proper OT library like ShareJS
        
        if operation["type"] == "insert":
            # Transform insert operations
            transformed_op = await self._transform_insert(session_id, operation, user_id)
        elif operation["type"] == "delete":
            # Transform delete operations
            transformed_op = await self._transform_delete(session_id, operation, user_id)
        else:
            # Pass through other operations
            transformed_op = operation
            
        # Add as collaboration event
        await self.add_event(session_id, user_id, "operation", transformed_op)
        
        return transformed_op

    async def _transform_insert(self, session_id: str, operation: dict, user_id: str) -> dict:
        """Transform insert operation based on concurrent operations."""
        # Get recent operations from other users
        recent_ops = [
            event for event in self.events[session_id][-10:]
            if event.user_id != user_id and event.event_type == "operation"
        ]
        
        # Adjust position based on concurrent inserts/deletes
        adjusted_position = operation["position"]
        for op_event in recent_ops:
            op_data = op_event.data
            if op_data["type"] == "insert" and op_data["position"] <= operation["position"]:
                adjusted_position += len(op_data["text"])
            elif op_data["type"] == "delete" and op_data["position"] < operation["position"]:
                adjusted_position -= op_data["length"]
                
        return {
            **operation,
            "position": max(0, adjusted_position)
        }

    async def _transform_delete(self, session_id: str, operation: dict, user_id: str) -> dict:
        """Transform delete operation based on concurrent operations."""
        # Similar logic to insert transformation
        recent_ops = [
            event for event in self.events[session_id][-10:]
            if event.user_id != user_id and event.event_type == "operation"
        ]
        
        adjusted_position = operation["position"]
        adjusted_length = operation["length"]
        
        for op_event in recent_ops:
            op_data = op_event.data
            if op_data["type"] == "insert" and op_data["position"] <= operation["position"]:
                adjusted_position += len(op_data["text"])
            elif op_data["type"] == "delete" and op_data["position"] < operation["position"]:
                adjusted_position -= op_data["length"]
                
        return {
            **operation,
            "position": max(0, adjusted_position),
            "length": adjusted_length
        }

    async def register_websocket(self, session_id: str, websocket):
        """Register WebSocket connection for real-time updates."""
        if session_id not in self.websocket_connections:
            self.websocket_connections[session_id] = []
        self.websocket_connections[session_id].append(websocket)

    async def unregister_websocket(self, session_id: str, websocket):
        """Unregister WebSocket connection."""
        if session_id in self.websocket_connections:
            try:
                self.websocket_connections[session_id].remove(websocket)
            except ValueError:
                pass

    async def _broadcast_event(
        self,
        session_id: str,
        event_data: dict,
        exclude_user: Optional[str] = None
    ):
        """Broadcast event to all WebSocket connections in session."""
        if session_id not in self.websocket_connections:
            return
            
        connections = self.websocket_connections[session_id].copy()
        
        for websocket in connections:
            try:
                await websocket.send_text(json.dumps(event_data))
            except Exception:
                # Remove dead connections
                await self.unregister_websocket(session_id, websocket)

    def get_user_sessions(self, user_id: str) -> List[dict]:
        """Get all active sessions for a user."""
        if user_id not in self.user_sessions:
            return []
            
        user_session_ids = self.user_sessions[user_id]
        return [
            asdict(self.sessions[session_id])
            for session_id in user_session_ids
            if session_id in self.sessions and self.sessions[session_id].is_active
        ]

    def get_session_analytics(self, session_id: str) -> dict:
        """Get analytics for a collaboration session."""
        if session_id not in self.sessions:
            return {}
            
        events = self.events[session_id]
        session = self.sessions[session_id]
        
        return {
            "total_events": len(events),
            "participants_count": len(session.participants),
            "duration_minutes": (datetime.now() - session.created_at).total_seconds() / 60,
            "events_by_type": self._count_events_by_type(events),
            "most_active_user": self._get_most_active_user(events)
        }

    def _count_events_by_type(self, events: List[CollaborationEvent]) -> dict:
        """Count events by type."""
        counts = {}
        for event in events:
            counts[event.event_type] = counts.get(event.event_type, 0) + 1
        return counts

    def _get_most_active_user(self, events: List[CollaborationEvent]) -> Optional[str]:
        """Get the most active user in the session."""
        if not events:
            return None
            
        user_counts = {}
        for event in events:
            user_counts[event.user_id] = user_counts.get(event.user_id, 0) + 1
            
        return max(user_counts.items(), key=lambda x: x[1])[0] if user_counts else None