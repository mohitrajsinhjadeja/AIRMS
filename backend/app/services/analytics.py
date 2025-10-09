import logging
from datetime import datetime, timedelta
from typing import Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import Depends
from app.core.database import get_database

logger = logging.getLogger(__name__)

class AnalyticsService:
    def __init__(self, db: AsyncIOMotorDatabase = Depends(get_database)):
        self.db = db

    async def get_summary(self, time_period: str = "24h") -> Dict[str, Any]:
        """Get analytics summary for the specified time period"""
        try:
            # Calculate time range
            end_time = datetime.utcnow()
            start_time = end_time - self._get_time_delta(time_period)

            # Get base statistics
            total_users = await self.db.users.count_documents({})
            active_users = await self.db.users.count_documents({"is_active": True})

            # Get analytics data
            pipeline = [
                {
                    "$match": {
                        "created_at": {"$gte": start_time, "$lte": end_time}
                    }
                },
                {
                    "$group": {
                        "_id": None,
                        "total_requests": {"$sum": 1},
                        "high_risk_requests": {
                            "$sum": {"$cond": [{"$gte": ["$risk_score", 7.0]}, 1, 0]}
                        },
                        "avg_risk_score": {"$avg": "$risk_score"}
                    }
                }
            ]

            results = await self.db.risk_assessments.aggregate(pipeline).to_list(1)
            stats = results[0] if results else {}

            return {
                "total_users": total_users,
                "active_users": active_users,
                "total_requests": stats.get("total_requests", 0),
                "high_risk_requests": stats.get("high_risk_requests", 0),
                "avg_risk_score": round(stats.get("avg_risk_score", 0), 2),
                "time_period": time_period
            }

        except Exception as e:
            logger.error(f"Failed to get analytics summary: {str(e)}")
            return self._get_empty_summary(time_period)

    def _get_time_delta(self, period: str) -> timedelta:
        """Convert time period string to timedelta"""
        periods = {
            "1h": timedelta(hours=1),
            "24h": timedelta(hours=24),
            "7d": timedelta(days=7),
            "30d": timedelta(days=30)
        }
        return periods.get(period, timedelta(hours=24))

    def _get_empty_summary(self, time_period: str) -> Dict[str, Any]:
        """Return empty analytics summary"""
        return {
            "total_users": 0,
            "active_users": 0,
            "total_requests": 0,
            "high_risk_requests": 0,
            "avg_risk_score": 0.0,
            "time_period": time_period
        }