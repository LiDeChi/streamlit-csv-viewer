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
    # 设置登录页面样式
    st.markdown("""
        <style>
            .login-container {
                max-width: 200px;
                margin: 0 auto;
                padding: 0.5rem;
                margin-top: 2rem;
            }
            .login-title {
                text-align: center;
                margin-bottom: 1rem;
                color: #262730;
                font-size: 1.2rem;
            }
            .stButton > button {
                width: 100%;
                margin-top: 0.5rem;
            }
            div[data-testid="stForm"] {
                background-color: white;
                padding: 1rem;
                border-radius: 6px;
                box-shadow: 0 2px 6px rgba(0,0,0,0.05);
            }
            div[data-testid="stForm"] > div[data-testid="column"] {
                padding: 0.3rem 0;
            }
            div[data-testid="stTextInput"] input {
                font-size: 0.9rem;
            }
            div.row-widget.stButton {
                width: 100px;
                margin: 0 auto;
            }
        </style>
    """, unsafe_allow_html=True)
    
    # 创建七列布局，中间列放置登录框
    col1, col2, col3, col4, col5, col6, col7 = st.columns([3, 2, 1, 1, 1, 2, 3])
    
    with col4:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.markdown('<h1 class="login-title">登录</h1>', unsafe_allow_html=True)
        
        with st.form("login_form"):
            username = st.text_input("用户名", label_visibility="collapsed", placeholder="用户名")
            password = st.text_input("密码", type="password", label_visibility="collapsed", placeholder="密码")
            submit = st.form_submit_button("登录")
            
            if submit:
                if login(username, password):
                    st.success("登录成功！")
                    st.rerun()
                else:
                    st.error("用户名或密码错误！")
        
        st.markdown('</div>', unsafe_allow_html=True) 