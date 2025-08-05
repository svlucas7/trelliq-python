# Deploy Instructions

## Streamlit Community Cloud (Easiest)

1. Push this repository to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub account
4. Select this repository
5. Choose main branch
6. Set app path: `app.py`
7. Click "Deploy"

Your app will be live at: `https://your-username-trelliq-python-app-main.streamlit.app`

## Railway

1. Go to [railway.app](https://railway.app)
2. Click "Start a New Project"
3. Connect GitHub repository
4. Railway will auto-detect Python and deploy
5. Custom domain available

## Heroku

1. Install Heroku CLI
2. Run commands:

```bash
heroku create your-app-name
git push heroku main
heroku open
```

## Environment Variables (Optional)

For any platform, you can set:
- `PYTHON_VERSION=3.9`
- `STREAMLIT_SERVER_PORT=8501`

All platforms support automatic Python detection and will use the files:
- `Procfile` (server configuration)
- `requirements.txt` (dependencies)
- `runtime.txt` (Python version)
- `.streamlit/config.toml` (Streamlit settings)
