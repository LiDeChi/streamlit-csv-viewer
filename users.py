import streamlit as st
from config import USERS, SESSION_STATE_USER, SESSION_STATE_AUTHENTICATED

def login(username: str, password: str) -> bool:
    """
    验证用户登录
    """
    if username in USERS and USERS[username] == password:
        st.session_state[SESSION_STATE_USER] = username
        st.session_state[SESSION_STATE_AUTHENTICATED] = True
        return True
    return False

def logout():
    """
    用户登出
    """
    st.session_state[SESSION_STATE_USER] = None
    st.session_state[SESSION_STATE_AUTHENTICATED] = False

def is_authenticated() -> bool:
    """
    检查用户是否已认证
    """
    return st.session_state.get(SESSION_STATE_AUTHENTICATED, False)

def get_current_user() -> str:
    """
    获取当前登录用户
    """
    return st.session_state.get(SESSION_STATE_USER, None)

def show_login_page():
    """
    显示登录页面
    """
    st.title("登录")
    
    with st.form("login_form"):
        username = st.text_input("用户名")
        password = st.text_input("密码", type="password")
        submit = st.form_submit_button("登录")
        
        if submit:
            if login(username, password):
                st.success("登录成功！")
                st.experimental_rerun()
            else:
                st.error("用户名或密码错误！") 