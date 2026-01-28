"""
Chat tools (MCP-style) for LLM function calling.
Tools are implemented as internal service functions; the chat endpoint
uses these with tool definitions matching OpenAI/Anthropic function format.
All tools are scoped to current_user.
"""

from typing import Any, Dict, List, Optional
from uuid import UUID
from datetime import datetime

from sqlalchemy.orm import Session

from app.models.user import User
from app.models.video import Video
from app.models.post import Post
from app.models.script import Script
from app.models.strategy import Strategy
from app.models.pattern import Pattern
from app.models.social_account import SocialAccount
from app.models.post import PostStatus as PostStatusEnum


# OpenAI-style function definitions for chat LLM
TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "list_scheduled_posts",
            "description": "List all scheduled posts for the user, ordered by scheduled time.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "schedule_post",
            "description": "Schedule a video to be published on one or more platforms at a future time.",
            "parameters": {
                "type": "object",
                "required": ["video_id", "platforms", "scheduled_at"],
                "properties": {
                    "video_id": {"type": "string", "description": "UUID of the video"},
                    "platforms": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Platforms: instagram, tiktok, youtube, facebook",
                    },
                    "scheduled_at": {"type": "string", "description": "ISO 8601 datetime (e.g. 2025-02-01T18:00:00Z)"},
                    "caption": {"type": "string", "description": "Optional caption"},
                    "hashtags": {"type": "array", "items": {"type": "string"}, "description": "Optional hashtags"},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "reschedule_post",
            "description": "Change the scheduled time of an existing scheduled post.",
            "parameters": {
                "type": "object",
                "required": ["post_id", "scheduled_at"],
                "properties": {
                    "post_id": {"type": "string", "description": "UUID of the scheduled post"},
                    "scheduled_at": {"type": "string", "description": "New ISO 8601 datetime"},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "cancel_scheduled_post",
            "description": "Cancel a scheduled post.",
            "parameters": {
                "type": "object",
                "required": ["post_id"],
                "properties": {"post_id": {"type": "string", "description": "UUID of the scheduled post"}},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_scripts",
            "description": "List the user's saved scripts, optionally filtered by platform.",
            "parameters": {
                "type": "object",
                "properties": {
                    "platform": {"type": "string", "description": "Filter by platform"},
                    "limit": {"type": "integer", "description": "Max number to return", "default": 20},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_script",
            "description": "Create a new script from a concept for a platform and duration.",
            "parameters": {
                "type": "object",
                "required": ["concept", "platform", "duration"],
                "properties": {
                    "concept": {"type": "string", "description": "Script concept or topic"},
                    "platform": {"type": "string", "description": "Target platform: instagram, tiktok, youtube, facebook"},
                    "duration": {"type": "integer", "description": "Target duration in seconds"},
                    "target_patterns": {"type": "array", "items": {"type": "string"}, "description": "Optional pattern IDs to align with"},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_script",
            "description": "Get a script by ID.",
            "parameters": {
                "type": "object",
                "required": ["script_id"],
                "properties": {"script_id": {"type": "string", "description": "UUID of the script"}},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_strategies",
            "description": "List the user's marketing strategies.",
            "parameters": {
                "type": "object",
                "properties": {"limit": {"type": "integer", "description": "Max number to return", "default": 20}},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_strategy",
            "description": "Get a strategy by ID.",
            "parameters": {
                "type": "object",
                "required": ["strategy_id"],
                "properties": {"strategy_id": {"type": "string", "description": "UUID of the strategy"}},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_strategy",
            "description": "Generate a marketing strategy based on video IDs, platforms, and optional goals/niche.",
            "parameters": {
                "type": "object",
                "required": ["video_ids", "platforms"],
                "properties": {
                    "video_ids": {"type": "array", "items": {"type": "string"}, "description": "UUIDs of videos to base strategy on"},
                    "platforms": {"type": "array", "items": {"type": "string"}, "description": "Target platforms"},
                    "goals": {"type": "array", "items": {"type": "string"}, "description": "Optional goals e.g. engagement, views"},
                    "niche": {"type": "string", "description": "Optional niche or industry"},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_videos",
            "description": "List the user's uploaded videos.",
            "parameters": {
                "type": "object",
                "properties": {"limit": {"type": "integer", "description": "Max number to return", "default": 20}},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_video",
            "description": "Get a video by ID.",
            "parameters": {
                "type": "object",
                "required": ["video_id"],
                "properties": {"video_id": {"type": "string", "description": "UUID of the video"}},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_patterns_for_video",
            "description": "Get analyzed patterns for a video.",
            "parameters": {
                "type": "object",
                "required": ["video_id"],
                "properties": {"video_id": {"type": "string", "description": "UUID of the video"}},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_connected_platforms",
            "description": "List which social platforms are connected for the user.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_oauth_connect_url",
            "description": "Get the OAuth URL to connect a platform. Returns URL for user to complete connection in browser.",
            "parameters": {
                "type": "object",
                "required": ["platform"],
                "properties": {
                    "platform": {"type": "string", "description": "Platform: instagram, tiktok, youtube, facebook"}
                },
            },
        },
    },
]


def _serialize_datetime(dt: Optional[datetime]) -> Optional[str]:
    if dt is None:
        return None
    return dt.isoformat() + "Z" if dt.tzinfo is None else dt.isoformat()


async def execute_tool(
    tool_name: str,
    arguments: Dict[str, Any],
    db: Session,
    current_user: User,
) -> Dict[str, Any]:
    """
    Execute a tool by name with given arguments. Returns a dict with 'result' (for LLM)
    and optionally 'card_type' and 'card_payload' for the frontend to render a result card.
    Raises ValueError for unknown tool or invalid args; callers should catch and return error to LLM.
    """
    if tool_name == "list_scheduled_posts":
        query = (
            db.query(Post)
            .join(Video)
            .filter(Video.user_id == current_user.id, Post.status == PostStatusEnum.SCHEDULED)
        )
        posts = query.order_by(Post.scheduled_at.asc()).all()
        items = [
            {
                "id": str(p.id),
                "video_id": str(p.video_id),
                "platform": p.platform,
                "scheduled_at": _serialize_datetime(p.scheduled_at),
                "caption": p.caption,
            }
            for p in posts
        ]
        return {"result": {"items": items, "total": len(items)}, "card_type": None}

    if tool_name == "schedule_post":
        video_id = arguments["video_id"]
        platforms = arguments["platforms"]
        scheduled_at_str = arguments["scheduled_at"]
        caption = arguments.get("caption")
        hashtags = arguments.get("hashtags")
        try:
            scheduled_at = datetime.fromisoformat(scheduled_at_str.replace("Z", "+00:00"))
        except Exception:
            scheduled_at = datetime.fromisoformat(scheduled_at_str)
        if scheduled_at.tzinfo:
            scheduled_at = scheduled_at.replace(tzinfo=None)
        video = db.query(Video).filter(Video.id == UUID(video_id), Video.user_id == current_user.id).first()
        if not video:
            return {"result": {"error": "Video not found"}, "card_type": None}
        accounts = db.query(SocialAccount).filter(
            SocialAccount.user_id == current_user.id,
            SocialAccount.platform.in_(platforms),
        ).all()
        if not accounts:
            return {"result": {"error": "No connected accounts for requested platforms"}, "card_type": None}
        if scheduled_at <= datetime.utcnow():
            return {"result": {"error": "Scheduled time must be in the future"}, "card_type": None}
        account_map = {acc.platform: acc for acc in accounts}
        from uuid import uuid4
        created = []
        for platform in platforms:
            if platform not in account_map:
                continue
            post = Post(
                id=uuid4(),
                video_id=video.id,
                social_account_id=account_map[platform].id,
                platform=platform,
                caption=caption,
                hashtags=hashtags,
                status=PostStatusEnum.SCHEDULED,
                scheduled_at=scheduled_at,
            )
            db.add(post)
            created.append({"id": str(post.id), "platform": platform})
        db.commit()
        return {
            "result": {"message": "Posts scheduled", "created": created},
            "card_type": "schedule",
            "card_payload": {"created": created, "scheduled_at": _serialize_datetime(scheduled_at), "video_id": video_id},
        }

    if tool_name == "reschedule_post":
        post_id = arguments["post_id"]
        scheduled_at_str = arguments["scheduled_at"]
        try:
            new_at = datetime.fromisoformat(scheduled_at_str.replace("Z", "+00:00"))
        except Exception:
            new_at = datetime.fromisoformat(scheduled_at_str)
        if new_at.tzinfo:
            new_at = new_at.replace(tzinfo=None)
        post = (
            db.query(Post)
            .join(Video)
            .filter(Post.id == UUID(post_id), Video.user_id == current_user.id, Post.status == PostStatusEnum.SCHEDULED)
            .first()
        )
        if not post:
            return {"result": {"error": "Scheduled post not found"}, "card_type": None}
        post.scheduled_at = new_at
        db.commit()
        return {
            "result": {"message": "Post rescheduled", "post_id": post_id, "scheduled_at": _serialize_datetime(new_at)},
            "card_type": "schedule",
            "card_payload": {"post_id": post_id, "scheduled_at": _serialize_datetime(new_at)},
        }

    if tool_name == "cancel_scheduled_post":
        post_id = arguments["post_id"]
        post = (
            db.query(Post)
            .join(Video)
            .filter(Post.id == UUID(post_id), Video.user_id == current_user.id, Post.status == PostStatusEnum.SCHEDULED)
            .first()
        )
        if not post:
            return {"result": {"error": "Scheduled post not found"}, "card_type": None}
        post.status = PostStatusEnum.CANCELLED
        db.commit()
        return {
            "result": {"message": "Scheduled post cancelled", "post_id": post_id},
            "card_type": "schedule",
            "card_payload": {"cancelled": post_id},
        }

    if tool_name == "list_scripts":
        platform = arguments.get("platform")
        limit = arguments.get("limit", 20)
        query = db.query(Script).filter(Script.user_id == current_user.id)
        if platform:
            query = query.filter(Script.platform == platform)
        scripts = query.order_by(Script.created_at.desc()).limit(limit).all()
        items = [
            {
                "id": str(s.id),
                "concept": s.concept,
                "platform": s.platform,
                "target_duration": s.target_duration,
                "created_at": _serialize_datetime(s.created_at),
            }
            for s in scripts
        ]
        return {"result": {"items": items, "total": len(items)}, "card_type": None}

    if tool_name == "create_script":
        from app.core.config import settings
        from app.services.script_service import ScriptService
        from app.utils.templates import get_cached_response, cache_response
        concept = arguments["concept"]
        platform = arguments["platform"]
        duration = int(arguments.get("duration", 60))
        target_patterns = arguments.get("target_patterns") or []
        patterns = []
        if target_patterns:
            patterns = db.query(Pattern).filter(
                Pattern.id.in_([UUID(pid) for pid in target_patterns])
            ).join(Video).filter(Video.user_id == current_user.id).all()
        cache_params = {"concept": concept, "platform": platform, "duration": duration, "pattern_count": len(patterns)}
        cached = get_cached_response("script", cache_params)
        if cached:
            script_data = cached
        else:
            script_service = ScriptService(openai_api_key=settings.OPENAI_API_KEY)
            pattern_data = [{"type": p.type, "score": p.score, "data": p.data} for p in patterns] if patterns else None
            script_data = await script_service.generate_script(
                concept=concept, platform=platform, duration=duration, patterns=pattern_data
            )
            cache_response("script", cache_params, script_data)
        actual_duration = None
        if script_data.get("segments"):
            actual_duration = max(s.get("end_time", 0) for s in script_data["segments"])
        from uuid import uuid4
        script = Script(
            id=uuid4(),
            user_id=current_user.id,
            concept=concept,
            platform=platform,
            target_duration=duration,
            pattern_ids=[str(p.id) for p in patterns],
            script_data=script_data,
            actual_duration=actual_duration,
            version=1,
        )
        db.add(script)
        db.commit()
        db.refresh(script)
        return {
            "result": {"id": str(script.id), "concept": concept, "platform": platform, "duration": duration},
            "card_type": "script",
            "card_payload": {"id": str(script.id), "concept": concept, "platform": platform, "snippet": str(script_data)[:200]},
        }

    if tool_name == "get_script":
        script_id = arguments["script_id"]
        script = db.query(Script).filter(
            Script.id == UUID(script_id),
            Script.user_id == current_user.id,
        ).first()
        if not script:
            return {"result": {"error": "Script not found"}, "card_type": None}
        return {
            "result": {
                "id": str(script.id),
                "concept": script.concept,
                "platform": script.platform,
                "target_duration": script.target_duration,
                "script_data": script.script_data,
                "created_at": _serialize_datetime(script.created_at),
            },
            "card_type": None,
        }

    if tool_name == "list_strategies":
        limit = arguments.get("limit", 20)
        strategies = db.query(Strategy).filter(Strategy.user_id == current_user.id).order_by(
            Strategy.created_at.desc()
        ).limit(limit).all()
        items = [
            {
                "id": str(s.id),
                "platforms": s.platforms,
                "goals": s.goals,
                "niche": s.niche,
                "created_at": _serialize_datetime(s.created_at),
            }
            for s in strategies
        ]
        return {"result": {"items": items, "total": len(items)}, "card_type": None}

    if tool_name == "get_strategy":
        strategy_id = arguments["strategy_id"]
        strategy = db.query(Strategy).filter(
            Strategy.id == UUID(strategy_id),
            Strategy.user_id == current_user.id,
        ).first()
        if not strategy:
            return {"result": {"error": "Strategy not found"}, "card_type": None}
        return {
            "result": {
                "id": str(strategy.id),
                "platforms": strategy.platforms,
                "goals": strategy.goals,
                "niche": strategy.niche,
                "strategy_data": strategy.strategy_data,
                "created_at": _serialize_datetime(strategy.created_at),
            },
            "card_type": None,
        }

    if tool_name == "create_strategy":
        from app.core.config import settings
        from app.services.strategy_service import StrategyService
        from app.utils.templates import get_cached_response, cache_response
        from uuid import uuid4
        video_ids = arguments["video_ids"]
        platforms = arguments["platforms"]
        goals = arguments.get("goals")
        niche = arguments.get("niche")
        videos = db.query(Video).filter(
            Video.id.in_([UUID(vid) for vid in video_ids]),
            Video.user_id == current_user.id,
        ).all()
        if len(videos) != len(video_ids):
            return {"result": {"error": "One or more videos not found"}, "card_type": None}
        patterns = db.query(Pattern).filter(
            Pattern.video_id.in_([UUID(vid) for vid in video_ids])
        ).all()
        cache_params = {"platforms": sorted(platforms), "goals": sorted(goals or []), "niche": niche, "pattern_count": len(patterns)}
        cached = get_cached_response("strategy", cache_params)
        if cached:
            strategy_data = cached
        else:
            strategy_service = StrategyService(openai_api_key=settings.OPENAI_API_KEY)
            pattern_data = [{"type": p.type, "score": p.score, "data": p.data} for p in patterns]
            strategy_data = await strategy_service.generate_strategy(
                patterns=pattern_data, platforms=platforms, goals=goals, niche=niche
            )
            cache_response("strategy", cache_params, strategy_data)
        strategy = Strategy(
            id=uuid4(),
            user_id=current_user.id,
            video_ids=video_ids,
            platforms=platforms,
            goals=goals,
            niche=niche,
            strategy_data=strategy_data,
            version=1,
        )
        db.add(strategy)
        db.commit()
        db.refresh(strategy)
        return {
            "result": {"id": str(strategy.id), "platforms": platforms, "created_at": _serialize_datetime(strategy.created_at)},
            "card_type": "strategy",
            "card_payload": {"id": str(strategy.id), "platforms": platforms},
        }

    if tool_name == "list_videos":
        limit = arguments.get("limit", 20)
        videos = db.query(Video).filter(Video.user_id == current_user.id).order_by(
            Video.created_at.desc()
        ).limit(limit).all()
        items = [
            {"id": str(v.id), "filename": v.filename, "status": v.status.value, "created_at": _serialize_datetime(v.created_at)}
            for v in videos
        ]
        return {"result": {"items": items, "total": len(items)}, "card_type": None}

    if tool_name == "get_video":
        video_id = arguments["video_id"]
        video = db.query(Video).filter(Video.id == UUID(video_id), Video.user_id == current_user.id).first()
        if not video:
            return {"result": {"error": "Video not found"}, "card_type": None}
        return {
            "result": {
                "id": str(video.id),
                "filename": video.filename,
                "status": video.status.value,
                "duration": video.duration,
                "created_at": _serialize_datetime(video.created_at),
            },
            "card_type": None,
        }

    if tool_name == "get_patterns_for_video":
        video_id = arguments["video_id"]
        video = db.query(Video).filter(Video.id == UUID(video_id), Video.user_id == current_user.id).first()
        if not video:
            return {"result": {"error": "Video not found"}, "card_type": None}
        patterns = db.query(Pattern).filter(Pattern.video_id == UUID(video_id)).order_by(Pattern.score.desc()).all()
        items = [
            {"id": str(p.id), "type": p.type, "score": p.score, "description": p.description}
            for p in patterns
        ]
        return {"result": {"items": items, "total": len(items)}, "card_type": None}

    if tool_name == "list_connected_platforms":
        accounts = db.query(SocialAccount).filter(SocialAccount.user_id == current_user.id).all()
        items = [{"platform": acc.platform, "username": acc.username} for acc in accounts]
        return {"result": {"accounts": items, "connected": [a.platform for a in accounts]}, "card_type": None}

    if tool_name == "get_oauth_connect_url":
        platform = arguments["platform"]
        supported = ["instagram", "tiktok", "youtube", "facebook"]
        if platform not in supported:
            return {"result": {"error": f"Unsupported platform. Use one of: {', '.join(supported)}"}, "card_type": None}
        # OAuth not implemented yet; return placeholder URL
        base = "https://app.elevoai.com"  # or from settings
        url = f"{base}/account/connected-platforms?connect={platform}"
        return {
            "result": {"url": url, "message": "Complete connection in Account > Connected Platforms.", "platform": platform},
            "card_type": "oauth",
            "card_payload": {"platform": platform, "url": url},
        }

    raise ValueError(f"Unknown tool: {tool_name}")
