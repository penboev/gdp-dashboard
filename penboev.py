import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="penboev_os", layout="wide")

# 1. API Ключ
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("Липсва ключ в Secrets!")
    st.stop()

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# 2. Опростена проверка на модела
try:
    # Директно опитваме с най-стабилния модел
    model = genai.GenerativeModel('gemini-pro')
    # Проверка дали работи
    model.generate_content("Hi")
    st.sidebar.success("✅ AI е онлайн (Gemini Pro)")
except Exception as e:
    st.sidebar.error(f"❌ Грешка при старт: {e}")
    st.stop()

# 3. Интерфейс
st.title("💻 penboev_os: Debug Tool")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Показване на чата
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 4. Логика
user_input = st.chat_input("Постави код тук...")

# Бутони за инструменти
with st.sidebar:
    st.subheader("Инструменти")
    bug_hunter = st.button("🔍 Bug Hunter")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)
    
    with st.chat_message("assistant"):
        response = model.generate_content(user_input)
        st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})

if bug_hunter and st.session_state.messages:
    last_msg = st.session_state.messages[-1]["content"]
    with st.chat_message("assistant"):
        res = model.generate_content(f"Открий грешките в този код:\n\n{last_msg}")
        st.markdown(res.text)
        st.session_state.messages.append({"role": "assistant", "content": res.text})
