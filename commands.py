# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

import os
import logging
import random
import asyncio
from Script import script
from validators import domain
from clone_plugins.dbusers import clonedb
from clone_plugins.users_api import get_user, update_user_info
from pyrogram import Client, filters, enums
from plugins.clone import mongo_db
from pyrogram.errors import ChatAdminRequired, FloodWait
from config import (
    BOT_USERNAME, ADMINS, PICS,
    CUSTOM_FILE_CAPTION, AUTO_DELETE_TIME, AUTO_DELETE
)
from pyrogram.types import (
    InlineKeyboardButton, InlineKeyboardMarkup,
    Message, CallbackQuery, InputMediaPhoto
)
import base64

logger = logging.getLogger(__name__)

def get_size(size):
    # Returns the size in a human-readable format
    units = ["Bytes", "KB", "MB", "GB", "TB", "PB", "EB"]
    size = float(size)
    i = 0
    while size >= 1024 and i < len(units) - 1:
        size /= 1024
        i += 1
    return "%.2f %s" % (size, units[i])


@Client.on_message(filters.command("start") & filters.incoming)
async def start(client, message: Message):
    me = await client.get_me()
    if not await clonedb.is_user_exist(me.id, message.from_user.id):
        await clonedb.add_user(me.id, message.from_user.id)

    # No deep-link parameter, show start panel
    if len(message.command) != 2:
        buttons = [
            [InlineKeyboardButton('💝 sᴜʙsᴄʀɪʙᴇ ᴍʏ ʏᴏᴜᴛᴜʙᴇ ᴄʜᴀɴɴᴇʟ', url='https://youtube.com/@Tech_VJ')],
            [InlineKeyboardButton('🤖 ᴄʀᴇᴀᴛᴇ ʏᴏᴜʀ ᴏᴡɴ ᴄʟᴏɴᴇ ʙᴏᴛ', url=f'https://t.me/{BOT_USERNAME}?start=clone')],
            [InlineKeyboardButton('💁‍♀️ ʜᴇʟᴘ', callback_data='help'), InlineKeyboardButton('ᴀʙᴏᴜᴛ 🔻', callback_data='about')]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.reply_photo(
            photo=random.choice(PICS),
            caption=script.CLONE_START_TXT.format(message.from_user.mention, me.mention),
            reply_markup=reply_markup
        )
        return

    # Deep-link file send logic
    data_b64 = message.command[1]
    try:
        # Adjust for missing padding in urlsafe_b64decode
        padded_b64 = data_b64 + "=" * (-len(data_b64) % 4)
        decoded = base64.urlsafe_b64decode(padded_b64).decode("ascii")
        pre, file_id = decoded.split("_", 1)
    except Exception as e:
        logger.error("START: Invalid deep-link parameter: %s", e)
        await message.reply("Invalid parameter.")
        return

    try:
        msg = await client.send_cached_media(
            chat_id=message.from_user.id,
            file_id=file_id,
            protect_content=True if pre == 'filep' else False,
        )
        filetype = msg.media
        file = getattr(msg, filetype.value)
        file_name = getattr(file, "file_name", "File")
        # Sanitize file name if needed
        title = '@VJ_Botz ' + ' '.join([x for x in file_name.split() if not x.startswith('[') and not x.startswith('@')])
        size = get_size(file.file_size)
        f_caption = f"<code>{title}</code>"
        if CUSTOM_FILE_CAPTION:
            try:
                f_caption = CUSTOM_FILE_CAPTION.format(
                    file_name=title or '',
                    file_size=size or '',
                    file_caption=''
                )
            except Exception as e:
                logger.warning("Error formatting custom caption: %s", e)
        await msg.edit_caption(f_caption)
        k = await msg.reply(f"<b><u>❗️❗️❗️IMPORTANT❗️️❗️❗️</u></b>\n\n"
                            f"This Movie File/Video will be deleted in <b><u>{AUTO_DELETE} mins</u> 🫥 <i></b>(Due to Copyright Issues)</i>.\n\n"
                            "<b><i>Please forward this File/Video to your Saved Messages and Start Download there</i></b>",
                            quote=True)
        await asyncio.sleep(AUTO_DELETE_TIME)
        await msg.delete()
        await k.edit_text("<b>Your File/Video is successfully deleted!!!</b>")
    except Exception as e:
        logger.error("SEND FILE in start: %s", e)
        await message.reply("Unable to send your file. Please try again later.")


@Client.on_message(filters.command('api') & filters.private)
async def shortener_api_handler(client, m: Message):
    user_id = m.from_user.id
    user = await get_user(user_id)
    cmd = m.command

    if len(cmd) == 1:
        s = script.SHORTENER_API_MESSAGE.format(base_site=user.get("base_site","None"), shortener_api=user.get("shortener_api","None"))
        return await m.reply(s)
    elif len(cmd) == 2:    
        api = cmd[1].strip()
        await update_user_info(user_id, {"shortener_api": api})
        await m.reply("Shortener API updated successfully to " + api)
    else:
        await m.reply("Wrong usage. Use: /api YOUR_API_KEY")


@Client.on_message(filters.command("base_site") & filters.private)
async def base_site_handler(client, m: Message):
    user_id = m.from_user.id
    user = await get_user(user_id)
    cmd = m.command
    text = ("/base_site (base_site)\n\nCurrent base site: {bsite}\n\n"
            "EX: /base_site shortnerdomain.com\n\n"
            "If You Want To Remove Base Site Then Copy This And Send To Bot - `/base_site None`"
            ).format(bsite=user.get("base_site", "None"))

    if len(cmd) == 1:
        return await m.reply(text=text, disable_web_page_preview=True)
    elif len(cmd) == 2:
        base_site = cmd[1].strip()
        # Allow removal
        if base_site.lower() == "none":
            await update_user_info(user_id, {"base_site": None})
            return await m.reply("Base Site removed successfully.")
        if not domain(base_site):
            return await m.reply("Invalid domain.\n"+text, disable_web_page_preview=True)
        await update_user_info(user_id, {"base_site": base_site})
        await m.reply("Base Site updated successfully")
    else:
        await m.reply("Wrong usage. Use: /base_site yourdomain.com")


@Client.on_callback_query()
async def cb_handler(client: Client, query: CallbackQuery):
    me = await client.get_me()
    data = query.data

    if data == "close_data":
        await query.message.delete()
        return

    elif data == "start":
        buttons = [
            [InlineKeyboardButton('💝 sᴜʙsᴄʀɪʙᴇ ᴍʏ ʏᴏᴜᴛᴜʙᴇ ᴄʜᴀɴɴᴇʟ', url='https://youtube.com/@Tech_VJ')],
            [InlineKeyboardButton('🤖 ᴄʀᴇᴀᴛᴇ ʏᴏᴜʀ ᴏᴡɴ ᴄʟᴏɴᴇ ʙᴏᴛ', url=f'https://t.me/{BOT_USERNAME}?start=clone')],
            [InlineKeyboardButton('💁‍♀️ ʜᴇʟᴘ', callback_data='help'), InlineKeyboardButton('ᴀʙᴏᴜᴛ 🔻', callback_data='about')]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        try:
            await client.edit_message_media(
                query.message.chat.id, 
                query.message.id, 
                InputMediaPhoto(random.choice(PICS))
            )
        except Exception:
            # In some cases, editing media might fail if it's not a media message; ignore
            pass
        await query.message.edit_text(
            text=script.CLONE_START_TXT.format(query.from_user.mention, me.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )

    elif data == "help":
        buttons = [
            [InlineKeyboardButton('Hᴏᴍᴇ', callback_data='start'), InlineKeyboardButton('🔒 Cʟᴏsᴇ', callback_data='close_data')]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        try:
            await client.edit_message_media(
                query.message.chat.id,
                query.message.id,
                InputMediaPhoto(random.choice(PICS))
            )
        except Exception:
            pass
        await query.message.edit_text(
            text=script.CHELP_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )  

    elif data == "about":
        buttons = [
            [InlineKeyboardButton('Hᴏᴍᴇ', callback_data='start'), InlineKeyboardButton('🔒 Cʟᴏsᴇ', callback_data='close_data')]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        try:
            await client.edit_message_media(
                query.message.chat.id, 
                query.message.id, 
                InputMediaPhoto(random.choice(PICS))
            )
        except Exception:
            pass
        owner = mongo_db.bots.find_one({'bot_id': me.id})
        ownerid = int(owner['user_id']) if owner and 'user_id' in owner else 0
        await query.message.edit_text(
            text=script.CABOUT_TXT.format(me.mention, ownerid),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )

# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01
