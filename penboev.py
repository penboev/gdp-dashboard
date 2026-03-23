import os
import streamlit as st
import google.generativeai as genai

# 1. ОСНОВНА КОНФИГУРАЦИЯ
st.set_page_config(page_title="penboev_os", page_icon="💻", layout="wide")

# 2. ЗАРЕЖДАНЕ НА ЛОГО (Търси файла в папката)
logo_file = None
for f in ["logo.png", "Logo.png", "logo.PNG", "LOGO.PNG", "logo.jpg"]:
    if os.path.exists(f):
        logo_file = f
        break

# 3. ИНИЦИАЛИЗАЦИЯ НА AI (Динамично намиране на модел)
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("Липсва GOOGLE_API_KEY в Secrets!")
    st.stop()

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

@st.cache_resource
def get_working_model():
    try:
        # Автоматично вземаме първия наличен модел (напр. gemini-2.0-flash)
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        if models:
            return genai.GenerativeModel(models[0])
    except Exception as e:
        st.error(f"Грешка при списъка с модели: {e}")
    return None

model = get_working_model()

# 4. ИСТОРИЯ НА ЧАТА
if "messages" not in st.session_state:
    st.session_state.messages = []

# 5. СТРАНИЧЕН ПАНЕЛ (SIDEBAR) - ТУК СА ВАШИТЕ БУТОНИ
with st.sidebar:
    if logo_file:
        st.image(logo_file, use_container_width=True)
    else:
        st.title("🛠 penboev_os")
    
    if model:
        st.success(f"✅ Активен: {model.model_name}")
    
    st.markdown("---")
    st.subheader("🚀 Инструменти")
    
    tool_prompt = None
    if st.button("🔍 Bug Hunter", use_container_width=True):
        tool_prompt = "Анализирай следния код за грешки и предложи решение:"
    
    if st.button("📝 Docstrings", use_container_width=True):
        tool_prompt = "Добави професионална документация (docstrings) към този код:"
    
    if st.button("⚡ Optimize", use_container_width=True):
        tool_prompt = "Оптимизирай този код за по-добра производителност:"

    st.markdown("---")
    if st.button("🗑 Изчисти чата", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# 6. ГЛАВЕН ИНТЕРФЕЙС
st.title("💻 penboev_os: Dev Mode")

# Показване на историята
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 7. ЛОГИКА НА РАБОТА
user_input = st.chat_input("Напиши задача или постави код тук...")

# Обработка на инструменти (Bug Hunter / Optimize)
if tool_prompt and st.session_state.messages:
    last_user_msg = next((m["content"] for m in reversed(st.session_state.messages) if m["role"] == "user"), None)
    if last_user_msg:
        with st.chat_message("assistant"):
            with st.spinner("AI анализира..."):
                try:
                    response = model.generate_content(f"{tool_prompt}\n\n{last_user_msg}")
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                    st.rerun()
                except Exception as e:
                    st.error(f"Грешка при инструмента: {e}")

# Стандартен чат
elif user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)
    
    with st.chat_message("assistant"):
        with st.spinner("Мисли..."):
            try:
                response = model.generate_content(user_input)
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"Грешка: {e}")

# 8. ФУНКЦИЯ ЗА ИЗТЕГЛЯНЕ (💾)
if st.session_state.messages:
    last_res = st.session_state.messages[-1]["content"]
    if "```" in last_res:
        st.download_button(
            label="💾 Изтегли генерирания код",
            data=last_res,
            file_name="penboev_output.py",
            mime="text/plain"
        )
