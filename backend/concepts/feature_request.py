"""
FeatureRequestConcept: Collect and manage user feature requests
Purpose: Users suggest features -> System tracks and manages requests
"""

import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict
import json
import aiofiles


class FeatureRequestConcept:
    """
    Manages feature requests from users and partner teams.
    Supports voting, prioritization, and status tracking.
    """

    def __init__(self, storage_dir: str = "feature_requests"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.requests = {}
        self.load_requests()

    def load_requests(self):
        """Load existing feature requests from storage."""
        try:
            requests_file = self.storage_dir / "requests.json"
            if requests_file.exists():
                with open(requests_file, 'r') as f:
                    self.requests = json.load(f)
        except Exception:
            self.requests = {}

    async def save_requests(self):
        """Save feature requests to storage."""
        requests_file = self.storage_dir / "requests.json"
        async with aiofiles.open(requests_file, 'w') as f:
            await f.write(json.dumps(self.requests, indent=2, default=str))

    async def create_request(
        self,
        title: str,
        description: str,
        user_id: str,
        category: str = "enhancement",
        priority: str = "medium",
        partner_team: Optional[str] = None
    ) -> dict:
        """
        Create a new feature request.

        Args:
            title: Short title of the feature
            description: Detailed description
            user_id: ID of requesting user
            category: Type of request (enhancement, bug, integration)
            priority: Priority level (low, medium, high, critical)
            partner_team: Partner team name if cross-team request

        Returns:
            Feature request data with ID
        """
        request_id = str(uuid.uuid4())
        
        request_data = {
            "id": request_id,
            "title": title,
            "description": description,
            "user_id": user_id,
            "category": category,
            "priority": priority,
            "partner_team": partner_team,
            "status": "pending",
            "votes": 0,
            "voters": [],
            "comments": [],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "assigned_to": None,
            "estimated_effort": None,
            "tags": []
        }

        self.requests[request_id] = request_data
        await self.save_requests()
        
        return request_data

    async def vote_request(self, request_id: str, user_id: str) -> dict:
        """Vote for a feature request."""
        if request_id not in self.requests:
            raise ValueError("Feature request not found")

        request = self.requests[request_id]
        
        if user_id in request["voters"]:
            # Remove vote
            request["voters"].remove(user_id)
            request["votes"] -= 1
        else:
            # Add vote
            request["voters"].append(user_id)
            request["votes"] += 1

        request["updated_at"] = datetime.now().isoformat()
        await self.save_requests()
        
        return request

    async def update_status(
        self,
        request_id: str,
        status: str,
        assigned_to: Optional[str] = None
    ) -> dict:
        """Update feature request status."""
        if request_id not in self.requests:
            raise ValueError("Feature request not found")

        request = self.requests[request_id]
        request["status"] = status
        request["updated_at"] = datetime.now().isoformat()
        
        if assigned_to:
            request["assigned_to"] = assigned_to

        await self.save_requests()
        return request

    async def add_comment(
        self,
        request_id: str,
        user_id: str,
        comment: str
    ) -> dict:
        """Add comment to feature request."""
        if request_id not in self.requests:
            raise ValueError("Feature request not found")

        comment_data = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "comment": comment,
            "created_at": datetime.now().isoformat()
        }

        self.requests[request_id]["comments"].append(comment_data)
        self.requests[request_id]["updated_at"] = datetime.now().isoformat()
        
        await self.save_requests()
        return comment_data

    def list_requests(
        self,
        status: Optional[str] = None,
        category: Optional[str] = None,
        partner_team: Optional[str] = None,
        sort_by: str = "votes"
    ) -> List[dict]:
        """List feature requests with filtering and sorting."""
        requests = list(self.requests.values())

        # Apply filters
        if status:
            requests = [r for r in requests if r["status"] == status]
        if category:
            requests = [r for r in requests if r["category"] == category]
        if partner_team:
            requests = [r for r in requests if r["partner_team"] == partner_team]

        # Sort requests
        if sort_by == "votes":
            requests.sort(key=lambda x: x["votes"], reverse=True)
        elif sort_by == "created_at":
            requests.sort(key=lambda x: x["created_at"], reverse=True)
        elif sort_by == "priority":
            priority_order = {"critical": 4, "high": 3, "medium": 2, "low": 1}
            requests.sort(key=lambda x: priority_order.get(x["priority"], 0), reverse=True)

        return requests

    def get_request(self, request_id: str) -> Optional[dict]:
        """Get specific feature request."""
        return self.requests.get(request_id)

    def get_stats(self) -> dict:
        """Get feature request statistics."""
        requests = list(self.requests.values())
        
        stats = {
            "total": len(requests),
            "by_status": {},
            "by_category": {},
            "by_priority": {},
            "top_voted": sorted(requests, key=lambda x: x["votes"], reverse=True)[:5]
        }

        for request in requests:
            # Count by status
            status = request["status"]
            stats["by_status"][status] = stats["by_status"].get(status, 0) + 1
            
            # Count by category
            category = request["category"]
            stats["by_category"][category] = stats["by_category"].get(category, 0) + 1
            
            # Count by priority
            priority = request["priority"]
            stats["by_priority"][priority] = stats["by_priority"].get(priority, 0) + 1

        return stats