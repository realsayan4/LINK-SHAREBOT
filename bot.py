import asyncio
import sys
from datetime import datetime
from pyrogram import Client
from pyrogram.enums import ParseMode
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from config import *
from plugins import web_server
import pyrogram.utils
from aiohttp import web

pyrogram.utils.MIN_CHANNEL_ID = -1002449417637

name = """
Link share bot started ✨ Credit:- @Realsayan
"""

class Bot(Client):
    def __init__(self):
        super().__init__(
            name="Bot",
            api_hash=API_HASH,
            api_id=APP_ID,
            plugins={"root": "plugins"},
            workers=TG_BOT_WORKERS,
            bot_token=TG_BOT_TOKEN,
        )
        self.LOGGER = LOGGER

    async def start(self, *args, **kwargs):
        await super().start()
        usr_bot_me = await self.get_me()
        self.uptime = datetime.now()
        
        # IMPORTANT: Pre-resolve all channels to populate session cache
        # This prevents PeerIdInvalid errors when bot is deployed on new server
        try:
            from database.database import Seishiro
            
            self.LOGGER(__name__).info("=" * 60)
            self.LOGGER(__name__).info("STARTING CHANNEL PEER RESOLUTION...")
            self.LOGGER(__name__).info("=" * 60)
            
            # Get all channels from database
            channels = await Seishiro.get_channels()
            
            if channels:
                self.LOGGER(__name__).info(f"Found {len(channels)} channel(s) in database")
                self.LOGGER(__name__).info("Resolving peers to populate session cache...")
                
                resolved_count = 0
                failed_count = 0
                
                for channel_id in channels:
                    try:
                        # This get_chat() call does 2 things:
                        # 1. Validates that the channel exists and bot has access
                        # 2. Stores peer data in Pyrogram's session file
                        chat = await self.get_chat(channel_id)
                        resolved_count += 1
                        self.LOGGER(__name__).info(
                            f"✓ [{resolved_count}/{len(channels)}] Resolved: {channel_id} ({chat.title})"
                        )
                    except Exception as e:
                        failed_count += 1
                        self.LOGGER(__name__).warning(
                            f"✗ [{resolved_count + failed_count}/{len(channels)}] Failed: {channel_id} - {e}"
                        )
                
                self.LOGGER(__name__).info("=" * 60)
                self.LOGGER(__name__).info(
                    f"PEER RESOLUTION COMPLETE: {resolved_count} success, {failed_count} failed"
                )
                self.LOGGER(__name__).info("=" * 60)
            else:
                self.LOGGER(__name__).info("No channels found in database. Skipping peer resolution.")
                
        except Exception as e:
            self.LOGGER(__name__).error(f"Error during channel pre-resolution: {e}")
            self.LOGGER(__name__).warning("Bot will continue, but may encounter PeerIdInvalid errors")
        
        # Notify bot restart
        try:
            await self.send_photo(
                chat_id=DATABASE_CHANNEL,
                photo="https://ibb.co/DH3N4Lyr",
                caption=("**I ʀᴇsᴛᴀʀᴛᴇᴅ ᴀɢᴀɪɴ !**"),
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("ᴜᴘᴅᴀᴛᴇs", url="https://t.me/CantarellaBots")]]
                )
            )
        except Exception as e:
            self.LOGGER(__name__).warning(f"Failed to send bot start message in {DATABASE_CHANNEL}: {e}")
        
        self.set_parse_mode(ParseMode.HTML)
        self.LOGGER(__name__).info("Wew...Bot is running...⚡  Credit:- @CantarellaBots")
        self.LOGGER(__name__).info(f"{name}")
        self.username = usr_bot_me.username
        
        # Web-response
        try:
            app = web.AppRunner(await web_server())
            await app.setup()
            bind_address = "0.0.0.0"
            await web.TCPSite(app, bind_address, PORT).start()
            self.LOGGER(__name__).info(f"Web server started on {bind_address}:{PORT}")
        except Exception as e:
            self.LOGGER(__name__).error(f"Failed to start web server: {e}")

    async def stop(self, *args):
        await super().stop()
        self.LOGGER(__name__).info("Bot stopped...")
        

if __name__ == "__main__":
    Bot().run()
