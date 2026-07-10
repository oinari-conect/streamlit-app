import streamlit as st

st.title("TODOアプリ")

if 'todos' not in st.session_state:
    st.session_state.todos = []

col1, col2 = st.columns([4, 1])
with col1:
    task_input = st.text_input("タスク入力", key="task_input")
with col2:
    if st.button("追加"):
        if task_input.strip():
            st.session_state.todos.append(task_input)
            st.session_state.task_input = ""
            st.rerun()

if st.session_state.todos:
    st.subheader("タスク一覧")
    for i, todo in enumerate(st.session_state.todos):
        st.write(f"{i + 1}. {todo}")
