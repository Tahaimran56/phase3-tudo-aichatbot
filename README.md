# Todo Web App - Full Stack

A modern, full-stack todo application built with **FastAPI** (Python) backend and **Next.js** (React/TypeScript) frontend. Deploy both frontend and backend to **Vercel** with zero configuration!

## ✨ Features

- 🔐 **User Authentication** - Secure signup/signin with JWT tokens
- ✅ **Task Management** - Create, read, update, delete, and complete tasks
- 🎨 **Modern UI** - Clean, responsive interface built with Tailwind CSS
- 🚀 **Fast API** - High-performance FastAPI backend
- 📱 **Responsive Design** - Works on desktop, tablet, and mobile
- 🔒 **Secure** - Password hashing, HTTP-only cookies, CORS protection
- 🗄️ **PostgreSQL Database** - Neon serverless PostgreSQL

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - SQL toolkit and ORM
- **PostgreSQL** - Neon serverless database
- **JWT** - Secure authentication
- **Pydantic** - Data validation

### Frontend
- **Next.js 15** - React framework with App Router
- **TypeScript** - Type-safe JavaScript
- **Tailwind CSS** - Utility-first styling
- **React Hooks** - Modern state management

## 🚀 Quick Deploy to Vercel

### 1. Fork/Clone this repository

```bash
git clone <your-repo-url>
cd todo
```

### 2. Set up Neon Database

1. Go to [neon.tech](https://neon.tech) and create a free account
2. Create a new project and database
3. Copy your connection string

### 3. Deploy to Vercel

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new)

1. Click "Deploy" or go to [vercel.com](https://vercel.com)
2. Import your GitHub repository
3. Add environment variables:
   - `DATABASE_URL` - Your Neon connection string
   - `SECRET_KEY` - Random 32+ character string
   - `ALGORITHM` - `HS256`
   - `ACCESS_TOKEN_EXPIRE_MINUTES` - `30`
   - `FRONTEND_URL` - Your Vercel URL (update after first deploy)
   - `ENVIRONMENT` - `production`
4. Click "Deploy"
5. Done! Your app is live 🎉

See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed instructions.

## 💻 Local Development

### Prerequisites
- Python 3.12+
- Node.js 18+
- PostgreSQL database (Neon or local)

### Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r ../requirements.txt

# Copy environment file
cp .env.example .env
# Edit .env with your database credentials

# Run migrations
alembic upgrade head

# Start server
uvicorn src.main:app --reload
```

Backend runs at: `http://localhost:8000`
API docs at: `http://localhost:8000/docs`

### Frontend Setup

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Copy environment file
cp .env.local.example .env.local
# Edit .env.local if needed

# Start development server
npm run dev
```

Frontend runs at: `http://localhost:3000`

## 📁 Project Structure

```
todo/
├── api/
│   └── index.py              # Vercel FastAPI entry point
├── backend/
│   ├── src/
│   │   ├── api/              # API endpoints
│   │   │   ├── auth.py       # Authentication routes
│   │   │   └── tasks.py      # Task CRUD routes
│   │   ├── models/           # Database models
│   │   ├── schemas/          # Pydantic schemas
│   │   ├── services/         # Business logic
│   │   ├── middleware/       # CORS, etc.
│   │   ├── config.py         # Configuration
│   │   ├── database.py       # DB connection
│   │   └── main.py           # FastAPI app
│   ├── alembic/              # Database migrations
│   └── tests/                # Backend tests
├── frontend/
│   ├── src/
│   │   ├── app/              # Next.js pages
│   │   ├── components/       # React components
│   │   ├── lib/              # Utilities
│   │   └── types/            # TypeScript types
│   └── public/               # Static assets
├── requirements.txt          # Python dependencies
├── vercel.json              # Vercel configuration
└── .env.example             # Environment template
```

## 🔐 Environment Variables

### Required for Deployment

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection string from Neon |
| `SECRET_KEY` | JWT secret key (32+ characters) |
| `ALGORITHM` | JWT algorithm (use `HS256`) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration (e.g., `30`) |
| `FRONTEND_URL` | Your Vercel app URL |
| `ENVIRONMENT` | `production` or `development` |

See [.env.example](./.env.example) for a template.

## 📚 API Documentation

Once running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Main Endpoints

#### Authentication
- `POST /auth/signup` - Create new account
- `POST /auth/signin` - Sign in
- `POST /auth/signout` - Sign out
- `GET /auth/me` - Get current user

#### Tasks
- `GET /api/tasks` - Get all user tasks
- `POST /api/tasks` - Create new task
- `GET /api/tasks/{id}` - Get specific task
- `PUT /api/tasks/{id}` - Update task
- `DELETE /api/tasks/{id}` - Delete task
- `PATCH /api/tasks/{id}/complete` - Mark task complete

## 🧪 Testing

### Backend Tests

```bash
cd backend
pytest
```

### Frontend Tests

```bash
cd frontend
npm test
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [Next.js](https://nextjs.org/) - React framework
- [Vercel](https://vercel.com/) - Deployment platform
- [Neon](https://neon.tech/) - Serverless PostgreSQL

## 📞 Support

For deployment issues, see [DEPLOYMENT.md](./DEPLOYMENT.md).

For bugs or feature requests, please [open an issue](https://github.com/yourusername/todo/issues).

---

Made with ❤️ using FastAPI and Next.js
