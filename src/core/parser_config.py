from dataclasses import dataclass


@dataclass(frozen=True)
class ParserConfig:
    offset: int = 25
    max_swipe_count: int = 9
    max_consecutive_ads: int = 3
    screenshot_similarity_threshold: int = 60

    ad_wait_timeout: float = 5
    action_timeout: float = 0.25
    video_load_timeout: float = 1
    player_hide_timeout: float = 5
    node_spawn_timeout: float = 2.5

    telegram_chat_id: int = None
    telegram_bot_api: str = None

    hidden_ad_duration: float = 0.1
    next_content_swipe_duration: float = 0.5
    half_content_swipe_duration: float = 0.5
    reposition_content_swipe_duration: float = 0.5
