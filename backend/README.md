# AIRMS MongoDB Backend

🚀 **Complete MongoDB-only backend for AI Risk Management System**

## 🏗️ Architecture

- **FastAPI** - High-performance async web framework
- **MongoDB** - Document database with Motor async driver
- **JWT Authentication** - Access & refresh tokens with bcrypt password hashing
- **Role-based Access Control** - User/Admin permissions
- **Docker** - Containerized deployment
- **GridFS** - File storage for documents and media

## 🚀 Quick Start

### Option 1: Docker (Recommended)

```bash
# Clone and navigate to backend
cd backend_mongo

# Copy environment file
cp .env.example .env

# Edit .env with your settings (optional - defaults work for development)
nano .env

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f backend
```

**Services:**
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/api/v1/docs
- **MongoDB**: localhost:27017
- **Mongo Express**: http://localhost:8081 (admin/airms_admin)

### Option 2: Local Development

```bash
# Install MongoDB locally or use MongoDB Atlas
# Update MONGO_URI in .env

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Run the application
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 🔐 Authentication

### Register User
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123",
    "full_name": "John Doe"
  }'
```

### Login
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }'
```

### Use JWT Token
```bash
# Get your access_token from login response
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## 📊 Database Schema

### Collections

```javascript
// users
{
  _id: ObjectId,
  email: String (unique),
  full_name: String,
  password_hash: String,
  role: String, // "user" | "admin"
  is_active: Boolean,
  created_at: Date,
  updated_at: Date,
  last_login: Date
}

// sessions (for refresh tokens)
{
  _id: ObjectId,
  user_id: ObjectId,
  token: String (unique),
  created_at: Date,
  expires_at: Date
}

// risk_assessments
{
  _id: ObjectId,
  user_id: ObjectId,
  content: String,
  score: Number, // 0-10
  risk_level: String, // "low" | "medium" | "high" | "critical"
  details: Object,
  categories: [String],
  created_at: Date,
  updated_at: Date
}

// daily_analytics
{
  _id: ObjectId,
  user_id: ObjectId,
  date: Date,
  activity: Object,
  risk_level: String,
  created_at: Date
}

// api_keys
{
  _id: ObjectId,
  user_id: ObjectId,
  key: String (unique),
  name: String,
  created_at: Date,
  expires_at: Date
}
```

## 🛡️ Security Features

- ✅ **Password Hashing** - bcrypt with salt
- ✅ **JWT Tokens** - Access (30min) + Refresh (7 days)
- ✅ **Role-based Access** - User/Admin permissions
- ✅ **Input Validation** - Pydantic schemas
- ✅ **CORS Protection** - Configurable origins
- ✅ **Rate Limiting** - Configurable limits
- ✅ **Database Indexes** - Optimized queries

## 🔧 Configuration

Key environment variables:

```bash
# Database
MONGO_URI=mongodb://localhost:27017
MONGO_DB_NAME=airms

# Authentication
JWT_SECRET_KEY=your-secret-key
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Admin User
ADMIN_EMAIL=admin@airms.com
ADMIN_PASSWORD=admin123
```

## 📡 API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login user
- `POST /api/v1/auth/refresh` - Refresh tokens
- `GET /api/v1/auth/me` - Get current user
- `POST /api/v1/auth/logout` - Logout user

### Health & Info
- `GET /health` - Health check
- `GET /` - API information
- `GET /api/v1/docs` - Interactive API documentation

## 🚀 Deployment

### MongoDB Atlas (Production)

1. Create MongoDB Atlas cluster
2. Get connection string
3. Update environment variables:

```bash
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/airms?retryWrites=true&w=majority
DEBUG=false
JWT_SECRET_KEY=your-production-secret-key
```

### Docker Production

```bash
# Build production image
docker build -t airms-backend .

# Run with production settings
docker run -d \
  -p 8000:8000 \
  -e MONGO_URI="your-mongodb-atlas-uri" \
  -e JWT_SECRET_KEY="your-production-secret" \
  -e DEBUG=false \
  airms-backend
```

## 🧪 Testing

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest

# Run with coverage
pytest --cov=app tests/
```

## 📁 Project Structure

```
backend_mongo/
├── app/
│   ├── api/v1/          # API routes
│   ├── core/            # Core functionality
│   ├── models/          # Pydantic models
│   ├── services/        # Business logic
│   └── main.py          # FastAPI app
├── tests/               # Test files
├── docker-compose.yml   # Docker services
├── Dockerfile          # Backend container
├── requirements.txt    # Python dependencies
├── .env.example       # Environment template
└── README.md          # This file
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

- 📚 **Documentation**: http://localhost:8000/api/v1/docs
- 🐛 **Issues**: Create GitHub issue
- 💬 **Discussions**: GitHub discussions

---

**Built with ❤️ using FastAPI + MongoDB**
