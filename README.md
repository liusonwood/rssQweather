# Shanghai Weather RSS Feed 🌦️

Automated weather forecast for Shanghai, generated daily via GitHub Actions and the QWeather (和风天气) API.

## 🚀 How it Works
1.  **Daily Trigger**: A GitHub Action runs every day at 20:00 UTC.
2.  **Fetch Data**: A Python script calls the QWeather API for tomorrow's forecast in Shanghai.
3.  **Generate RSS**: The script updates `weather.xml` with the latest forecast data.
4.  **Auto-Commit**: The updated XML is pushed back to this repository.

## 📡 Subscribe to the Feed
You can subscribe to this weather feed using your favorite RSS reader by using the **Raw URL** of the `weather.xml` file:

`https://raw.githubusercontent.com/<YOUR_USERNAME>/<YOUR_REPO_NAME>/main/weather.xml`

## 🛠️ Setup Instructions

### 1. Get a QWeather API Key
- Sign up at [QWeather Developer Console](https://console.qweather.com/).
- Create a "Standard Edition" or "Free Edition" project.
- Obtain your **API Key**.

### 2. Configure GitHub Secrets
To allow the automation to run, you must add your API key and Host to GitHub:
1.  Go to your repository on GitHub.
2.  Navigate to **Settings** > **Secrets and variables** > **Actions**.
3.  Click **New repository secret** for each of the following:
    *   **Name**: `QWEATHER_KEY` | **Value**: Your API Key.
    *   **Name**: `QWEATHER_HOST` | **Value**: Your API Host (e.g., `xxx.re.qweatherapi.com`).
4.  Click **Add secret**.

### 3. Workflow Permissions
Ensure the GitHub Actions bot has permission to write to your repository:
1.  Go to **Settings** > **Actions** > **General**.
2.  Scroll down to **Workflow permissions**.
3.  Select **Read and write permissions**.
4.  Check **Allow GitHub Actions to create and approve pull requests** (optional but recommended).
5.  Click **Save**.

## 🖥️ Local Development
If you want to run the script locally:

```bash
# Install dependencies
pip install -r requirements.txt

# Set your credentials
export QWEATHER_KEY="your_api_key_here"
export QWEATHER_HOST="xxx.re.qweatherapi.com"

# Run the script
python fetch_weather.py
```

## 📄 License
MIT
