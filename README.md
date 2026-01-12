# Thesis Content Guard

A unified platform combining **Content Moderation** and **Thesis Strength Analysis** for investment theses.

## Features

- **Content Moderation Gateway**: Filters scam, spam, and toxic content before analysis
- **Thesis Strength Analysis**: ML + LLM hybrid scoring across 5 dimensions
- **Manual Review System**: Appeals process for blocked content
- **Lightweight Mode**: Optimized for 512MB free tier deployment

## Quick Start

### Backend
```bash
cd backend
pip install -r requirements.txt
python -m spacy download en_core_web_sm
python main.py
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/moderate` | POST | Content moderation check |
| `/api/analyze` | POST | Thesis strength analysis |
| `/api/manual-review` | POST | Request manual review |
| `/api/warmup` | POST | Preload ML models |

## Environment Variables

Create `backend/.env`:
```
OPENAI_API_KEY=your_key_here
LIGHTWEIGHT_MODE=true
```

## Architecture

```
User Input → Content Moderation → PASS/BLOCK
                                    ↓
                            [If PASS]
                                    ↓
                        Thesis Strength Analysis
                                    ↓
                            Results Dashboard
```

## Tech Stack

- **Backend**: FastAPI, spaCy, OpenAI GPT-4o-mini
- **Frontend**: React, Vite, Framer Motion
- **ML Models**: en_core_web_sm, all-MiniLM-L6-v2

## License

MIT
