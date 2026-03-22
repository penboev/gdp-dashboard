import os
import streamlit as st
import google.generativeai as genai

# 1. КОНФИГУРАЦИЯ
st.set_page_config(page_title="penboev_os", page_icon="💻", layout="wide")

# 2. ТЪРСЕНЕ НА ЛОГО
logo_file = None
for f in ["logo.png", "Logo.png", "logo.PNG", "LOGO.PNG", "logo.jpg"]:
    if os.path.exists(f):
        logo_file = f
        break

# 3. НАСТРОЙКА НА AI (GEMINI)
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("Липсва GOOGLE_API_KEY в Settings -> Secrets!")
    st.stop()

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = genai.GenerativeModel(
    model_name='gemini-1.5-flash',
    system_instruction="Ти си Експертен Програмен Асистент в penboev_os. Пишеш чист и документиран код."
)

if "messages" not in st.session_state:
    st.session_state.messages = []

# 4. СТРАНИЧЕН ПАНЕЛ (SIDEBAR)
with st.sidebar:
    if logo_file:
        st.image(logo_file, use_container_width=True)
    else:
        st.title("🛠 penboev_os")
    
    st.markdown("---")
    st.subheader("🚀 Инструменти")
    
    tool_prompt = None
    if st.button("🔍 Bug Hunter", key="bh_btn"):
        tool_prompt = "Анализирай следния код за грешки и предложи решение:"
    
    if st.button("📝 Docstrings", key="ds_btn"):
        tool_prompt = "Добави професионална документация (docstrings) към този код:"
    
    if st.button("⚡ Optimize", key="opt_btn"):
        tool_prompt = "Оптимизирай този код за по-добра производителност:"

    st.markdown("---")
    if st.button("🗑 Изчисти чата", key="clear_btn"):
        st.session_state.messages = []
        st.rerun()

# 5. ГЛАВЕН ИНТЕРФЕЙС
st.title("💻 penboev_os: Dev Mode")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 6. ЛОГИКА НА ЧАТА
input_text = st.chat_input("Напиши задача или постави код...")

if tool_prompt and st.session_state.messages:
    last_user_msg = next((m["content"] for m in reversed(st.session_state.messages) if m["role"] == "user"), None)
    if last_user_msg:
        with st.chat_message("assistant"):
            with st.spinner("Анализирам..."):
                response = model.generate_content(f"{tool_prompt}\n\n{last_user_msg}")
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
                st.rerun()

elif input_text:
    st.session_state.messages.append({"role": "user", "content": input_text})
    with st.chat_message("user"):
        st.markdown(input_text)
    
    with st.chat_message("assistant"):
        with st.spinner("Мисли..."):
            response = model.generate_content(input_text)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})

# 7. ФУНКЦИЯ ЗА ИЗТЕГЛЯНЕ
if st.session_state.messages:
    last_res = st.session_state.messages[-1]["content"]
    if "```" in last_res:
        st.download_button(label="💾 Изтегли кода", data=last_res, file_name="output.py", mime="text/plain") 
