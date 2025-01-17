import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from datetime import datetime
import shutil
from config import PAGE_TITLE, PAGE_ICON
from users import is_authenticated, show_login_page, logout, get_current_user

# 设置页面标题
st.set_page_config(page_title=PAGE_TITLE, page_icon=PAGE_ICON, layout="wide")

# 设置全局样式
st.markdown("""
    <style>
        .stTabs {
            position: sticky;
            top: 0;
            z-index: 999;
            background-color: white;
            padding: 10px 0;
        }
        .stTabs button {
            font-size: 1.2em !important;
            padding: 10px 20px !important;
        }
        .upload-section {
            position: fixed;
            bottom: 20px;
            right: 20px;
            z-index: 1000;
            background-color: white;
            padding: 10px;
            border-radius: 10px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .main-content {
            margin-top: 20px;
        }
    </style>
""", unsafe_allow_html=True)

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

def save_uploaded_file(uploaded_file):
    """保存上传的文件到data目录"""
    if not os.path.exists('data'):
        os.makedirs('data')
    
    # 生成唯一文件名
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{timestamp}_{uploaded_file.name}"
    filepath = os.path.join('data', filename)
    
    with open(filepath, 'wb') as f:
        f.write(uploaded_file.getbuffer())
    return filepath

def get_saved_files():
    """获取已保存的CSV文件列表"""
    if not os.path.exists('data'):
        return []
    return sorted([f for f in os.listdir('data') if f.endswith('.csv')], reverse=True)

def create_visualization(df, chart_type, x_axis, y_axis):
    """创建可视化图表"""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    if chart_type == "柱状图":
        # 如果数据点过多，只显示前20个
        if len(df) > 20:
            df = df.head(20)
        sns.barplot(data=df, x=x_axis, y=y_axis, ax=ax)
    elif chart_type == "折线图":
        sns.lineplot(data=df, x=x_axis, y=y_axis, ax=ax)
    elif chart_type == "散点图":
        sns.scatterplot(data=df, x=x_axis, y=y_axis, ax=ax)
    
    # 设置标签和样式
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    return fig

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
    
    # 创建固定在右下角的上传按钮
    with st.container():
        st.markdown('<div class="upload-section">', unsafe_allow_html=True)
        uploaded_file = st.file_uploader("上传新的CSV文件", type=["csv"])
        if uploaded_file:
            save_uploaded_file(uploaded_file)
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    # 获取所有保存的文件
    saved_files = get_saved_files()
    
    if saved_files:
        # 创建标签页
        tabs = st.tabs(saved_files)
        
        # 处理每个文件
        for idx, (tab, filename) in enumerate(zip(tabs, saved_files)):
            with tab:
                # 读取CSV文件
                filepath = os.path.join('data', filename)
                df = pd.read_csv(filepath)
                df = process_percentage(df)  # 处理百分比字段
                
                # 显示数据预览
                with st.expander("数据预览", expanded=True):
                    st.write(df.head())

                # 数据分析工具
                col1, col2 = st.columns(2)
                with col1:
                    # 排序功能
                    with st.expander("数据排序", expanded=True):
                        sort_column = st.selectbox(
                            "选择排序字段",
                            df.columns.tolist(),
                            key=f"sort_column_{idx}"
                        )
                        ascending = st.radio(
                            "排序顺序",
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
                            st.dataframe(display_df, use_container_width=True)

                with col2:
                    # 搜索功能
                    with st.expander("数据搜索", expanded=True):
                        search_query = st.text_input("输入搜索关键词", key=f"search_{idx}")
                        if search_query:
                            df_filtered = df[df.apply(lambda row: row.astype(str).str.contains(search_query).any(), axis=1)]
                            st.write(f"搜索结果（共 {len(df_filtered)} 条记录）：")
                            st.dataframe(df_filtered, use_container_width=True)
                
                # 数据可视化
                with st.expander("数据可视化", expanded=True):
                    viz_col1, viz_col2 = st.columns([1, 3])
                    with viz_col1:
                        chart_type = st.selectbox(
                            "选择图表类型",
                            ["柱状图", "折线图", "散点图"],
                            key=f"chart_type_{idx}"
                        )
                        
                        numeric_columns = df.select_dtypes(include=np.number).columns.tolist()
                        x_axis = st.selectbox("选择 X 轴", numeric_columns, key=f"x_axis_{idx}")
                        y_axis = st.selectbox("选择 Y 轴", numeric_columns, key=f"y_axis_{idx}")
                        
                    with viz_col2:
                        if x_axis and y_axis:
                            fig = create_visualization(df, chart_type, x_axis, y_axis)
                            st.pyplot(fig)

    else:
        st.info("暂无CSV文件，请点击右下角上传按钮添加文件")
