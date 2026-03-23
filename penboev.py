import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="penboev_os", layout="wide")

# 1. API Ключ
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("Липсва ключ в Secrets!")
    st.stop()

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# 2. ДИНАМИЧНО ЗАРЕЖДАНЕ (Решава грешка 404)
@st.cache_resource
def load_best_model():
    try:
        # Питаме Google кои модели са достъпни за ВАШИЯ ключ
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                # Избираме първия наличен (обикновено gemini-1.5-flash)
                return genai.GenerativeModel(m.name)
    except Exception as e:
        st.error(f"Грешка при списъка с модели: {e}")
    return None

model = load_best_model()

# 3. ИНТЕРФЕЙС
with st.sidebar:
    st.title("🛠 Настройки")
    if model:
        st.success(f"✅ Активен: {model.model_name}")
    else:
        st.error("❌ Няма достъпни модели.")
        st.stop()
    
    if st.button("🗑 Изчисти чата"):
        st.session_state.messages = []
        st.rerun()

st.title("💻 penboev_os: Debug Tool")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Показване на историята
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 4. ЛОГИКА НА ЧАТА
user_input = st.chat_input("Постави код или задай въпрос...")

if user_input:
    # Добавяме съобщението на потребителя
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)
    
    # Генерираме отговор от AI
    with st.chat_message("assistant"):
        with st.spinner("AI мисли..."):
            try:
                response = model.generate_content(user_input)
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"Грешка при генериране: {e}")