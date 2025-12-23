这是一份为您准备的 `README.md` 文件，采用专业且具有吸引力的格式，适合放在 GitHub 或项目主页上。

---

# 💸 花光大佬的钱 | Spend Billions

一个基于 Streamlit 开发的摸鱼神级小游戏。在这里，你可以化身世界顶级富豪（马云、马化腾或马斯克），体验在巨额财富面前“身无分文”是多么困难的一件事！

## ✨ 核心特性

* **多角色切换**：内置“二马一马（马云、马化腾、马斯克）”三位顶级富豪，每位角色拥有专属的起始资金、货币单位和商品库。
* **沉浸式体验**：
* **马云**：买榨菜、清空购物车，甚至重组蚂蚁金服。
* **马化腾**：买表情包、充绿钻，甚至收购 Epic Games。
* **马斯克**：买狗狗币、发射猎鹰 9 号，甚至殖民火星。


* **动态账单生成**：根据角色风格，自动生成微信支付、支付宝或 PayPal 风格的购物账单。
* **智能双语系统**：自动检测浏览器语言（支持中/英），并提供手动切换开关。
* **访客统计**：基于 SQLite 实现简单的 UV（独立访客）和 PV（页面浏览量）统计。
* **响应式设计**：完美适配 PC 端和手机端，支持生成分享海报和朋友圈文案。

## 🛠️ 技术栈

* **前端框架**: [Streamlit](https://streamlit.io/)
* **数据持久化**: SQLite (用于流量统计)
* **样式定制**: HTML + CSS (注入 Streamlit 容器)
* **图标**: Emoji + Dicebear Avatars

## 🚀 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/your-username/spend-billions.git
cd spend-billions

```

### 2. 安装依赖

```bash
pip install streamlit

```

### 3. 运行应用

```bash
streamlit run app.py

```

## 📂 项目结构

```text
├── app.py              # 主程序代码
├── data/               # (可选) 存放静态资源
└── visit_stats.db      # 运行后自动生成的访客数据库

```

## 🧩 核心代码说明

### 访客统计逻辑

程序通过 `st.session_state` 结合 `uuid` 识别唯一访客，并将数据持久化在本地 SQLite 数据库中。

### 购物逻辑

使用字典映射（Map）来管理不同角色的资产和商品单价，通过 `st.session_state.cart` 实时计算余额。

## 🤝 贡献建议

欢迎通过 Pull Request 提供更多离谱的商品创意或角色建议！

1. 提交前请确保代码遵循 PEP 8 规范。
2. 新增商品请同步修改 `CHARACTERS` 字典中的 `name_zh` 和 `name_en`。

## ☕ 投喂作者

如果你觉得这个小游戏让你的摸鱼时光更快乐了，欢迎点击页面底部的“请开发者喝咖啡”按钮进行打赏。支持微信、支付宝及 PayPal。

## 📜 许可证

本项目采用 [MIT License](https://www.google.com/search?q=LICENSE) 开源。

---

**注意**：本项目仅供娱乐和学习 Streamlit 交互设计使用，所有数据均为模拟。
