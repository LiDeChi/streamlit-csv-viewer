import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from datetime import datetime
from config import PAGE_TITLE, PAGE_ICON
from users import is_authenticated, show_login_page, logout, get_current_user

# 设置matplotlib中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

# 设置Seaborn样式
sns.set_style("whitegrid")
sns.set_context("notebook", font_scale=1.2)

# 设置页面标题
st.set_page_config(page_title=PAGE_TITLE, page_icon=PAGE_ICON, layout="wide")

# 设置全局样式
st.markdown("""
    <style>
        div[data-testid="stVerticalBlock"] div[data-testid="stHorizontalBlock"] {
            position: sticky;
            top: 0;
            background-color: white;
            z-index: 999;
            padding: 1rem 0;
            border-bottom: 1px solid #f0f0f0;
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
        .stDataFrame {
            margin-top: 1rem;
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
    
    # 直接使用原始文件名
    filename = uploaded_file.name
    filepath = os.path.join('data', filename)
    
    # 如果文件已存在，直接覆盖
    with open(filepath, 'wb') as f:
        f.write(uploaded_file.getbuffer())
    return filepath

def get_saved_files():
    """获取已保存的CSV文件列表"""
    if not os.path.exists('data'):
        return []
    # 按文件名排序，不再按时间戳排序
    return sorted([f for f in os.listdir('data') if f.endswith('.csv')])

def create_visualization(df, chart_type, x_axis, y_axis):
    """创建可视化图表"""
    # 设置中文字体
    plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans', 'Arial Unicode MS']
    plt.rcParams['axes.unicode_minus'] = False
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
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
    plt.xticks(rotation=45, ha='right', fontsize=10)
    plt.yticks(fontsize=10)
    ax.set_xlabel(x_axis, fontsize=12)
    ax.set_ylabel(y_axis, fontsize=12)
    ax.set_title(f"{chart_type}: {x_axis} vs {y_axis}", fontsize=14, pad=20)
    
    # 调整布局
    plt.tight_layout()
    return fig

def delete_file(filename):
    """删除指定的文件"""
    filepath = os.path.join('data', filename)
    if os.path.exists(filepath):
        os.remove(filepath)
        return True
    return False

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
                # 添加删除按钮
                col1, col2 = st.columns([6, 1])
                with col2:
                    if st.button("🗑️ 删除文件", key=f"delete_{idx}", type="primary"):
                        if delete_file(filename):
                            st.success(f"文件 {filename} 已删除")
                            st.rerun()
                        else:
                            st.error("删除文件失败")
                
                # 读取CSV文件
                filepath = os.path.join('data', filename)
                df = pd.read_csv(filepath)
                df = process_percentage(df)  # 处理百分比字段
                
                # 显示数据预览
                st.write("### 数据预览")
                st.dataframe(df, use_container_width=True, height=400)

                # 搜索功能
                st.write("### 数据搜索")
                search_query = st.text_input("输入搜索关键词", key=f"search_{idx}")
                if search_query:
                    df_filtered = df[df.apply(lambda row: row.astype(str).str.contains(search_query).any(), axis=1)]
                    st.write(f"搜索结果（共 {len(df_filtered)} 条记录）：")
                    st.dataframe(df_filtered, use_container_width=True)
                
                # 数据可视化
                st.write("### 数据可视化")
                viz_col1, viz_col2 = st.columns([1, 3])
                with viz_col1:
                    chart_type = st.selectbox(
                        "选择图表类型",
                        ["柱状图", "折线图", "散点图"],
                        key=f"chart_type_{idx}"
                    )
                    
                    # 获取所有列作为可选项
                    all_columns = df.columns.tolist()
                    x_axis = st.selectbox("选择 X 轴", all_columns, key=f"x_axis_{idx}")
                    y_axis = st.selectbox("选择 Y 轴", all_columns, key=f"y_axis_{idx}")
                    
                with viz_col2:
                    if x_axis and y_axis:
                        fig = create_visualization(df, chart_type, x_axis, y_axis)
                        st.pyplot(fig)

    else:
        st.info("暂无CSV文件，请点击右下角上传按钮添加文件")
