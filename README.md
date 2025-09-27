# Credit Risk Analysis Platform

A comprehensive full-stack application for credit risk analysis using React.js, FastAPI, and Machine Learning with LLM integration.

## Project Structure

```
Credit Risk Analysis/
├── frontend/                 # React.js frontend application
│   ├── src/
│   │   ├── components/      # Reusable UI components
│   │   ├── pages/          # Application pages
│   │   └── services/       # API services
│   ├── public/             # Public assets
│   └── package.json        # Frontend dependencies
│
├── backend/                 # FastAPI backend application
│   ├── app/
│   │   ├── routers/        # API route handlers
│   │   ├── models/         # Pydantic models
│   │   ├── services/       # Business logic
│   │   └── config.py       # Configuration settings
│   ├── main.py             # FastAPI application entry point
│   └── requirements.txt    # Backend dependencies
│
├── ml/                     # Machine Learning service
│   ├── src/
│   │   ├── llm_service.py  # LLM integration (OpenAI, Anthropic, Cohere)
│   │   └── credit_analyzer.py # ML models for credit analysis
│   ├── models/             # Trained ML models
│   ├── config/             # ML service configuration
│   ├── main.py             # ML service entry point
│   └── requirements.txt    # ML dependencies
│
├── .gitignore             # Git ignore rules
└── README.md              # This file
```

## Features

### Frontend (React.js)
- **Dashboard**: Overview of credit risk statistics
- **Credit Analysis Form**: Input form for credit applications
- **Material-UI Components**: Modern, responsive UI
- **API Integration**: Seamless backend communication
- **Routing**: Multi-page navigation with React Router

### Backend (FastAPI)
- **REST API**: Credit risk analysis endpoints
- **Data Models**: Pydantic models for type safety
- **CORS Support**: Cross-origin resource sharing
- **Statistics API**: Analysis metrics and history
- **ML Service Integration**: Communication with ML service

### ML Service
- **LLM Integration**: Support for multiple AI providers:
  - OpenAI GPT models
  - Anthropic Claude
  - Cohere Command models
- **Credit Risk Models**: Traditional ML algorithms
- **Explanation Service**: AI-powered decision explanations
- **Model Management**: Trained model storage and loading

## Quick Start

### Prerequisites
- Node.js (v16 or higher)
- Python (v3.8 or higher)
- npm or yarn
- pip

### 1. Frontend Setup
```bash
cd frontend
npm install
npm start
```
The frontend will run on `http://localhost:3000`

### 2. Backend Setup
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
The backend API will run on `http://localhost:8000`

### 3. ML Service Setup
```bash
cd ml
pip install -r requirements.txt
python main.py
```
The ML service will run on `http://localhost:8001`

### 4. Environment Configuration

#### Backend (.env)
```bash
cp backend/.env.example backend/.env
# Edit backend/.env with your configuration
```

#### ML Service (.env)
```bash
cp ml/.env.example ml/.env
# Add your API keys:
OPENAI_API_KEY=your-openai-key-here
ANTHROPIC_API_KEY=your-anthropic-key-here
COHERE_API_KEY=your-cohere-key-here
```

## API Endpoints

### Backend API (Port 8000)
- `GET /` - API status
- `POST /api/credit-risk/analyze` - Analyze credit risk
- `GET /api/credit-risk/statistics` - Get analysis statistics
- `GET /api/credit-risk/history` - Get analysis history
- `POST /api/ml/analyze` - LLM analysis proxy

### ML Service API (Port 8001)
- `GET /` - Service status
- `POST /analyze` - General LLM analysis
- `POST /credit-analysis` - Specialized credit analysis
- `POST /explain-decision` - Decision explanation
- `GET /models/status` - Model availability status

## Configuration

### LLM API Keys
The ML service supports multiple AI providers. Configure at least one:

1. **OpenAI**: Get API key from [OpenAI Platform](https://platform.openai.com)
2. **Anthropic**: Get API key from [Anthropic Console](https://console.anthropic.com)
3. **Cohere**: Get API key from [Cohere Dashboard](https://dashboard.cohere.ai)

### Database (Optional)
- Default: SQLite (development)
- Production: Configure PostgreSQL in backend/.env

## Development

### Project Setup for Development
1. Clone/create the repository structure
2. Install dependencies for each service
3. Configure environment variables
4. Start services in development mode

### Adding New Features
- **Frontend**: Add components in `frontend/src/components/`
- **Backend**: Add routes in `backend/app/routers/`
- **ML**: Extend models in `ml/src/`

### Testing
Each service includes testing frameworks:
- Frontend: React Testing Library
- Backend: pytest with FastAPI
- ML: pytest with scikit-learn

## Production Deployment

### Environment Variables
Set production values for:
- Database URLs
- API keys
- Secret keys
- CORS origins

### Security Considerations
- Use strong secret keys
- Configure proper CORS origins
- Implement authentication/authorization
- Use HTTPS in production
- Secure API key storage

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For questions or issues:
- Create an issue in the repository
- Check the documentation
- Review API endpoints with FastAPI docs at `/docs`