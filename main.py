import os
import asyncio
import sqlite3
import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

# Environment variables dan o'qish
API_TOKEN = os.getenv('BOT_TOKEN', '7515019190:AAETOcIVcS93k6DkptBM02M4jNNPOSDJU5c')
ADMIN_ID = int(os.getenv('ADMIN_ID', '5796033703'))

print(f"🤖 Bot token: ...{API_TOKEN[-10:]}")
print(f"👑 Admin ID: {ADMIN_ID}")

# ==================== STATE LAR ====================
class BroadcastState(StatesGroup):
    waiting_message = State()

class SupportState(StatesGroup):
    waiting_question = State()

class MacroState(StatesGroup):
    waiting_name = State()
    waiting_content = State()

# ==================== MA'LUMOTLAR BAZASI ====================
def init_db():
    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            joined_date TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS support_questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            question TEXT,
            answered BOOLEAN DEFAULT 0,
            created_date TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS macros (
            name TEXT PRIMARY KEY,
            content TEXT,
            created_date TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

init_db()

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# ==================== FUNKSIYALAR ====================
def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID

def admin_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📊 Statistika"), KeyboardButton(text="👥 Foydalanuvchilar")],
            [KeyboardButton(text="📢 Xabar Yuborish"), KeyboardButton(text="🆘 Support Savollar")],
            [KeyboardButton(text="📝 Makroslar"), KeyboardButton(text="⚙️ Sozlamalar")],
            [KeyboardButton(text="🔙 Asosiy menyu")]
        ],
        resize_keyboard=True
    )
    return keyboard

def main_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🆘 Support"), KeyboardButton(text="ℹ️ Ma'lumot")],
            [KeyboardButton(text="📞 Bog'lanish"), KeyboardButton(text="👨‍💻 Admin")]
        ],
        resize_keyboard=True
    )
    return keyboard

# ==================== ASOSIY HANDLERLAR ====================
@dp.message(Command('start'))
async def start_handler(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    
    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()
    cursor.execute('INSERT OR IGNORE INTO users VALUES (?, ?, ?, ?)', 
                  (user_id, username, first_name, datetime.datetime.now()))
    conn.commit()
    conn.close()
    
    await message.answer(f"""
👋 Salom {first_name}!

🤖 **Mening ismim - Admin Bot!**

🚀 **Mening imkoniyatlarim:**
• 📊 Statistika ko'rsatish
• 📢 Xabar yuborish
• 🆘 Support tizimi
• 📝 Makroslar
• 👥 Foydalanuvchilar boshqaruvi

🛠️ Admin panel: /admin
🆘 Yordam: /help
    """, reply_markup=main_keyboard())

@dp.message(Command('help'))
async def help_handler(message: types.Message):
    await message.answer("""
🆘 **Yordam:**

📋 **Buyruqlar:**
/start - Botni ishga tushirish
/help - Yordam ko'rsatish
/stats - Statistika
/support - Support xizmati

📞 **Bog'lanish:**
Support tugmasi orqali savolingizni yuboring

👨‍💻 **Admin:**
/admin - Admin panel (faqat adminlar uchun)
    """)

@dp.message(Command('stats'))
async def stats_handler(message: types.Message):
    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM users')
    user_count = cursor.fetchone()[0]
    conn.close()
    
    await message.answer(f"📊 Bot statistikasi:\n\n👥 Foydalanuvchilar: {user_count} ta")

# ==================== YANGI KNOBKALAR ====================
@dp.message(lambda message: message.text == "📞 Bog'lanish")
async def contact_handler(message: types.Message):
    await message.answer("""
📞 **Bog'lanish:**

👨‍💻 **Developer:** Sizning Ismingiz
📧 **Email:** siz@email.com
📱 **Telegram:** @sizning_username

🕒 **Ish vaqti:** 24/7
⚡ **Javob:** 1 soat ichida
    """)

@dp.message(lambda message: message.text == "ℹ️ Ma'lumot")
async def info_handler(message: types.Message):
    await message.answer("""
ℹ️ **Bot haqida ma'lumot:**

🤖 **Nomi:** Admin Bot
🛠️ **Versiya:** 2.0
📅 **Yaratilgan:** 2024
👨‍💻 **Developer:** Siz

🚀 **Funksiyalar:**
• 👥 Foydalanuvchilar boshqaruvi
• 🆘 Support tizimi
• 📊 Statistika
• 📢 Xabar yuborish
• 📝 Makroslar
    """)

# ==================== SUPPORT TIZIMI ====================
@dp.message(lambda message: message.text == "🆘 Support")
async def support_start(message: types.Message):
    await message.answer("📝 **Support xizmati**\n\nSavolingizni yozing va men uni adminlarga yuboraman:")
    await SupportState.waiting_question.set()

@dp.message(SupportState.waiting_question)
async def support_question(message: types.Message, state: FSMContext):
    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO support_questions (user_id, question, created_date) VALUES (?, ?, ?)',
                  (message.from_user.id, message.text, datetime.datetime.now()))
    conn.commit()
    conn.close()
    
    admin_message = f"""
🆘 **Yangi Support Savol**

👤 Foydalanuvchi: {message.from_user.first_name}
🆔 ID: {message.from_user.id}
📱 Username: @{message.from_user.username or "Yo'q"}
📝 Savol: {message.text}
⏰ Vaqt: {datetime.datetime.now().strftime('%H:%M %d.%m.%Y')}
    """
    
    try:
        await bot.send_message(ADMIN_ID, admin_message)
    except:
        pass
    
    await message.answer("✅ Savolingiz qabul qilindi! Adminlar tez orada javob berishadi.", reply_markup=main_keyboard())
    await state.finish()

# ==================== MAKROSLAR TIZIMI ====================
@dp.message(lambda message: message.text == "📝 Makroslar")
async def macros_menu(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.answer("❌ Siz admin emassiz!")
        return
    
    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT name, content FROM macros')
    macros = cursor.fetchall()
    conn.close()
    
    if macros:
        macros_text = "📝 **Mavjud Makroslar:**\n\n"
        for macro_name, content in macros:
            macros_text += f"• `{macro_name}` - {content[:30]}...\n"
        
        macros_text += "\n🔧 **Boshqarish:**\n/add_macro - Yangi qo'shish"
    else:
        macros_text = "📝 Makroslar hali mavjud emas.\n\nYangi makros qo'shish: /add_macro"
    
    await message.answer(macros_text)

@dp.message(Command('add_macro'))
async def add_macro_start(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.answer("❌ Siz admin emassiz!")
        return
    
    await message.answer("📝 **Yangi makros qo'shish**\n\nMakros nomini kiriting (masalan: %salom):")
    await MacroState.waiting_name.set()

@dp.message(MacroState.waiting_name)
async def process_macro_name(message: types.Message, state: FSMContext):
    if not message.text.startswith('%'):
        await message.answer("❌ Makros nomi % belgisi bilan boshlanishi kerak!\nMasalan: %salom\nQayta kiriting:")
        return
    
    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT name FROM macros WHERE name = ?', (message.text,))
    existing = cursor.fetchone()
    conn.close()
    
    if existing:
        await message.answer("❌ Bu nomli makros allaqachon mavjud!\nBoshqa nom kiriting:")
        return
    
    await state.update_data(macro_name=message.text)
    await message.answer(f"✅ Nom qabul qilindi: `{message.text}`\n\n📋 Endi makros matnini kiriting:")
    await MacroState.next()

@dp.message(MacroState.waiting_content)
async def process_macro_content(message: types.Message, state: FSMContext):
    data = await state.get_data()
    macro_name = data['macro_name']
    macro_content = message.text
    
    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO macros (name, content, created_date) VALUES (?, ?, ?)',
                      (macro_name, macro_content, datetime.datetime.now()))
        conn.commit()
        await message.answer(f"✅ **Makros muvaffaqiyatli qo'shildi!**\n\n📛 Nomi: `{macro_name}`\n📋 Matn: {macro_content}\n\n💡 **Ishlatish:** `{macro_name}` deb yozing")
    except Exception as e:
        await message.answer(f"❌ Xatolik yuz berdi: {e}")
    finally:
        conn.close()
    
    await state.finish()

@dp.message(lambda message: message.text.startswith('%'))
async def use_macro(message: types.Message):
    macro_name = message.text.strip()
    
    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT content FROM macros WHERE name = ?', (macro_name,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        await message.answer(result[0])
    else:
        await message.answer(f"❌ `{macro_name}` makrosi topilmadi!\n\n📝 Mavjud makroslarni ko'rish uchun: /admin → Makroslar")

# ==================== ADMIN PANEL ====================
@dp.message(Command('admin'))
async def admin_handler(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.answer("❌ Siz admin emassiz!")
        return
    
    await message.answer("🛠️ **Admin Panelga Xush Kelibsiz!**\n\nQuyidagi tugmalardan foydalaning:", reply_markup=admin_keyboard())

@dp.message(lambda message: message.text == "📊 Statistika")
async def admin_stats(message: types.Message):
    if not is_admin(message.from_user.id):
        return
    
    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM users')
    total_users = cursor.fetchone()[0]
    
    today = datetime.datetime.now().date()
    cursor.execute('SELECT COUNT(*) FROM users WHERE DATE(joined_date) = ?', (today,))
    today_users = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM support_questions WHERE answered = 0')
    unanswered_questions = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM macros')
    total_macros = cursor.fetchone()[0]
    
    conn.close()
    
    stats_text = f"""
📊 **Admin Statistikasi:**

👥 Jami foydalanuvchilar: {total_users}
🆕 Bugun qo'shilgan: {today_users}
🆘 Javobsiz savollar: {unanswered_questions}
📝 Makroslar: {total_macros}
📈 Faollik: {today_users} ta/yangi
    """
    await message.answer(stats_text)

@dp.message(lambda message: message.text == "👥 Foydalanuvchilar")
async def admin_users(message: types.Message):
    if not is_admin(message.from_user.id):
        return
    
    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users ORDER BY joined_date DESC LIMIT 15')
    users = cursor.fetchall()
    conn.close()
    
    users_text = "👥 **Oxirgi 15 ta foydalanuvchi:**\n\n"
    for user in users:
        join_date = str(user[3]).split()[0] if user[3] else "Noma'lum"
        username = f"@{user[1]}" if user[1] else "Yo'q"
        users_text += f"🆔 {user[0]} | 👤 {user[2]} | 📱 {username}\n"
    
    await message.answer(users_text[:4000])

@dp.message(lambda message: message.text == "📢 Xabar Yuborish")
async def broadcast_start(message: types.Message):
    if not is_admin(message.from_user.id):
        return
    
    await message.answer("📢 **Xabar yuborish**\n\nBarcha foydalanuvchilarga yubormoqchi bo'lgan xabaringizni yozing:")
    await BroadcastState.waiting_message.set()

@dp.message(BroadcastState.waiting_message)
async def broadcast_send(message: types.Message, state: FSMContext):
    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT user_id FROM users')
    users = cursor.fetchall()
    conn.close()
    
    total = len(users)
    success = 0
    
    progress_msg = await message.answer(f"📤 Xabar yuborilmoqda... 0/{total}")
    
    for i, user in enumerate(users):
        try:
            await bot.send_message(chat_id=user[0], text=f"📢 **Botdan xabar:**\n\n{message.text}")
            success += 1
        except:
            pass
        
        if (i + 1) % 5 == 0:
            await progress_msg.edit_text(f"📤 Xabar yuborilmoqda... {i+1}/{total}")
        
        await asyncio.sleep(0.2)
    
    await progress_msg.edit_text(f"""
✅ **Xabar yuborildi!**

📨 Jami: {total} ta
✅ Muvaffaqiyatli: {success} ta
❌ Xatolik: {total - success} ta
    """)
    await state.finish()

@dp.message(lambda message: message.text == "🆘 Support Savollar")
async def support_questions(message: types.Message):
    if not is_admin(message.from_user.id):
        return
    
    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT sq.id, u.first_name, sq.question, sq.created_date 
        FROM support_questions sq
        LEFT JOIN users u ON sq.user_id = u.user_id
        WHERE sq.answered = 0
        ORDER BY sq.created_date DESC
        LIMIT 10
    ''')
    questions = cursor.fetchall()
    conn.close()
    
    if not questions:
        await message.answer("✅ Javobsiz savollar yo'q!")
        return
    
    questions_text = "🆘 **Oxirgi 10 ta javobsiz savol:**\n\n"
    for q in questions:
        date_str = str(q[3]).split('.')[0] if q[3] else "Noma'lum"
        questions_text += f"📝 **#{q[0]}** | 👤 {q[1]}\n⏰ {date_str}\n❓ {q[2]}\n\n"
    
    await message.answer(questions_text[:4000])

@dp.message(lambda message: message.text == "⚙️ Sozlamalar")
async def settings_handler(message: types.Message):
    if not is_admin(message.from_user.id):
        return
    
    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM users')
    total_users = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM macros')
    total_macros = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM support_questions WHERE answered = 0')
    unanswered = cursor.fetchone()[0]
    
    conn.close()
    
    settings_text = f"""
⚙️ **Bot Sozlamalari**

📊 **Statistika:**
• 👥 Foydalanuvchilar: {total_users}
• 📝 Makroslar: {total_macros}
• 🆘 Javobsiz savollar: {unanswered}

🛠️ **Sozlash imkoniyatlari:**
• Bot nomini o'zgartirish
• Start xabarini sozlash
• Tugmalarni moslashtirish
• Makroslar boshqaruvi
    """
    
    await message.answer(settings_text)

@dp.message(lambda message: message.text == "🔙 Asosiy menyu")
async def back_to_main(message: types.Message):
    await message.answer("🏠 Asosiy menyu:", reply_markup=main_keyboard())

@dp.message(lambda message: message.text == "👨‍💻 Admin")
async def admin_button(message: types.Message):
    await admin_handler(message)

# ==================== ASOSIY DASTUR ====================
async def main():
    print('🚀 Bot Render.com da ishga tushmoqda...')
    print('✅ Barcha funksiyalar tayyor!')
    print(f'👑 Admin ID: {ADMIN_ID}')
    print('📊 Ma\'lumotlar bazasi: bot_data.db')
    print('🌐 Bot 24/7 ishlaydi!')
    
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())