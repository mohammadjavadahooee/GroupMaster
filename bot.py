from rubpy import Client, filters
from rubpy.types import Updates
import jdatetime
from datetime import datetime

bot = Client("bot")

links = ["http", "www.", ".ir", ".com", "rubika.ir/", "t.me/", "@"]
user_warnings = {}
group_cache = {}
user_cache = {}
cache_message_id = {}
silent = {}
max_warnings = 3
voice_chat_id = None
settings = {
        "anti_link": True,
        "anti_video" : False,
        "anti_voice" : False,
        "anti_photo" : False,
        "anti_forward" : False,
        "anti_music" : False,
        "anti_file" : False,
        "anti_contact" : False,
        "anti_location" : False,
        "anti_poll" : False,
        "anti_gif" : False,
        "anti_sticker" : False,
        "warning_mode":True
    }

def is_link(text):
    return any(x in text for x in links)

async def delet_and_warning(grop_guid,warning,id_message,user_guid):
    
    user_info = await bot.get_user_info(user_guid)
    user_name = user_info.user.first_name
    
    try:
        await bot.delete_messages(grop_guid,id_message)
        if settings['warning_mode']:
            await bot.send_message(grop_guid, warning)
            if user_guid not in user_warnings:
                user_warnings[user_guid] = 1
            else:
                user_warnings[user_guid] += 1
        if user_warnings[user_guid] >= max_warnings:
            await bot.ban_member(grop_guid, user_guid)
            await bot.send_message(grop_guid,f"کاربر {user_name} به علت نقض قوانین گروه بن شد🚫")
            user_warnings[user_guid] = 1
            
    except:
        await bot.send_message(grop_guid, "خطا در حذف محتوای قفل شده لطفا ربات را ادمین کنید")


async def toggle_feature(group_guid, id_message, feature, text):
    if text.split()[1]== "قفل":
        settings[feature] = True
    elif text.split()[1] == "باز":
        settings[feature] = False
    status = "روشن" if settings[feature] else "خاموش"
    await bot.send_message(group_guid, f"قفل {text[0:-4]} {status} شد", id_message)

async def info_user_replay(update:Updates):
    pass

@bot.on_message_updates(filters.is_group)
async def zedlink(update:Updates):
    global max_warnings

    text = update.text or ""

    group_guid = update.object_guid
    if group_guid not in silent:
        silent[group_guid] = []
    if group_guid in group_cache:
        info_group = group_cache[group_guid]
    else:
        info_group = await bot.get_group_info(group_guid)
        group_cache[group_guid] = info_group  
        
    id_message = update.message_id
    
    if group_guid not in cache_message_id:
        cache_message_id[group_guid] = [id_message]
    cache_message_id[group_guid].append(id_message)
    lismsg = cache_message_id[group_guid]

    name_group = info_group.group.group_title
    count_members = info_group.group.count_members
    slow_mode = info_group.group.slow_mode
    chat_history = info_group.group.chat_history_for_new_members
    link_group = await bot.get_group_link(group_guid)
    bio_group = info_group.group.description

    
    user_guid = update.author_guid
    if user_guid in user_cache:
        user_info = user_cache[user_guid]
    else:
        user_info = await bot.get_user_info(user_guid)
        user_cache[user_guid] = user_info
    user_warning = user_warnings.get(user_guid,0)
    user_name = user_info.user.first_name
    user_id = user_info.user.username


    is_admin = await update.is_admin(group_guid,user_guid)
    creator_guid = None
    admins_info = await bot.get_group_admin_members(group_guid)
    if not creator_guid:
        admins = admins_info["in_chat_members"]
        for admin in admins:
            if admin["join_type"] == "Creator":
                creator_guid = admin["member_guid"]
                creator_name = admin["first_name"]
                creator_id = f"{admin["username"]}"
                break
      
    if update.reply_message_id:
        msg_user = await update.get_messages(group_guid, [update.reply_message_id])
        user_replay_guid = msg_user["messages"][0]["author_object_guid"]
        user_replay_info = await bot.get_user_info(user_replay_guid)
        user_reply_name = user_replay_info.user.first_name
        user_reply_id = user_replay_info.user.username
        user_reply_bio = user_replay_info.user.bio or "ندارد"
        is_admin_replay = await update.is_admin(group_guid,user_replay_guid)
    
    if is_link(text) and settings['anti_link'] and not is_admin:
        warning_message = f"🚫 **کاربر** ﹝[{user_name}](https://rubika.ir/{user_id})﹞ **ارسال لینک در این گروه ممنوع است!**\n🔴 **اخطار** {user_warning}/{str(max_warnings)}"
        await delet_and_warning(group_guid, warning_message, id_message, user_guid)

    elif update.video and settings['anti_video'] and not is_admin:
        warning_message = f"🚫 **کاربر** ﹝[{user_name}](https://rubika.ir/{user_id})﹞ **ارسال ویدیو در این گروه ممنوع است!**\n🔴 **اخطار** {user_warning}/{str(max_warnings)}"
        await delet_and_warning(group_guid, warning_message, id_message, user_guid)

    elif update.voice and settings['anti_voice'] and not is_admin:
        warning_message = f"🚫 **کاربر** ﹝[{user_name}](https://rubika.ir/{user_id})﹞ **ارسال ویس در این گروه ممنوع است!**\n🔴 **اخطار** {user_warning}/{str(max_warnings)}"
        await delet_and_warning(group_guid, warning_message, id_message, user_guid)

    elif update.photo and settings['anti_photo'] and not is_admin:
        warning_message = f"🚫 **کاربر** ﹝[{user_name}](https://rubika.ir/{user_id})﹞ **ارسال عکس در این گروه ممنوع است!**\n🔴 **اخطار** {user_warning}/{str(max_warnings)}"
        await delet_and_warning(group_guid, warning_message, id_message, user_guid)

    elif update.is_forward and settings['anti_forward'] and not is_admin:
        warning_message = f"🚫 **کاربر** ﹝[{user_name}](https://rubika.ir/{user_id})﹞ ** فوروارد در این گروه ممنوع است!**\n🔴 **اخطار** {user_warning}/{str(max_warnings)}"
        await delet_and_warning(group_guid, warning_message, id_message, user_guid)

    elif update.music and settings['anti_music'] and not is_admin:
        warning_message = f"🚫 **کاربر** ﹝[{user_name}](https://rubika.ir/{user_id})﹞ **ارسال موسیقی در این گروه ممنوع است!**\n🔴 **اخطار** {user_warning}/{str(max_warnings)}"
        await delet_and_warning(group_guid, warning_message, id_message, user_guid)

    elif update.file and settings['anti_file'] and not is_admin:
        warning_message = f"🚫 **کاربر** ﹝[{user_name}](https://rubika.ir/{user_id})﹞ **ارسال فایل در این گروه ممنوع است!**\n🔴 **اخطار** {user_warning}/{str(max_warnings)}"
        await delet_and_warning(group_guid, warning_message, id_message, user_guid)

    elif update.contact and settings['anti_contact'] and not is_admin:
        warning_message = f"🚫 **کاربر** ﹝[{user_name}](https://rubika.ir/{user_id})﹞ **ارسال مخاطب در این گروه ممنوع است!**\n🔴 **اخطار** {user_warning}/{str(max_warnings)}"
        await delet_and_warning(group_guid, warning_message, id_message, user_guid)

    elif update.poll and settings['anti_poll'] and not is_admin:
        warning_message = f"🚫 **کاربر** ﹝[{user_name}](https://rubika.ir/{user_id})﹞ **ارسال نظرسنجی در این گروه ممنوع است!**\n🔴 **اخطار** {user_warning}/{str(max_warnings)}"
        await delet_and_warning(group_guid, warning_message, id_message, user_guid)

    elif update.gif and settings['anti_gif'] and not is_admin:
        warning_message = f"🚫 **کاربر** ﹝[{user_name}](https://rubika.ir/{user_id})﹞ **ارسال گیف در این گروه ممنوع است!**\n🔴 **اخطار** {user_warning}/{str(max_warnings)}"
        await delet_and_warning(group_guid, warning_message, id_message, user_guid)

    elif update.sticker and settings['anti_sticker'] and not is_admin:
        warning_message = f"🚫 **کاربر** ﹝[{user_name}](https://rubika.ir/{user_id})﹞ **ارسال استیکر در این گروه ممنوع است!**\n🔴 **اخطار** {user_warning}/{str(max_warnings)}"
        await delet_and_warning(group_guid, warning_message, id_message, user_guid)
        
    elif user_guid in silent[group_guid]:
        await bot.delete_messages(group_guid,id_message,'Global')

    command_map = {
        "لینک قفل": "anti_link",
        "لینک باز": "anti_link",
        "ویدیو قفل": "anti_video",
        "ویدیو باز": "anti_video",
        "ویس قفل": "anti_voice",
        "ویس باز": "anti_voice",
        "عکس قفل": "anti_photo",
        "عکس باز": "anti_photo",
        "فوروارد قفل": "anti_forward",
        "فوروارد باز": "anti_forward",
        "موسیقی قفل": "anti_music",
        "موسیقی باز": "anti_music",
        "فایل قفل": "anti_file",
        "فایل باز": "anti_file",
        "مخاطب قفل": "anti_contact",
        "مخاطب باز": "anti_contact",
        "نظرسنجی قفل": "anti_poll",
        "نظرسنجی باز": "anti_poll",
        "گیف قفل": "anti_gif",
        "گیف باز": "anti_gif",
        "استیکر قفل": "anti_sticker",
        "استیکر باز": "anti_sticker",
        "هشدار قفل" : "warning_mode",
        "هشدار باز" : "warning_mode"
    }


    if text in command_map and is_admin:
        await toggle_feature(group_guid, id_message, command_map[text], text)

    elif text == "قفل ها" and is_admin:
        
        status_text = "📊 وضعیت گروه:\n\n"
        
        status_text += f"🔗 قفل لینک: {'✅ روشن' if settings['anti_link'] else '❌ خاموش'}\n"
        status_text += f"🎞 قفل ویدیو: {'✅ روشن' if settings['anti_video'] else '❌ خاموش'}\n"
        status_text += f"🎙️ قفل ویس: {'✅ روشن' if settings['anti_voice'] else '❌ خاموش'}\n"
        status_text += f"🖼 قفل عکس: {'✅ روشن' if settings['anti_photo'] else '❌ خاموش'}\n"
        status_text += f"⏩ قفل فوروارد: {'✅ روشن' if settings['anti_forward'] else '❌ خاموش'}\n"
        status_text += f"🎵 قفل موسیقی: {'✅ روشن' if settings['anti_music'] else '❌ خاموش'}\n"
        status_text += f"📁 قفل فایل: {'✅ روشن' if settings['anti_file'] else '❌ خاموش'}\n"
        status_text += f"📱 قفل مخاطب: {'✅ روشن' if settings['anti_contact'] else '❌ خاموش'}\n"
        status_text += f"🌍 قفل لوکیشن: {'✅ روشن' if settings['anti_location'] else '❌ خاموش'}\n"
        status_text += f"📊 قفل نظرسنجی: {'✅ روشن' if settings['anti_poll'] else '❌ خاموش'}\n"
        status_text += f"🎬 قفل گیف: {'✅ روشن' if settings['anti_gif'] else '❌ خاموش'}\n"
        status_text += f"📑 قفل استیکر: {'✅ روشن' if settings['anti_sticker'] else '❌ خاموش'}\n"
        status_text += f"⚠️ قفل هشدار: {'✅ روشن' if settings['warning_mode'] else '❌ خاموش'}\n"
        
        await bot.send_message(group_guid, status_text, id_message)
    
    elif text.startswith("اخطار") and is_admin:
        try:
            max_warnings = int(text.split()[1])
            await bot.send_message(group_guid,f"تعداد اخطار ها به {max_warnings} تغییر پیدا کرد💢")
        except ValueError:
            await bot.send_message(group_guid, "لطفاً یک عدد معتبر برای حداکثر تعداد اخطار وارد کنید.")

    elif text == "اینفو گروه" and is_admin:

        text_info_group = f"""**
🔹 نام گروه : {name_group}\n
Ⓜ️ تعداد پیام ها از زمان فعالیت ربات : {len(cache_message_id[group_guid])}\n
🔸 تعداد اعضا : {count_members}\n
🕒 حالت کندی : {slow_mode}\n
💬 تاریخچه گفتگوها : {"قابل مشاهده" if chat_history == "Visible" else "پنهان"}\n
💡 بیو گروه : {bio_group}\n
⚙️ گوید گروه : {group_guid}\n
🗽 مالک گروه : **\n[{creator_name}](https://rubika.ir/{creator_id})\n**
🔗 لینک گروه : **{link_group["join_link"]}"""

        await bot.send_message(group_guid, text_info_group, id_message)

    elif text == "اد کامل" and user_guid == creator_guid:
        if update.reply_message_id:
            access_list = ["ChangeInfo", "DeleteGlobalAllMessages","BanMember","SetJoinLink","PinMessages","SetAdmin","SetMemberAccess"]
            await bot.set_group_admin(group_guid, user_replay_guid, "SetAdmin", access_list=access_list)
            await bot.send_message(group_guid, f"**کاربر** ﹝[{user_reply_name}](https://rubika.ir/{user_reply_id})﹞ **ادمین کامل شد🗽**",id_message)
        else:
            await bot.send_message(group_guid, "لطفاً این دستور را روی پیام فرد مورد نظر ریپلای کنید.",id_message)

    elif text == "اد چت" and user_guid == creator_guid:
        if update.reply_message_id:
            access_list = ["DeleteGlobalAllMessages","SetJoinLink","PinMessages","SetMemberAccess"]
            await bot.set_group_admin(group_guid,user_replay_guid,"SetAdmin",access_list=access_list)
            await bot.send_message(group_guid,f"**کاربر** ﹝[{user_reply_name}](https://rubika.ir/{user_reply_id})﹞ **ادمین چت شد🗽**",id_message)
        else:
            await bot.send_message(group_guid, "لطفاً این دستور را روی پیام فرد مورد نظر ریپلای کنید.",id_message)

    elif text == "ویژه" and is_admin:
        if update.reply_message_id:
            await bot.set_group_admin(group_guid,user_replay_guid,"SetAdmin")
            await bot.send_message(group_guid,f"**کاربر** ﹝[{user_reply_name}](https://rubika.ir/{user_reply_id})﹞ **ادمین ویژه شد🧑‍💻**",id_message)
        else:
            await bot.send_message(group_guid, "لطفاً این دستور را روی پیام فرد مورد نظر ریپلای کنید.")

    elif "مالک" in text:
        await bot.send_message(group_guid,f"**مالک گروه** ﹝[{creator_name}](https://rubika.ir/{creator_id})﹞",id_message)

    elif text in ["امارم","امار","اینفو"]:
        user_bio = user_info.user.bio
        user_birthday = user_info.user.birth_date
        birth_date_jalali = (jdatetime.date.fromgregorian(date=datetime.strptime(user_info.user.birth_date, "%Y-%m-%d")).strftime("%Y/%m/%d") if user_info.user.birth_date else "نامشخص")
        user_online_time = user_info.user.online_time.approximate_period
        text_info_user = f"""👤 **مشخصات کاربر**
    ━━━━━━━━━━━━━━━\n
📛 **نام: {user_name}\n
🧑‍💻 ایدی: @{user_id}\n
🆔 گوید کاربر:** `{user_guid}`\n**
🗽 ادمین : {"هستید✅" if is_admin else "نیستید❌"}\n
🚫 اخطار ها : {user_warning}\n
📅 تاریخ تولد: {birth_date_jalali}\n
🗓 آخرین حضور: {user_online_time}\n
📖 بیو: {user_bio}**"""
        await bot.send_message(group_guid,text_info_user,id_message)

    elif text == "لینک":
        await bot.send_message(group_guid,f"**🅰️لینک گروه:\n{link_group['join_link']}**",id_message)

    elif text == "امارش" and is_admin:
        if update.reply_message_id: 
            text_info_user_replay = f"""👤 **مشخصات کاربر**
        ━━━━━━━━━━━━━━━
📛 **نام: {user_reply_name}\n
🧑‍💻 نام‌کاربری: @{user_reply_id}\n
🗽 ادمین : {"هست✅" if is_admin else "نیست❌"}\n
🚫 اخطار ها : {user_warning}\n
🆔 گوید کاربر: **`{user_replay_guid}`\n**
📖 بیو:
{user_reply_bio}**"""
            await bot.send_message(group_guid,text_info_user_replay,id_message)
        else:
            await bot.send_message(group_guid, "لطفاً این دستور را روی پیام فرد مورد نظر ریپلای کنید.",id_message)

    elif text in ["عزل","برکناری","برکنار"] and user_guid == creator_guid:
        if update.reply_message_id:
            await bot.set_group_admin(group_guid,user_replay_guid,"UnsetAdmin")
            await bot.send_message(group_guid,f"**کاربر** ﹝[{user_reply_name}](https://rubika.ir/{user_reply_id})﹞ **برکنار شد⤵️**",id_message)
        else:
            await bot.send_message(group_guid, "لطفاً این دستور را روی پیام فرد مورد نظر ریپلای کنید.",id_message)

    elif text  in ["بستن", "بستن گروه", "بسته شو"] and is_admin:
        await bot.set_group_default_access(group_guid,[])
        await bot.send_message(group_guid,"گروه بسته شد🔒",id_message)
    
    elif text in ["باز کردن", "باز کردن گروه", "باز", "باز شو"] and is_admin:
        await bot.set_group_default_access(group_guid,['SendMessages'])
        await bot.send_message(group_guid,"گروه برای تمامی کاربران باز شد👐",id_message)

    elif text in ["پین","pin","سنجاق"] and is_admin:
        if update.reply_message_id:
            await bot.set_pin(group_guid,update.reply_message_id)
            await bot.send_message(group_guid,"پیام ریپلای شده پین شد📌",id_message)
        else:
            await bot.send_message(group_guid, "لطفاً این دستور را روی پیام فرد مورد نظر ریپلای کنید.",id_message)

    elif text in ["unpin","برداشتن سنجاق","انپین"] and is_admin:
        if update.reply_message_id:
            await bot.set_unpin(group_guid,update.reply_message_id)
            await bot.send_message(group_guid,"پیام ریپلای شده ان پین شد📍",id_message)
        else:
            await bot.send_message(group_guid, "لطفاً این دستور را روی پیام فرد مورد نظر ریپلای کنید.",id_message)

    elif text in ["کال"] and is_admin:
        await bot.create_group_voice_chat(group_guid)
        await bot.send_message(group_guid,"کال فعال شد🎤",id_message)

    elif text == "یک عضو از طریق لینک به گروه افزوده شد.":
        welcome_message = f"""
👋 سلام و خوش آمدید به **{name_group}**!

ما خیلی خوشحالیم که به جمع ما پیوستید! 🌟 در اینجا، شما می‌توانید با اعضای دیگر گپ بزنید، اطلاعات مفید به اشتراک بذارید و از گفتگوهای جذاب لذت ببرید. 

🔹 **لطفاً به چند نکته توجه کنید**:
1️⃣ قبل از شروع، لطفاً قوانین گروه رو مطالعه کنید.
2️⃣ احترام به دیگران، اولین قانون اینجاست.
3️⃣ از ارسال پیام‌های اسپم و غیر مرتبط خودداری کنید.

همچنین، در صورت نیاز به کمک یا سوال، همیشه می‌توانید با مدیران گروه در ارتباط باشید. 🤝

خوش بگذره و منتظرتون هستیم! 🚀
"""
        await bot.send_message(group_guid,welcome_message)

    elif text == "ادمین ها":
        admins_message = "🛠️ **لیست ادمین‌ها در گروه:**\n\n"
        for admin in admins_info["in_chat_members"]:
            admin_name = admin["first_name"] 
            admin_role = admin["username"]
            
            admins_message += f"🔹 [{admin_name}]({admin_role})\n"
        
        await bot.send_message(group_guid, admins_message)

    elif text.startswith('حذف') and is_admin:
        number_delete = text.split()[1]
        await bot.delete_messages(group_guid,lismsg[len(lismsg):int(number_delete)],'Global')
        await bot.send_message(group_guid,f"{number_delete} پیام اخر گروه حدف شد🪄",id_message)

    elif text == "سکوت" and is_admin:
        if update.reply_message_id:
        
            if is_admin_replay:
                msg = f"**کاربر** ﹝[{user_reply_name}](https://rubika.ir/{user_reply_id})﹞ **ادمین است و نمیتوانید او را در لیست سکوت قرار دهید**"
                await bot.send_message(group_guid,msg,id_message)

            elif user_replay_guid in silent[group_guid]:
                msg = f"**کاربر** ﹝[{user_reply_name}](https://rubika.ir/{user_reply_id})﹞ **در حالت سکوت قرار دارد🤐**"
                await bot.send_message(group_guid,msg,id_message)

            else:
                silent[group_guid].append(user_replay_guid)
                text_silent = f"**کاربر** ﹝[{user_reply_name}](https://rubika.ir/{user_reply_id})﹞ **در حالت سکوت قرار گرفت🤐**"
                await bot.send_message(group_guid,text_silent,id_message)
        else:
            await bot.send_message(group_guid, "لطفاً این دستور را روی پیام فرد مورد نظر ریپلای کنید.",id_message)

    elif text == "لیست سکوت" and is_admin:
        silent_list_guid = silent[group_guid]
        if len(silent_list_guid) == 0:
            await bot.send_message(group_guid,"لیست سکوت خالی است👐")
        else:
            msg = """لیست کاربران در حالت سکوت🤐\n
    ━━━━━━━━━━━━━━━\n"""
            for user_silent in silent_list_guid:
                info_user_silent = await bot.get_user_info(user_silent)
                name_user_silent = info_user_silent.user.first_name
                id_user_silent = info_user_silent.user.username
                msg += f"[{name_user_silent}](https://rubika.ir/{id_user_silent}) : `{user_silent}`\n"
            await bot.send_message(group_guid,msg,id_message)

    elif text.startswith(("آزاد","ازاد")) and is_admin:
        if update.reply_message_id:
            if user_replay_guid in silent[group_guid]:
                silent[group_guid].remove(user_replay_guid)
                msg = f"**کاربر** ﹝[{user_reply_name}](https://rubika.ir/{user_reply_id})﹞ **از لیست سکوت خارج شد🎤**"
                await bot.send_message(group_guid,msg,id_message)
            else:
                msg = f"**کاربر** ﹝[{user_reply_name}](https://rubika.ir/{user_reply_id})﹞ **در لیست سکوت قرار ندارد💢**"
                await bot.send_message(group_guid,msg,id_message)       
        else:
            if user_replay_guid in silent[group_guid]:
                silent[group_guid].remove(text.split()[1])
                info_user_silent_a = await bot.get_user_info(text.split()[1])
                name_user_silent_a = info_user_silent_a.user.first_name
                id_user_silent_a = info_user_silent_a.user.username
                msg = f"**کاربر** ﹝[{name_user_silent_a}](https://rubika.ir/{id_user_silent_a})﹞ **از لیست سکوت خارج شد🎤**"
                await bot.send_message(group_guid,msg,id_message)
            else:
                msg = f"**کاربر** ﹝[{user_reply_name}](https://rubika.ir/{user_reply_id})﹞ **در لیست سکوت قرار ندارد💢**"
                await bot.send_message(group_guid,msg,id_message)


bot.run()
