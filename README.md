# Zenyth

Zenyth is an AI-powered application that extracts, transcribes, summarizes, and translates YouTube video content. It provides a simple web interface where users can input a YouTube URL and receive a concise, well-structured summary of the video's content in their preferred language.

![Workflow](agent_workflow.png)

## Features

- **YouTube Transcript Extraction**: Automatically extracts transcripts from YouTube videos
- **AI-Powered Summarization**: Generates concise, structured summaries of video content
- **Multi-Language Support**: Translates summaries into various languages
- **Proxy-Based Solution**: Uses Webshare proxy to bypass YouTube API limitations
- **Responsive Web Interface**: Clean, user-friendly interface for submitting URLs and viewing results

## Architecture Overview

Zenyth consists of the following components:

- **Frontend**: Next.js application with a responsive UI
- **Backend**: FastAPI server with LangChain/LangGraph for orchestrating the AI workflow
- **AI Components**: Uses OpenRouter API to access deepseek models for summarization and translation
- **Proxy System**: Webshare rotating residential proxy to avoid IP blocking
- **Reverse Proxy**: Nginx for routing traffic and SSL termination

### Workflow Diagram

```mermaid
graph TD
    A[User] -->|Submits YouTube URL| B[Frontend]
    B -->|API Request| C[Backend]
    C -->|1. Extract Video ID| D[YouTube ID Extraction]
    D -->|2. Fetch Transcript| E[Transcript Retrieval]
    E -->|Via Webshare Proxy| F[YouTube API]
    F -->|Raw Transcript| E
    E -->|3. Process Text| G[Summarization]
    G -->|Via OpenRouter| H[LLM - deepseek]
    H -->|Raw Summary| G
    G -->|4. Translate| I[Translation]
    I -->|Via OpenRouter| J[LLM - deepseek]
    J -->|Translated Summary| I
    I -->|Final Result| C
    C -->|Response| B
    B -->|Display Results| A
```

## Prerequisites

- Docker & Docker Compose
- A domain name pointing to your server
- A Webshare account with a "Rotating Residential Proxy" plan
- OpenRouter API key(s)
- Python 3.9+ (for local development)

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd zenyth
```

### 2. Configure Environment Variables

Create a `.env` file in the backend directory:

```bash
cp backend/.env.example backend/.env
```

Edit the `.env` file and add your credentials:

```
# Webshare Proxy Configuration
WEBSHARE_PROXY_USERNAME=your_username
WEBSHARE_PROXY_PASSWORD=your_password

# OpenRouter API Keys (comma-separated for rotation)
OPENROUTER_API_KEYS=key1,key2,key3

# LangSmith Tracing (optional)
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langchain_api_key
LANGCHAIN_PROJECT=zenyth

# Site Information
YOUR_SITE_URL=https://your-domain.com
YOUR_SITE_NAME=Zenyth
```

### 3. Configure Nginx as Reverse Proxy

Create a virtual host configuration in `/etc/nginx/sites-available/`:

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;
    
    # SSL Configuration
    ssl_certificate /path/to/fullchain.pem;
    ssl_certificate_key /path/to/privkey.pem;
    
    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable the configuration and reload Nginx:

```bash
ln -s /etc/nginx/sites-available/your-domain.com /etc/nginx/sites-enabled/
systemctl reload nginx
```

### 4. Launch Services

Start the application using Docker Compose:

```bash
docker compose up -d --build
```

## Usage Guide

### Accessing the Web Interface

Open your browser and navigate to your domain (e.g., `https://your-domain.com`).

### Submitting a YouTube URL

1. Paste a YouTube video URL in the input field
2. Select your preferred language for the summary (default is English)
3. Click "Generate Summary"
4. Wait for the processing to complete (this may take a few moments depending on the video length)

### Understanding the Results

The results will be displayed in two collapsible sections:

- **Video Summary**: A concise, structured summary of the video content
- **Transcript**: The full transcript of the video (expandable)

## Troubleshooting

### Common Issues

#### 502 Bad Gateway

- Verify that the backend service is running (`docker compose ps`)
- Check backend logs for errors (`docker compose logs backend`)

#### RequestBlocked or IpBlocked Errors

This means the proxy IP is blacklisted by YouTube.

- Try increasing the number of retries in the configuration
- Change your Webshare proxy pool
- Contact Webshare support to obtain a "YouTube Unblocker" pool

#### 407 Proxy Authentication Required

- Verify your Webshare credentials in the `.env` file

#### No Traffic in Webshare Dashboard

- Check the proxy configuration in the code and in the `.env` file

### Testing the Proxy Manually

You can test the proxy configuration with this command:

```bash
docker compose exec -T backend python - << 'PY'
import os, requests
proxies = {
    "http":  f"http://{os.getenv('WEBSHARE_PROXY_USERNAME')}-rotate:{os.getenv('WEBSHARE_PROXY_PASSWORD')}@p.webshare.io:80",
    "https": f"http://{os.getenv('WEBSHARE_PROXY_USERNAME')}-rotate:{os.getenv('WEBSHARE_PROXY_PASSWORD')}@p.webshare.io:80",
}
r = requests.get("https://httpbin.org/ip", proxies=proxies, timeout=10)
print(r.text)
PY
```

## Development Guide

### Local Setup

1. Clone the repository
2. Install backend dependencies:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```
3. Install frontend dependencies:
   ```bash
   cd frontend
   npm install
   ```
4. Create and configure the `.env` file
5. Start the backend:
   ```bash
   cd backend
   uvicorn api:app --reload
   ```
6. Start the frontend:
   ```bash
   cd frontend
   npm run dev
   ```

### Project Structure

- `backend/`: FastAPI backend
  - `api.py`: API endpoints
  - `agent.py`: LangGraph workflow
  - `tools.py`: Tool definitions
  - `config.py`: Configuration
  - `src/`: Core functionality
    - `video_tools.py`: YouTube transcript extraction
    - `summarize.py`: Text summarization
    - `translation.py`: Text translation
- `frontend/`: Next.js frontend
  - `app/`: Next.js app directory
  - `components/`: React components
  - `public/`: Static assets

## Credits

- [youtube-transcript-api](https://github.com/jdepoix/youtube-transcript-api)
- [Webshare](https://www.webshare.io/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [LangChain](https://langchain.com/)
- [LangGraph](https://github.com/langchain-ai/langgraph)
- [Next.js](https://nextjs.org/)
- [OpenRouter](https://openrouter.ai/)
- [Nginx](https://nginx.org/)
- [Docker](https://www.docker.com/)

## License

This project is licensed under the MIT License.

## Contact

For questions or contributions, please open an issue or contact the author.
