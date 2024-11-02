from telethon.tl.types import InputMediaPhoto, InputMediaDocument

class StoryManager:
    @staticmethod
    async def prepare_caption(client, caption=None, mentions=None, link=None):
        text = caption or ""
        
        if mentions:
            for username in mentions:
                entity = await client.get_entity(username)
                text += f"[{entity.first_name}](tg://user?id={entity.id}) "
        
        if link:
            text += f"\n{link}"
            
        return text
    
    @staticmethod
    async def prepare_media(client, media_path):
        if media_path.lower().endswith(('.jpg', '.jpeg', '.png')):
            return InputMediaPhoto(await client.upload_file(media_path))
        return InputMediaDocument(await client.upload_file(media_path))
    
    @staticmethod
    async def post_story(client, media_path, caption=None, mentions=None, link=None):
        text = await StoryManager.prepare_caption(client, caption, mentions, link)
        media = await StoryManager.prepare_media(client, media_path)
        
        return await client.send_file(
            'me',
            media,
            caption=text,
            parse_mode='md'
        )