"""
Simple test for analytics endpoint
"""
import asyncio
from models import LearningAnalytics

async def create_safe_analytics(student_id: str, period: str = "week"):
    """Create safe fallback analytics"""
    return LearningAnalytics(
        student_id=student_id,
        time_period=period,
        total_sessions=1,
        total_time_minutes=30,
        concepts_mastered=2,
        accuracy_metrics={"math": 0.8, "reading": 0.75},
        engagement_metrics={"average_engagement": 0.7, "session_consistency": 0.5},
        difficulty_progression=["easy", "medium"],
        learning_velocity="steady",
        prediction_models={
            "expected_improvement": 0.15,
            "mastery_timeline": "3-4 weeks",
            "risk_factors": []
        }
    )

if __name__ == "__main__":
    result = asyncio.run(create_safe_analytics("demo-student"))
    print(f"Analytics created: {result.student_id}, sessions: {result.total_sessions}")