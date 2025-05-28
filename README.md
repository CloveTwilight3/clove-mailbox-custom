# Personal Email Client

A full-stack email client application with Python FastAPI backend and React TypeScript frontend, supporting IMAP, POP3, and SMTP protocols.

## 🚀 Features

- **Multi-Account Support**: Manage multiple email accounts with account switching
- **Profile Management**: Custom profile images and display names for each account  
- **Email Management**: Read, compose, reply, forward, and delete emails
- **Real-time Sync**: Automatic email synchronization via IMAP
- **Secure Authentication**: JWT-based authentication with encrypted password storage
- **Modern UI**: Responsive React TypeScript frontend with Tailwind CSS
- **File Attachments**: Support for email attachments and file uploads
- **Search & Filtering**: Advanced email search and filtering capabilities

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **Uvicorn** - ASGI server
- **SQLAlchemy** - Database ORM
- **Pydantic** - Data validation
- **JWT Authentication** - Secure token-based auth
- **Email Protocols**: IMAP, POP3, SMTP support

### Frontend  
- **React 18** with **TypeScript**
- **Vite** - Fast build tool
- **Tailwind CSS** - Utility-first styling
- **React Query** - Data fetching and caching
- **Zustand** - State management
- **React Router** - Client-side routing

## 📁 Project Structure

```
email-client/
├── backend/           # Python FastAPI backend
│   ├── app/
│   │   ├── api/       # API routes
│   │   ├── core/      # Core configuration
│   │   ├── models/    # Database models
│   │   ├── schemas/   # Pydantic schemas
│   │   ├── services/  # Email services (IMAP/SMTP)
│   │   └── utils/     # Utility functions
│   └── requirements.txt
├── frontend/          # React TypeScript frontend
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   └── types/
│   └── package.json
└── docs/             # Documentation
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js 16+
- Git

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/email-client.git
cd email-client
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file and configure
cp .env.example .env
# Edit .env with your settings

# Run development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Copy environment file and configure
cp .env.example .env
# Edit .env with your settings

# Run development server
npm run dev
```

### 4. Access Application

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 🔧 Configuration

### Email Server Settings (One.com)

The application comes pre-configured for one.com email hosting:

```env
# IMAP Settings
DEFAULT_IMAP_HOST=imap.one.com
DEFAULT_IMAP_PORT=993
DEFAULT_IMAP_SSL=True

# POP3 Settings  
DEFAULT_POP3_HOST=pop.one.com
DEFAULT_POP3_PORT=995
DEFAULT_POP3_SSL=True

# SMTP Settings
DEFAULT_SMTP_HOST=send.one.com
DEFAULT_SMTP_PORT=465
DEFAULT_SMTP_SSL=True
```

### Environment Variables

#### Backend (.env)
```env
# Server
HOST=0.0.0.0
PORT=8000
DEBUG=True

# Database
DATABASE_URL=sqlite:///./data/email.db

# Security
SECRET_KEY=your-super-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# File Upload
MAX_FILE_SIZE=5242880
UPLOAD_DIR=./uploads
```

#### Frontend (.env)
```env
VITE_API_URL=http://localhost:8000
VITE_APP_NAME=Personal Email Client
```

## 🔐 Security Features

- **Password Hashing**: Bcrypt for secure password storage
- **JWT Tokens**: Secure authentication with expiring tokens
- **Email Encryption**: Email passwords encrypted in database
- **CORS Protection**: Configured CORS for secure API access
- **Input Validation**: Pydantic models for request validation

## 📧 Email Features

### Supported Operations
- ✅ Connect to IMAP/POP3/SMTP servers
- ✅ Fetch and display email lists
- ✅ Read email content (text/HTML)
- ✅ Compose and send new emails
- ✅ Reply to emails
- ✅ Forward emails
- ✅ Mark as read/unread
- ✅ Delete emails
- ✅ File attachments
- ✅ Profile images

### Supported Email Providers
- ✅ One.com (pre-configured)
- ✅ Gmail (with app passwords)
- ✅ Outlook/Hotmail
- ✅ Yahoo Mail
- ✅ Custom IMAP/SMTP servers

## 🧪 Development

### Running Tests

```bash
# Backend tests
cd backend
python -m pytest

# Frontend tests
cd frontend
npm test
```

### Code Formatting

```bash
# Format Python code
cd backend
black .
isort .

# Format TypeScript code
cd frontend
npm run format
```

### API Documentation

FastAPI automatically generates interactive API documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🚀 Deployment

### Using Docker

```bash
# Build and run with docker-compose
docker-compose up --build
```

### Manual Deployment

1. **Backend**: Deploy FastAPI app with Gunicorn/Uvicorn
2. **Frontend**: Build React app and serve with Nginx
3. **Database**: Use PostgreSQL for production
4. **SSL**: Configure HTTPS with Let's Encrypt

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: Check the `/docs` folder
- **Issues**: Create an issue on GitHub
- **Discussions**: Use GitHub Discussions for questions

## 🔮 Roadmap

- [ ] Email templates
- [ ] Email scheduling
- [ ] Advanced search filters
- [ ] Email labels/tags
- [ ] Dark mode
- [ ] Mobile app (React Native)
- [ ] Email encryption (PGP)
- [ ] Calendar integration
- [ ] Contact management

---

**Built with ❤️ using Python FastAPI and React TypeScript**
