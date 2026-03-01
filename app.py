import streamlit as st
import requests
import time
from datetime import datetime, date, timedelta
import uuid
import streamlit.components.v1 as components

# ========== URL ТВОЕЙ НОВОЙ ФУНКЦИИ ==========
PROXY_URL = "https://functions.yandexcloud.net/d4engbmsh7mbf2ps4ile"

# ========== ТЕКСТЫ ==========
translations = {
    "ru": {
        "title": "NEXUS",
        "subtitle": "🌀 твой личный помощник",
        "new_chat": "Новый чат",
        "today": "Сегодня",
        "yesterday": "Вчера",
        "earlier": "Ранее",
        "clear_chat": "Очистить чат",
        "rename": "Переименовать",
        "pin": "Закрепить",
        "delete": "Удалить",
        "input_placeholder": "Напиши сообщение...",
        "generating": "🌀 Думаю...",
        "error": "Ошибка",
        "new_chat_placeholder": "Новый чат",
        "welcome": "Привет! Я твой помощник."
    }
}

# ========== КОНФИГУРАЦИЯ ==========
st.set_page_config(
    page_title="Nexus",
    page_icon="🌀",
    layout="centered",
    initial_sidebar_state="expanded"
)

# ========== СТИЛИ ==========
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;600;700&display=swap');
    
    * { font-family: 'Space Grotesk', sans-serif; }
    
    .stApp {
        background: radial-gradient(circle at 20% 20%, #1a1a2e, #16213e, #0f3460);
        color: white;
    }
    
    h1 {
        font-size: 4rem !important;
        font-weight: 700 !important;
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0 !important;
        animation: glow 3s ease-in-out infinite;
    }
    
    @keyframes glow {
        0%, 100% { filter: drop-shadow(0 0 10px rgba(168,237,234,0.5)); }
        50% { filter: drop-shadow(0 0 20px rgba(254,214,227,0.8)); }
    }
    
    .subtitle {
        text-align: center;
        color: #a8edea;
        font-size: 1.2rem;
        margin-bottom: 2rem;
        opacity: 0.9;
    }
    
    .stChatMessage {
        border-radius: 20px !important;
        padding: 15px 20px !important;
        margin: 10px 0 !important;
        animation: fadeIn 0.5s;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .stChatMessage[data-testid="user"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
    }
    
    .stChatMessage[data-testid="assistant"] {
        background: rgba(255,255,255,0.1) !important;
        backdrop-filter: blur(10px) !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        color: white !important;
    }
    
    .stChatInputContainer {
        background: transparent !important;
        padding: 10px !important;
    }
    
    .stChatInputContainer input {
        background: rgba(255,255,255,0.1) !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        border-radius: 30px !important;
        color: white !important;
        padding: 15px 20px !important;
        font-size: 16px !important;
    }
    
    .stChatInputContainer input::placeholder {
        color: rgba(255,255,255,0.5) !important;
    }
    
    .css-1d391kg {
        background: rgba(0,0,0,0.3) !important;
        backdrop-filter: blur(10px);
    }
    
    .stButton button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 30px !important;
        padding: 10px 25px !important;
        font-weight: 600 !important;
        transition: transform 0.3s !important;
    }
    
    .stButton button:hover {
        transform: scale(1.05);
    }
    
    .date-header {
        color: #a8edea;
        font-size: 0.9rem;
        font-weight: 600;
        margin: 15px 0 5px 0;
        opacity: 0.8;
    }
    
    .chat-item {
        position: relative;
        padding: 8px 12px;
        margin: 2px 0;
        border-radius: 8px;
        background: rgba(255,255,255,0.03);
        cursor: context-menu;
        user-select: none;
        transition: background 0.2s;
    }
    
    .chat-item:hover {
        background: rgba(168,237,234,0.1);
    }
    
    .chat-item.active {
        background: rgba(168,237,234,0.15);
        border-left: 2px solid #a8edea;
    }
    
    .chat-item span {
        pointer-events: none;
    }
    
    .custom-menu {
        position: fixed;
        background: rgba(30, 30, 40, 0.95);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(168,237,234,0.3);
        border-radius: 12px;
        padding: 8px 0;
        min-width: 180px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        z-index: 9999;
        display: none;
    }
    
    .custom-menu.show {
        display: block;
    }
    
    .menu-item {
        padding: 10px 20px;
        color: white;
        cursor: pointer;
        transition: background 0.2s;
        font-size: 14px;
    }
    
    .menu-item:hover {
        background: rgba(168,237,234,0.2);
    }
    
    .menu-item.delete {
        color: #ff6b6b;
    }
    
    .menu-item.delete:hover {
        background: rgba(255,107,107,0.2);
    }
</style>
""", unsafe_allow_html=True)

# JavaScript для контекстного меню
components.html("""
<script>
document.addEventListener('contextmenu', function(e) {
    const chatItem = e.target.closest('.chat-item');
    if (!chatItem) return;
    
    e.preventDefault();
    
    const oldMenu = document.querySelector('.custom-menu');
    if (oldMenu) oldMenu.remove();
    
    const menu = document.createElement('div');
    menu.className = 'custom-menu show';
    menu.style.left = e.pageX + 'px';
    menu.style.top = e.pageY + 'px';
    
    const chatId = chatItem.dataset.chatId;
    const chatName = chatItem.dataset.chatName;
    
    const renameItem = document.createElement('div');
    renameItem.className = 'menu-item';
    renameItem.textContent = 'Переименовать';
    renameItem.onclick = function() {
        const newName = prompt('Введите новое название:', chatName);
        if (newName) {
            window.location.href = '/?rename=' + encodeURIComponent(chatId) + '&name=' + encodeURIComponent(newName);
        }
        menu.remove();
    };
    
    const pinItem = document.createElement('div');
    pinItem.className = 'menu-item';
    pinItem.textContent = 'Закрепить';
    pinItem.onclick = function() {
        window.location.href = '/?pin=' + encodeURIComponent(chatId);
        menu.remove();
    };
    
    const deleteItem = document.createElement('div');
    deleteItem.className = 'menu-item delete';
    deleteItem.textContent = 'Удалить';
    deleteItem.onclick = function() {
        if (confirm('Удалить чат?')) {
            window.location.href = '/?delete=' + encodeURIComponent(chatId);
        }
        menu.remove();
    };
    
    menu.appendChild(renameItem);
    menu.appendChild(pinItem);
    menu.appendChild(deleteItem);
    
    document.body.appendChild(menu);
    
    document.addEventListener('click', function closeMenu() {
        menu.remove();
        document.removeEventListener('click', closeMenu);
    }, {once: true});
});
</script>
""", height=0)

# ========== ИНИЦИАЛИЗАЦИЯ ==========
if "chats" not in st.session_state:
    first_chat_id = str(uuid.uuid4())
    now = datetime.now()
    st.session_state.chats = {
        first_chat_id: {
            "name": "Новый чат",
            "messages": [],
            "created": now,
            "created_str": now.strftime("%H:%M"),
            "first_message": "",
            "pinned": False
        }
    }
    st.session_state.current_chat_id = first_chat_id

# ========== ОБРАБОТКА ЗАПРОСОВ ИЗ URL ==========
if "rename" in st.query_params and "name" in st.query_params:
    chat_id = st.query_params["rename"]
    new_name = st.query_params["name"]
    if chat_id in st.session_state.chats:
        st.session_state.chats[chat_id]["name"] = new_name
    st.rerun()

if "pin" in st.query_params:
    chat_id = st.query_params["pin"]
    if chat_id in st.session_state.chats:
        st.session_state.chats[chat_id]["pinned"] = not st.session_state.chats[chat_id].get("pinned", False)
    st.rerun()

if "delete" in st.query_params:
    chat_id = st.query_params["delete"]
    if chat_id in st.session_state.chats and len(st.session_state.chats) > 1:
        del st.session_state.chats[chat_id]
        if st.session_state.current_chat_id == chat_id:
            st.session_state.current_chat_id = list(st.session_state.chats.keys())[0]
    st.rerun()

if "chat" in st.query_params:
    chat_id = st.query_params["chat"]
    if chat_id in st.session_state.chats:
        st.session_state.current_chat_id = chat_id
    st.rerun()

# ========== ФУНКЦИЯ ДЛЯ ОБНОВЛЕНИЯ НАЗВАНИЯ ЧАТА ==========
def update_chat_name(chat_id, message):
    chat = st.session_state.chats[chat_id]
    if not chat["first_message"] and message:
        chat_name = message[:30] + "..." if len(message) > 30 else message
        chat["name"] = chat_name
        chat["first_message"] = message

# ========== ФУНКЦИЯ ДЛЯ ГРУППИРОВКИ ЧАТОВ ПО ДАТАМ ==========
def group_chats_by_date(chats_dict):
    today = date.today()
    yesterday = today - timedelta(days=1)
    
    pinned = []
    groups = {
        "today": [],
        "yesterday": [],
        "earlier": {}
    }
    
    for chat_id, chat_data in chats_dict.items():
        if chat_data.get("pinned", False):
            pinned.append((chat_id, chat_data))
            continue
            
        chat_date = chat_data["created"].date()
        
        if chat_date == today:
            groups["today"].append((chat_id, chat_data))
        elif chat_date == yesterday:
            groups["yesterday"].append((chat_id, chat_data))
        else:
            date_str = chat_data["created"].strftime("%d %B %Y")
            if date_str not in groups["earlier"]:
                groups["earlier"][date_str] = []
            groups["earlier"][date_str].append((chat_id, chat_data))
    
    for date_str in groups["earlier"]:
        groups["earlier"][date_str].sort(key=lambda x: x[1]["created"], reverse=True)
    
    return pinned, groups

# ========== БОКОВАЯ ПАНЕЛЬ ==========
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; font-size: 3rem; margin-bottom: 1rem;">🌀</div>
    """, unsafe_allow_html=True)
    
    t = translations["ru"]
    
    # Кнопка нового чата
    if st.button(t["new_chat"], use_container_width=True):
        new_chat_id = str(uuid.uuid4())
        now = datetime.now()
        st.session_state.chats[new_chat_id] = {
            "name": t["new_chat_placeholder"],
            "messages": [],
            "created": now,
            "created_str": now.strftime("%H:%M"),
            "first_message": "",
            "pinned": False
        }
        st.session_state.current_chat_id = new_chat_id
        st.rerun()
    
    st.markdown("---")
    
    # Получаем закрепленные и сгруппированные чаты
    pinned_chats, chat_groups = group_chats_by_date(st.session_state.chats)
    
    # Функция для отображения чата
    def display_chat(chat_id, chat_data, indent=""):
        is_active = chat_id == st.session_state.current_chat_id
        active_class = "active" if is_active else ""
        pin_icon = "📌 " if chat_data.get("pinned", False) else ""
        
        chat_html = f"""
        <a href="?chat={chat_id}" style="text-decoration: none; color: inherit;">
            <div class="chat-item {active_class}" 
                 data-chat-id="{chat_id}" 
                 data-chat-name="{chat_data['name']}">
                <span>{indent}{pin_icon}{chat_data['created_str']} - {chat_data['name']}</span>
            </div>
        </a>
        """
        st.markdown(chat_html, unsafe_allow_html=True)
    
    # Закрепленные чаты
    if pinned_chats:
        st.markdown("📌 **Закрепленные**")
        for chat_id, chat_data in pinned_chats:
            display_chat(chat_id, chat_data)
    
    # Сегодня
    if chat_groups["today"]:
        st.markdown(f'<div class="date-header">{t["today"]}</div>', unsafe_allow_html=True)
        for chat_id, chat_data in chat_groups["today"]:
            display_chat(chat_id, chat_data)
    
    # Вчера
    if chat_groups["yesterday"]:
        st.markdown(f'<div class="date-header">{t["yesterday"]}</div>', unsafe_allow_html=True)
        for chat_id, chat_data in chat_groups["yesterday"]:
            display_chat(chat_id, chat_data)
    
    # Ранее
    if chat_groups["earlier"]:
        st.markdown(f'<div class="date-header">{t["earlier"]}</div>', unsafe_allow_html=True)
        for date_str in sorted(chat_groups["earlier"].keys(), reverse=True):
            st.markdown(f'<div style="margin-left: 10px; color: #a8edea80; font-size: 0.8rem; margin-top: 10px;">{date_str}</div>', unsafe_allow_html=True)
            for chat_id, chat_data in chat_groups["earlier"][date_str]:
                display_chat(chat_id, chat_data, "  ")
    
    st.markdown("---")
    
    # Кнопка очистки чата
    if st.button(t["clear_chat"], use_container_width=True):
        st.session_state.chats[st.session_state.current_chat_id]["messages"] = []
        st.rerun()

# ========== ЗАГОЛОВОК ==========
t = translations["ru"]
st.markdown(f"<h1>{t['title']}</h1>", unsafe_allow_html=True)
st.markdown(f'<p class="subtitle">{t["subtitle"]}</p>', unsafe_allow_html=True)

# ========== ТЕКУЩИЙ ЧАТ ==========
current_chat = st.session_state.chats[st.session_state.current_chat_id]

# Приветствие для нового чата
if len(current_chat["messages"]) == 0:
    current_chat["messages"].append({
        "role": "assistant", 
        "content": t["welcome"]
    })

# ========== ОТОБРАЖЕНИЕ СООБЩЕНИЙ ==========
user_avatar = "👤"
assistant_avatar = "🌀"

for msg in current_chat["messages"]:
    if msg["role"] == "user":
        with st.chat_message("user", avatar=user_avatar):
            st.markdown(msg["content"])
    else:
        with st.chat_message("assistant", avatar=assistant_avatar):
            st.markdown(msg["content"])

# ========== ПОЛЕ ВВОДА ==========
if prompt := st.chat_input(t["input_placeholder"]):
    # Сохраняем первое сообщение как название чата
    if not current_chat["first_message"]:
        chat_name = prompt[:30] + "..." if len(prompt) > 30 else prompt
        current_chat["name"] = chat_name
        current_chat["first_message"] = prompt
    
    # Сообщение пользователя
    current_chat["messages"].append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar=user_avatar):
        st.markdown(prompt)
    
    # Получаем ответ с глубоким мышлением
    with st.chat_message("assistant", avatar=assistant_avatar):
        with st.spinner(t["generating"]):
            try:
                # Промпт для глубокого мышления (без указания языка)
                deep_prompt = f"Ты — глубокий мыслитель. Отвечай максимально подробно, развёрнуто, с примерами. Если вопрос сложный — разбей ответ на части. Используй аналитический подход.\n\nВопрос пользователя: {prompt}"
                
                response = requests.post(
                    PROXY_URL,
                    json={'message': deep_prompt},
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    answer = result.get('answer', '')
                    
                    # Эффект печатной машинки
                    placeholder = st.empty()
                    displayed_text = ""
                    for char in answer:
                        displayed_text += char
                        placeholder.markdown(displayed_text + '<span class="cursor"></span>', unsafe_allow_html=True)
                        time.sleep(0.02)
                    
                    current_chat["messages"].append({"role": "assistant", "content": answer})
                else:
                    st.error(f"{t['error']} {response.status_code}")
                    
            except Exception as e:
                st.error(f"{t['error']}: {str(e)}")