import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from config import PAGE_TITLE, PAGE_ICON
from users import is_authenticated, show_login_page, logout, get_current_user

# 设置页面标题
st.set_page_config(page_title=PAGE_TITLE, page_icon=PAGE_ICON, layout="wide")

def process_percentage(df):
    """处理百分比字段，转换为数值类型"""
    for col in df.columns:
        if df[col].dtype == 'object':
            # 检查是否为百分比格式
            if df[col].str.contains('%').any():
                df[col] = df[col].str.rstrip('%').astype('float') / 100
    return df

def format_percentage(value):
    """将数值格式化为百分比显示"""
    if isinstance(value, (int, float)):
        return f"{value:.2%}"
    return value

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
            st.rerun()
    
    # 主要应用内容
    st.title("CSV 文件分析系统")
    
    # 允许上传多个文件
    uploaded_files = st.file_uploader("上传 CSV 文件", type=["csv"], accept_multiple_files=True)

    # 如果有文件被上传，创建文件标签页
    if uploaded_files:
        # 创建标签页
        file_names = [file.name for file in uploaded_files]
        selected_file = st.tabs(file_names)
        
        # 处理每个文件
        for idx, (tab, file) in enumerate(zip(selected_file, uploaded_files)):
            with tab:
                # 读取 CSV 文件
                df = pd.read_csv(file)
                df = process_percentage(df)  # 处理百分比字段
                
                # 显示数据框的一部分
                st.write("数据预览：")
                st.write(df.head())

                # 数据框的字段排序
                col1, col2 = st.columns(2)
                with col1:
                    sort_column = st.selectbox(
                        "选择排序字段",
                        df.columns.tolist(),
                        key=f"sort_column_{idx}"
                    )
                with col2:
                    ascending = st.radio(
                        "选择排序顺序",
                        ["升序", "降序"],
                        key=f"sort_order_{idx}"
                    )
                
                if sort_column:
                    df_sorted = df.sort_values(
                        by=sort_column,
                        ascending=True if ascending == "升序" else False
                    )
                    # 恢复百分比显示格式
                    display_df = df_sorted.copy()
                    for col in display_df.columns:
                        if display_df[col].dtype in ['float64', 'float32']:
                            if display_df[col].between(0, 1).all():
                                display_df[col] = display_df[col].apply(format_percentage)
                    
                    st.write(f"按 {sort_column} {ascending}排序后的数据：")
                    st.write(display_df)

                # 搜索功能
                search_query = st.text_input("搜索数据", key=f"search_{idx}")
                if search_query:
                    # 使用字符串匹配进行过滤
                    df_filtered = df[df.apply(lambda row: row.astype(str).str.contains(search_query).any(), axis=1)]
                    st.write(f"搜索结果：")
                    st.write(df_filtered)
                
                # 数据可视化部分
                st.subheader("数据可视化")
                
                # 选择要绘制的图形类型
                chart_type = st.selectbox(
                    "选择可视化类型",
                    ["无", "柱状图", "折线图", "散点图"],
                    key=f"chart_type_{idx}"
                )
                
                if chart_type != "无":
                    numeric_columns = df.select_dtypes(include=np.number).columns.tolist()
                    x_axis = st.selectbox("选择 X 轴", numeric_columns, key=f"x_axis_{idx}")
                    y_axis = st.selectbox("选择 Y 轴", numeric_columns, key=f"y_axis_{idx}")
                    
                    fig, ax = plt.subplots()
                    
                    if chart_type == "柱状图":
                        ax.bar(df[x_axis], df[y_axis])
                    elif chart_type == "折线图":
                        ax.plot(df[x_axis], df[y_axis])
                    elif chart_type == "散点图":
                        ax.scatter(df[x_axis], df[y_axis])
                    
                    ax.set_xlabel(x_axis)
                    ax.set_ylabel(y_axis)
                    st.pyplot(fig)

    else:
        st.info("请上传至少一个 CSV 文件")
