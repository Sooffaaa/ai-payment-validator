import streamlit as st
from services.ai_service import AIService

st.set_page_config(page_title="AI Financial Parser", page_icon="💳")

st.title("💳 AI Financial Parser")

ai_service = AIService()

user_input = st.text_area("Введите текст:")

if st.button("Распознать"):
    if not user_input.strip():
        st.warning("Введите текст")
    else:
        try:
            data = ai_service.extract_payment_data(user_input)
            st.success("Данные успешно обработаны")
            st.json(data)
        except Exception as e:
            st.error("Ошибка при обработке")
            st.code(str(e))