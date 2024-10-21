# TikTok Client Script: tiktok_client.py
import asyncio
from TikTokLive import TikTokLiveClient
from TikTokLive.events import CommentEvent, GiftEvent, LikeEvent, FollowEvent
from asyncio import Queue

class TikTokClient:
    def __init__(self, username):
        # Create TikTokLiveClient instance
        self.client = TikTokLiveClient(unique_id=username)
        self.comment_queue = Queue()
        self.gift_queue = Queue()
        self.like_queue = Queue()
        self.follow_queue = Queue()

        # Register event handlers using decorators
        @self.client.on(CommentEvent)
        async def on_comment(event: CommentEvent):
            print(f"Received Comment: {event.user.unique_id} says {event.comment}")  # Debug Log
            await self.comment_queue.put({
                'type': 'comment',
                'user': event.user.unique_id,
                'content': event.comment
            })

        @self.client.on(GiftEvent)
        async def on_gift(event: GiftEvent):
            print(f"Received Gift: {event.user.unique_id} sent {event.gift.name} x {event.gift.repeat_count}")  # Debug Log
            await self.gift_queue.put({
                'type': 'gift',
                'user': event.user.unique_id,
                'gift_name': event.gift.name,
                'repeat_count': event.gift.repeat_count,
                'value': event.gift.diamond_count  # Added gift value for classification
            })

        @self.client.on(LikeEvent)
        async def on_like(event: LikeEvent):
            print(f"Received Like: {event.user.unique_id} liked {event.like_count} times")  # Debug Log
            await self.like_queue.put({
                'type': 'like',
                'user': event.user.unique_id,
                'like_count': event.like_count
            })

        @self.client.on(FollowEvent)
        async def on_follow(event: FollowEvent):
            print(f"Received Follow: {event.user.unique_id} followed the stream")  # Debug Log
            await self.follow_queue.put({
                'type': 'follow',
                'user': event.user.unique_id
            })

    async def start(self):
        try:
            await self.client.start()
        except Exception as e:
            print(f"Error starting TikTok client: {e}")


    