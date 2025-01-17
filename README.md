# CSV文件分析系统

这是一个基于Streamlit开发的CSV文件分析系统，提供了文件上传、数据分析和可视化功能。

## 功能特点

- 用户认证系统
- 多文件上传支持
- 数据排序和搜索
- 数据可视化（柱状图、折线图、散点图）
- 响应式界面设计

## 安装要求

- Python 3.8+
- 依赖包列表见 `requirements.txt`

## 快速开始

1. 克隆仓库：
```bash
git clone [仓库地址]
cd streamlit_app
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 运行应用：
```bash
streamlit run app.py
```

## 用户指南

1. 登录系统
   - 默认用户名：admin
   - 默认密码：admin

2. 上传CSV文件
   - 支持单个或多个CSV文件
   - 最大文件大小：200MB

3. 数据分析
   - 数据排序
   - 关键字搜索
   - 数据可视化

## 项目结构

```
streamlit_app/
├── app.py          # 主应用程序
├── config.py       # 配置文件
├── users.py        # 用户认证模块
├── requirements.txt # 依赖包列表
└── README.md       # 项目说明文档
```

## 注意事项

- 首次使用请修改config.py中的默认用户名和密码
- 建议在虚拟环境中运行应用
- 确保上传的CSV文件格式正确 