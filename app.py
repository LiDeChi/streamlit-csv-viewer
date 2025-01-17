import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from config import PAGE_TITLE, PAGE_ICON
from users import is_authenticated, show_login_page, logout, get_current_user

# 设置页面标题
st.set_page_config(page_title=PAGE_TITLE, page_icon=PAGE_ICON, layout="wide")

# 检查用户是否已登录
if not is_authenticated():
    show_login_page()
else:
    # 显示顶部导航栏
    col1, col2, col3 = st.columns([1, 8, 1])
    with col1:
        st.write(f"欢迎, {get_current_user()}")
    with col3:
        if st.button("登出"):
            logout()
            st.experimental_rerun()
    
    # 主要应用内容
    st.title("CSV 文件分析系统")
    
    # 允许上传多个文件
    uploaded_files = st.file_uploader("上传 CSV 文件", type=["csv"], accept_multiple_files=True)

    # 如果有文件被上传
    if uploaded_files:
        for uploaded_file in uploaded_files:
            # 读取 CSV 文件
            df = pd.read_csv(uploaded_file)

            # 显示文件名
            st.subheader(f"查看文件：{uploaded_file.name}")
            
            # 显示数据框的一部分
            st.write(df.head())

            # 数据框的字段排序
            sort_column = st.selectbox("选择排序字段", df.columns.tolist())
            ascending = st.radio("选择排序顺序", ["升序", "降序"])
            df_sorted = df.sort_values(by=sort_column, ascending=True if ascending == "升序" else False)
            st.write(f"按 {sort_column} 排序后的数据：")
            st.write(df_sorted)

            # 搜索功能
            search_query = st.text_input("搜索数据")
            if search_query:
                # 使用字符串匹配进行过滤
                df_filtered = df[df.apply(lambda row: row.astype(str).str.contains(search_query).any(), axis=1)]
                st.write(f"搜索结果：")
                st.write(df_filtered)
            
            # 数据可视化部分
            st.subheader("数据可视化")
            
            # 选择要绘制的图形类型
            chart_type = st.selectbox("选择可视化类型", ["无", "柱状图", "折线图", "散点图"])
            
            if chart_type == "柱状图":
                numeric_columns = df.select_dtypes(include=np.number).columns.tolist()
                x_axis = st.selectbox("选择 X 轴", numeric_columns)
                y_axis = st.selectbox("选择 Y 轴", numeric_columns)
                fig, ax = plt.subplots()
                ax.bar(df[x_axis], df[y_axis])
                ax.set_xlabel(x_axis)
                ax.set_ylabel(y_axis)
                st.pyplot(fig)

            elif chart_type == "折线图":
                numeric_columns = df.select_dtypes(include=np.number).columns.tolist()
                x_axis = st.selectbox("选择 X 轴", numeric_columns)
                y_axis = st.selectbox("选择 Y 轴", numeric_columns)
                fig, ax = plt.subplots()
                ax.plot(df[x_axis], df[y_axis])
                ax.set_xlabel(x_axis)
                ax.set_ylabel(y_axis)
                st.pyplot(fig)
            
            elif chart_type == "散点图":
                numeric_columns = df.select_dtypes(include=np.number).columns.tolist()
                x_axis = st.selectbox("选择 X 轴", numeric_columns)
                y_axis = st.selectbox("选择 Y 轴", numeric_columns)
                fig, ax = plt.subplots()
                ax.scatter(df[x_axis], df[y_axis])
                ax.set_xlabel(x_axis)
                ax.set_ylabel(y_axis)
                st.pyplot(fig)

    else:
        st.info("请上传至少一个 CSV 文件")
