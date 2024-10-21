import asyncio
from TikTokLive import TikTokLiveClient
from TikTokLive.events import CommentEvent, GiftEvent, FollowEvent

async def main():
    # Replace 'your_username_here' with the TikTok username you want to connect to
    username = "migo.238"

    client = TikTokLiveClient(unique_id=username)

    # Callback function for incoming comments
    @client.on(CommentEvent)
    async def on_comment(event: CommentEvent):
        username = event.user.uniqueId
        print(f"Comment from {username}: {event.comment}")
        print(f"Type of username characters: {analyze_username(username)}")

    # Callback function for incoming gifts
    @client.on(GiftEvent)
    async def on_gift(event: GiftEvent):
        username = event.user.uniqueId
        print(f"Gift from {username}: {event.gift.gift_name}")
        print(f"Type of username characters: {analyze_username(username)}")

    # Callback function for incoming follows
    @client.on(FollowEvent)
    async def on_follow(event: FollowEvent):
        username = event.user.uniqueId
        print(f"Follow from {username}")
        print(f"Type of username characters: {analyze_username(username)}")

    # Start the TikTok client
    try:
        await client.start()
    except Exception as e:
        print(f"An error occurred: {e}")


def analyze_username(username):
    # This function will categorize characters in the username and return the details
    char_types = {
        "alphabets": 0,
        "digits": 0,
        "emojis": 0,
        "special_characters": 0
    }

    for char in username:
        if char.isalpha():
            char_types["alphabets"] += 1
        elif char.isdigit():
            char_types["digits"] += 1
        elif ord(char) in range(0x1F600, 0x1F64F):  # Simple check for emojis (not exhaustive)
            char_types["emojis"] += 1
        else:
            char_types["special_characters"] += 1

    return char_types

if __name__ == "__main__":
    asyncio.run(main())
