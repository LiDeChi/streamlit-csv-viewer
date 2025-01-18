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
        /* 删除按钮样式 */
        div[data-testid="stButton"] button[kind="secondary"] {
            background: none;
            border: none;
            color: #ff4b4b;
            padding: 0;
            opacity: 0.6;
            transition: opacity 0.3s;
        }
        div[data-testid="stButton"] button[kind="secondary"]:hover {
            background: none;
            opacity: 1;
        }
        .file-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1rem;
        }
        .file-header h3 {
            margin: 0;
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

def save_uploaded_files(files):
    """保存上传的多个文件到data目录"""
    if not os.path.exists('data'):
        os.makedirs('data')
    
    saved_files = []
    for file in files:
        if file.name.endswith('.csv'):
            filename = file.name
            filepath = os.path.join('data', filename)
            with open(filepath, 'wb') as f:
                f.write(file.getbuffer())
            saved_files.append(filename)
    
    return saved_files

def get_saved_files():
    """获取已保存的CSV文件列表"""
    if not os.path.exists('data'):
        return []
    # 按文件名排序
    return sorted([f for f in os.listdir('data') if f.endswith('.csv')])

def get_numeric_columns(df):
    """获取数值类型的列"""
    return df.select_dtypes(include=[np.number]).columns.tolist()

def get_categorical_columns(df):
    """获取分类类型的列"""
    return df.select_dtypes(exclude=[np.number]).columns.tolist()

def calculate_statistics(df, group_by_col, value_col, agg_funcs):
    """计算统计指标"""
    if not group_by_col or not value_col:
        return None
    
    agg_dict = {
        '计数': 'count',
        '求和': 'sum',
        '平均值': 'mean',
        '最大值': 'max',
        '最小值': 'min',
        '中位数': 'median',
        '标准差': 'std'
    }
    
    selected_aggs = {value_col: [agg_dict[func] for func in agg_funcs]}
    result = df.groupby(group_by_col).agg(selected_aggs)
    result.columns = result.columns.droplevel(0)  # 删除多级索引
    return result

def create_visualization(df, chart_type, x_axis, y_axis):
    """创建可视化图表"""
    # 设置中文字体
    plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans', 'Arial Unicode MS']
    plt.rcParams['axes.unicode_minus'] = False
    
    # 确保数据是可视化的格式
    df = df.copy()
    if df[y_axis].dtype == 'object':
        try:
            df[y_axis] = pd.to_numeric(df[y_axis], errors='coerce')
        except:
            st.error(f"无法将 {y_axis} 列转换为数值类型")
            return None
    
    # 创建图表
    fig, ax = plt.subplots(figsize=(12, 6))
    
    try:
        if chart_type == "柱状图":
            # 如果数据点过多，只显示前20个
            if len(df) > 20:
                df = df.head(20)
            sns.barplot(data=df, x=x_axis, y=y_axis, ax=ax, ci=None)
        elif chart_type == "折线图":
            sns.lineplot(data=df, x=x_axis, y=y_axis, ax=ax, ci=None)
        elif chart_type == "散点图":
            sns.scatterplot(data=df, x=x_axis, y=y_axis, ax=ax)
        elif chart_type == "箱线图":
            sns.boxplot(data=df, x=x_axis, y=y_axis, ax=ax)
        elif chart_type == "小提琴图":
            sns.violinplot(data=df, x=x_axis, y=y_axis, ax=ax)
        
        # 设置标签和样式
        plt.xticks(rotation=45, ha='right', fontsize=10)
        plt.yticks(fontsize=10)
        ax.set_xlabel(x_axis, fontsize=12)
        ax.set_ylabel(y_axis, fontsize=12)
        ax.set_title(f"{chart_type}: {x_axis} vs {y_axis}", fontsize=14, pad=20)
        
        # 调整布局
        plt.tight_layout()
        return fig
    except Exception as e:
        st.error(f"创建图表时出错: {str(e)}")
        return None

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
    # 暂时注释掉登出功能
    # with col3:
    #     if st.button("登出"):
    #         logout()
    #         st.rerun()
    
    # 主要应用内容
    st.title("CSV 文件分析系统")
    
    # 创建固定在右下角的上传按钮
    with st.container():
        st.markdown('<div class="upload-section">', unsafe_allow_html=True)
        uploaded_files = st.file_uploader("上传CSV文件", type=["csv"], accept_multiple_files=True)
        if uploaded_files:
            saved_files = save_uploaded_files(uploaded_files)
            if saved_files:
                st.success(f"成功上传 {len(saved_files)} 个CSV文件")
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
                # 创建文件标题和删除按钮的容器
                st.markdown('<div class="file-header">', unsafe_allow_html=True)
                st.write("### 数据预览")
                if st.button("🗑️", key=f"delete_{idx}", help="删除此文件", type="secondary"):
                    if delete_file(filename):
                        st.success(f"文件 {filename} 已删除")
                        st.rerun()
                    else:
                        st.error("删除文件失败")
                st.markdown('</div>', unsafe_allow_html=True)
                
                # 读取CSV文件
                filepath = os.path.join('data', filename)
                df = pd.read_csv(filepath)
                df = process_percentage(df)  # 处理百分比字段
                
                # 显示数据表格
                st.dataframe(df, use_container_width=True, height=400)

                # 数据统计分析
                st.write("### 数据统计")
                stat_col1, stat_col2 = st.columns(2)
                
                with stat_col1:
                    group_by_col = st.selectbox(
                        "选择分组字段",
                        get_categorical_columns(df),
                        key=f"group_{idx}"
                    )
                    value_col = st.selectbox(
                        "选择统计字段",
                        get_numeric_columns(df),
                        key=f"value_{idx}"
                    )
                
                with stat_col2:
                    agg_funcs = st.multiselect(
                        "选择统计指标",
                        ['计数', '求和', '平均值', '最大值', '最小值', '中位数', '标准差'],
                        default=['计数', '平均值'],
                        key=f"agg_{idx}"
                    )
                
                if group_by_col and value_col and agg_funcs:
                    stats_df = calculate_statistics(df, group_by_col, value_col, agg_funcs)
                    if stats_df is not None:
                        st.write("统计结果：")
                        st.dataframe(stats_df, use_container_width=True)
                        
                        # 可视化统计结果
                        st.write("### 统计可视化")
                        viz_col1, viz_col2 = st.columns([1, 3])
                        with viz_col1:
                            chart_type = st.selectbox(
                                "选择图表类型",
                                ["柱状图", "折线图", "散点图", "箱线图", "小提琴图"],
                                key=f"chart_type_{idx}"
                            )
                            
                            # 对于统计结果的可视化
                            if len(agg_funcs) == 1:
                                # 单个统计指标时直接可视化
                                fig = create_visualization(
                                    stats_df.reset_index(),
                                    chart_type,
                                    group_by_col,
                                    agg_funcs[0]
                                )
                                with viz_col2:
                                    st.pyplot(fig)
                            else:
                                # 多个统计指标时，让用户选择要可视化的指标
                                selected_metric = st.selectbox(
                                    "选择要可视化的指标",
                                    agg_funcs,
                                    key=f"metric_{idx}"
                                )
                                fig = create_visualization(
                                    stats_df.reset_index(),
                                    chart_type,
                                    group_by_col,
                                    selected_metric
                                )
                                with viz_col2:
                                    st.pyplot(fig)

                # 搜索功能
                st.write("### 数据搜索")
                search_query = st.text_input("输入搜索关键词", key=f"search_{idx}")
                if search_query:
                    df_filtered = df[df.apply(lambda row: row.astype(str).str.contains(search_query).any(), axis=1)]
                    st.write(f"搜索结果（共 {len(df_filtered)} 条记录）：")
                    st.dataframe(df_filtered, use_container_width=True)

    else:
        st.info("暂无CSV文件，请点击右下角上传按钮添加文件")
