# Shanghai Weather RSS Feed 🌦️

[![Update Weather RSS](https://github.com/liusonwood/github-rss-weather/actions/workflows/weather.yml/badge.svg)](https://github.com/liusonwood/github-rss-weather/actions/workflows/weather.yml)
[![Python Version](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![API Powered By](https://img.shields.io/badge/API-QWeather-orange.svg)](https://dev.qweather.com/)

基于 GitHub Actions 与和风天气（QWeather）API 实现的上海每日天气预报 RSS 订阅源生成器。每日自动运行、增量更新，为您提供最及时、详尽的天气数据。

---

## 📖 目录

- [💡 工作原理](#-工作原理)
- [📡 订阅源地址](#-订阅源地址)
- [✨ 订阅展示预览](#-订阅展示预览)
- [📁 项目结构](#-项目结构)
- [🛠️ 部署与配置指南](#️-部署与配置指南)
  - [第一步：获取和风天气 API Key](#第一步获取和风天气-api-key)
  - [第二步：配置 GitHub Secrets](#第二步配置-github-secrets)
  - [第三步：开启 Workflow 写入权限](#第三步开启-workflow-写入权限)
- [🖥️ 本地调试与开发](#️-本地调试与开发)
- [📄 开源协议](#-开源协议)

---

## 💡 工作原理

本项目通过极其轻量化的无服务器（Serverless）架构实现自动运行：

1. **定时触发 (Daily Trigger)**：每日 **23:00 UTC**（北京时间早上 07:00），GitHub Actions 自动运行工作流。
2. **拉取数据 (Fetch Data)**：运行 Python 脚本请求和风天气 API，获取上海明天的最新天气数据。
3. **更新订阅 (Generate RSS)**：解析并格式化天气指标，**增量追加**到 `weather.xml` 文件中，保留历史天气记录。
4. **自动提交 (Auto-Commit)**：工作流自动将更新后的 `weather.xml` 提交并推送到 GitHub 仓库。

---

## 📡 订阅源地址

复制下方的 **Raw URL** 粘贴至您喜爱的 RSS 阅读器（如 NetNewsWire, Feedbin, Reeder 等）即可完成订阅：

```text
https://raw.githubusercontent.com/liusonwood/rssqweather/main/weather.xml
```

> [!NOTE]
> 请注意，实际的 XML 订阅源地址取决于您自己的 GitHub 用户名和仓库名。如果您 Fork 了本项目，请将上述链接中的 `liusonwood` 和 `rssqweather` 替换为您自己的用户名和仓库名称。

---

## ✨ 订阅展示预览

生成的 RSS 会将每天的天气封装为一个独立的 `item`，包含了多维度的精细化气象指标：

### 📝 RSS XML 结构示例

```xml
<item>
  <title>2026-05-21: Sunny, 18°C - 26°C</title>
  <link>https://github.com/liusonwood/github-rss-weather#2026-05-21</link>
  <description>
    <![CDATA[
      <strong>Condition (Day):</strong> Sunny (Icon: 100)<br/>
      <strong>Condition (Night):</strong> Clear (Icon: 150)<br/>
      <strong>Temperature:</strong> 18°C to 26°C<br/>
      <strong>Precipitation:</strong> 0.0 mm<br/>
      <strong>Cloud Cover:</strong> 10%<br/><br/>
      <strong>Wind (Day):</strong> Northeast (45°), Scale 3-4, Speed 15 km/h<br/>
      <strong>Wind (Night):</strong> Northeast (45°), Scale 3, Speed 12 km/h<br/><br/>
      <strong>Humidity:</strong> 55%<br/>
      <strong>Visibility:</strong> 15 km<br/>
      <strong>Sun:</strong> Rise 04:55, Set 18:45<br/>
      <strong>Moon:</strong> Rise 09:20, Set 23:40 (Phase: Waxing Crescent, 801)<br/>
      <strong>UV Index:</strong> 8
    ]]>
  </description>
  <guid isPermaLink="false">shanghai-weather-2026-05-21</guid>
  <pubDate>Thu, 21 May 2026 23:00:00 GMT</pubDate>
</item>
```

---

## 📁 项目结构

```text
.
├── .github/
│   └── workflows/
│       └── weather.yml       # GitHub Actions 自动化工作流定义
├── GEMINI.md                 # 项目上下文与约束定义
├── README.md                 # 项目自述文件（本文件）
├── fetch_weather.py          # 核心 Python 脚本 (请求 API、解析数据、组装 XML)
├── requirements.txt          # Python 依赖声明 (requests)
└── weather.xml               # 生成的增量天气 RSS Feed (主订阅产物)
```

---

## 🛠️ 部署与配置指南

### 第一步：获取和风天气 API Key

1. 登录 [和风天气开发者控制台](https://console.qweather.com/)。
2. 创建一个项目（选择 **免费订阅** 或 **标准订阅**）。
3. 在项目中创建凭证（KEY），获取 **API Key**（通常为一串 32 位的字母与数字）。
4. 在控制台查看您的 **API 主机地址 (API Host)**（如 `devapi.qweather.com` 或特殊的专用域名）。

> [!IMPORTANT]
> 免费订阅的 API Host 通常为 `devapi.qweather.com`，付费订阅一般为 `api.qweather.com`。请务必根据和风天气后台的实际提示进行配置。

### 第二步：配置 GitHub Secrets

为了让 GitHub Actions 能够安全地请求和风天气 API，您需要将相关凭证保存到仓库的 Secrets 中：

1. 打开您的 GitHub 仓库页面。
2. 导航至 **Settings** > **Secrets and variables** > **Actions**。
3. 点击 **New repository secret** 分别添加以下两个 Secret：
   * **Name**: `QWEATHER_KEY` | **Value**: 您的 API Key
   * **Name**: `QWEATHER_HOST` | **Value**: 您的 API 主机地址 (e.g. `devapi.qweather.com`，**注意：不需要带协议头 `https://`**)
4. 保存配置。

### 第三步：开启 Workflow 写入权限

因为 GitHub Actions 需要在运行完毕后将更新的 `weather.xml` 文件推送回仓库，所以必须授予其写权限：

1. 进入仓库的 **Settings** > **Actions** > **General**。
2. 滚动页面至底部找到 **Workflow permissions**。
3. 选择 **Read and write permissions**（读写权限）。
4. 勾选 **Allow GitHub Actions to create and approve pull requests**（可选，推荐）。
5. 点击 **Save** 保存。

---

## 🖥️ 本地调试与开发

若想在本地调试 Python 脚本或手动更新天气数据，请执行以下命令：

```bash
# 1. 克隆仓库
git clone https://github.com/liusonwood/github-rss-weather.git
cd github-rss-weather

# 2. 安装必要依赖
pip install -r requirements.txt

# 3. 设置本地环境变量
export QWEATHER_KEY="你的和风天气API-Key"
export QWEATHER_HOST="devapi.qweather.com" # 或您的专属 Host

# 4. 执行脚本
python fetch_weather.py
```

执行成功后，您会在项目根目录下看到全新生成或已追加最新数据的 `weather.xml` 文件。

---

## 📄 开源协议

本项目采用 [MIT License](LICENSE) 协议开源。
