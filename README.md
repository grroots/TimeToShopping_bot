# 🛍️ TimeToShopping_bot

**Intelligent Telegram bot for managing the ShoppingTime channel (@time_2_shopping) with AI-powered Armenian content generation**

[![Python](https://img.shields.io/badge/Python-3.13+-blue.svg)](https://python.org)
[![aiogram](https://img.shields.io/badge/aiogram-3.x-green.svg)](https://aiogram.dev)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o--mini-orange.svg)](https://openai.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Deploy on Railway](https://img.shields.io/badge/Deploy-Railway-purple.svg)](https://railway.app)

## 🌟 Overview

TimeToShopping_bot is a comprehensive Telegram administration bot designed specifically for the ShoppingTime channel. It leverages OpenAI's GPT-4o-mini to generate high-quality Armenian content across four different post formats, providing a complete solution for social media management with advanced analytics and scheduling capabilities.

### 🎯 Key Features

- **🤖 AI-Powered Content Generation**: GPT-4o-mini generates authentic Armenian posts
- **📝 Multiple Post Formats**: Selling, Collections, Informational, Promotions
- **⏰ Advanced Scheduling**: Calendar-based scheduling with APScheduler
- **📊 Comprehensive Analytics**: Real-time statistics with CSV/JSON export
- **🎯 Media Support**: Photos, videos, GIFs with Telegram file_id storage
- **🔐 Security**: Whitelist-based access control and input validation
- **📈 Export Capabilities**: Data export in multiple formats
- **🔄 Background Processing**: Automated post publication and monitoring

## 🏗️ Architecture

```
TimeToShopping_bot/
├── bot/                    # Core application
│   ├── handlers/           # Command & callback handlers
│   │   ├── admin.py       # Post creation & management
│   │   ├── analytics.py   # Statistics & reporting
│   │   └── scheduler.py   # Scheduled posts management
│   ├── ai/                # OpenAI integration
│   │   ├── openai_client.py # AI client & text generation
│   │   └── prompts.py     # Armenian prompts & formats
│   ├── database/          # Data persistence
│   │   ├── db.py         # Async database operations
│   │   └── models.py     # SQLAlchemy models
│   ├── keyboards/         # Telegram UI components
│   │   └── common.py     # Inline & reply keyboards
│   ├── middlewares/       # Request processing
│   │   └── access.py     # Authentication & authorization
│   └── utils/            # Utilities & helpers
│       ├── scheduler.py  # APScheduler management
│       └── csv_export.py # Data export functionality
├── tests/                 # Test suites
│   ├── test_ai.py        # AI functionality tests
│   └── __init__.py       # Test configuration
├── docs/                 # Documentation
│   ├── architecture.md   # System architecture
│   └── flow_chart.md     # Process flow diagrams
├── requirements.txt       # Python dependencies
├── Dockerfile            # Container configuration
└── .env.example          # Environment template
```

## 🚀 Quick Start

### 1. Railway Deployment (Recommended)

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template?template=https%3A%2F%2Fgithub.com%2Fyour-repo%2FTimeToShopping_bot)

1. **Fork this repository**
2. **Connect to Railway**
3. **Set environment variables**:
   ```env
   BOT_TOKEN=your_telegram_bot_token_here
   OPENAI_API_KEY=your_openai_api_key_here
   CHANNEL_ID=@time_2_shopping
   CHANNEL_CHAT_ID=-100123456789
   AUTHORIZED_USERS=123456789,987654321
   ```
4. **Deploy automatically!** ⚡

### 2. Render Deployment

1. **Connect GitHub repository to Render**
2. **Choose "Web Service"**
3. **Configure build settings**:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python main.py`
4. **Add environment variables from `.env.example`**
5. **Deploy and monitor** 📊

### 3. Local Development

```bash
# Clone repository
git clone https://github.com/your-repo/TimeToShopping_bot.git
cd TimeToShopping_bot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your credentials

# Initialize database
python -c "
import asyncio
from bot.database.db import db
asyncio.run(db.init_db())
"

# Run bot
python main.py
```

## ⚙️ Configuration

### Required Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `BOT_TOKEN` | Telegram bot token from @BotFather | `123456:ABC-DEF1234...` |
| `OPENAI_API_KEY` | OpenAI API key for GPT-4o-mini | `sk-proj-ABC123...` |
| `CHANNEL_ID` | Channel username | `@time_2_shopping` |
| `CHANNEL_CHAT_ID` | Channel numeric ID | `-100123456789` |
| `AUTHORIZED_USERS` | Comma-separated user IDs | `123456789,987654321` |

### Optional Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite:///./bot_database.db` | Database connection |
| `LOG_LEVEL` | `INFO` | Logging verbosity |
| `SCHEDULER_TIMEZONE` | `Asia/Yerevan` | Timezone for scheduling |
| `OPENAI_MODEL` | `gpt-4o-mini` | OpenAI model |
| `OPENAI_TEMPERATURE` | `0.7` | AI creativity level |
| `HEALTH_CHECK_PORT` | `8000` | Health check port |

## 🎯 Usage Guide

### Bot Commands

| Command | Description | Usage |
|---------|-------------|--------|
| `/start` | Initialize bot and show menu | Basic setup |
| `/new_post` | Create new AI-generated post | Content creation |
| `/drafts` | View and manage draft posts | Content review |
| `/scheduled` | View scheduled publications | Schedule management |
| `/stats` | Analytics dashboard | Performance tracking |
| `/help` | Command reference | User assistance |

### Post Creation Workflow

```mermaid
graph LR
    A[Select Format] --> B[Enter Keywords]
    B --> C[AI Generation]
    C --> D[Review & Edit]
    D --> E[Add Media]
    E --> F[Preview]
    F --> G[Publish/Schedule]
```

### Post Formats (Armenian)

1. **🔥 Վաճառող (Selling Post)**
   - Sales-focused with strong CTA
   - Emotional appeal and urgency
   - Direct call-to-action buttons

2. **📝 Ընտրանի (Collection Post)**
   - Product lists with emojis
   - Organized item presentations
   - Category-based groupings

3. **💡 Տեղեկատվական (Informational Post)**
   - Educational tips and advice
   - How-to guides and insights
   - Value-driven content

4. **⚡ Ակցիա (Promotional Post)**
   - Urgent offers and discounts
   - Time-sensitive deals
   - FOMO-driven messaging

## 📊 Analytics & Reporting

### Real-time Statistics
- **Daily Performance**: Posts, clicks, engagement rates
- **Weekly Trends**: Growth patterns and best times
- **Top Content**: Best-performing posts by format
- **Format Analysis**: Performance comparison by type

### Export Capabilities
- **CSV Export**: Excel-compatible data export
- **JSON Export**: Structured data for APIs
- **Summary Reports**: Key metrics and insights
- **Custom Filtering**: Date ranges and criteria

### Key Metrics Tracked
- **Post Performance**: Views, clicks, shares
- **Engagement Rates**: CTR by format and time
- **User Behavior**: Click patterns and preferences
- **Channel Growth**: Subscriber trends and activity

## 🔧 Development

### Adding New Post Formats

1. **Update prompts configuration**:
   ```python
   # bot/ai/prompts.py
   POST_FORMAT_PROMPTS["new_format"] = {
       "armenian": "Your Armenian prompt here...",
       "cta_examples": ["Button 1", "Button 2"]
   }
   ```

2. **Add to keyboard options**:
   ```python
   # bot/keyboards/common.py
   # Add new format to get_post_format_keyboard()
   ```

3. **Update format mappings**:
   ```python
   # bot/ai/prompts.py
   FORMAT_NAMES["new_format"] = "Armenian Name"
   ```

### Database Migrations

```bash
# Create migration (if using Alembic)
alembic revision --autogenerate -m "Add new feature"

# Apply migration
alembic upgrade head

# Rollback if needed
alembic downgrade -1
```

### Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_ai.py -v

# Run with coverage
pytest tests/ --cov=bot --cov-report=html
```

### Test AI Integration
```bash
python -c "
import asyncio
from bot.ai.openai_client import openai_client
print(asyncio.run(openai_client.test_connection()))
"
```

## 🛡️ Security Features

### Access Control
- **User Whitelist**: Telegram ID-based authorization
- **Session Validation**: Middleware-based request filtering
- **Input Sanitization**: XSS and injection prevention
- **Rate Limiting**: Spam and abuse protection

### Data Protection
- **Environment Variables**: Secure credential storage
- **Database Security**: Parameterized queries and encryption
- **API Key Management**: Secure credential handling
- **Audit Logging**: Complete action tracking

### Security Best Practices
- **Regular Updates**: Automated dependency updates
- **Error Handling**: Graceful failure without info leakage
- **Monitoring**: Security event logging and alerting
- **Backup Strategy**: Regular data backups and recovery

## 📈 Monitoring & Observability

### Health Checks
- **Application Status**: `/health` endpoint for monitoring
- **Database Connectivity**: Connection pool monitoring
- **External APIs**: OpenAI and Telegram API status
- **Background Jobs**: Scheduler health and job status

### Logging Strategy
- **Structured Logging**: JSON format with detailed context
- **Log Levels**: Configurable verbosity (DEBUG, INFO, ERROR)
- **File Rotation**: Automatic log management and archival
- **Error Tracking**: Exception logging with stack traces

### Performance Metrics
- **Response Times**: API and database query performance
- **Resource Usage**: Memory and CPU utilization
- **Success Rates**: Operation success/failure ratios
- **User Activity**: Usage patterns and peak times

## 🔄 Background Processes

### Scheduled Publication
- **APScheduler**: Robust job scheduling and execution
- **Retry Logic**: Automatic retry with exponential backoff
- **Failure Recovery**: Failed post rescheduling and notification
- **Timezone Support**: Multi-timezone scheduling capabilities

### Analytics Processing
- **Real-time Tracking**: Immediate event logging and processing
- **Batch Processing**: Efficient bulk data operations
- **Cache Management**: Performance optimization with smart caching
- **Data Aggregation**: Automated summary generation

## 🌍 Internationalization

### Supported Languages
- **Armenian (Primary)**: Complete UI and content generation
- **Russian**: Fallback support and translation
- **English**: Development and documentation

### Armenian Language Features
- **Text Validation**: Armenian character detection and validation
- **Content Quality**: Automated Armenian text quality scoring
- **Cultural Context**: Culturally appropriate content generation
- **Grammar Checking**: Basic Armenian grammar validation

## 🚀 Deployment Options

### Cloud Platforms

#### Railway (Recommended)
```bash
# One-click deployment
railway login
railway link your-project-id
railway up
```

#### Render
```yaml
# render.yaml
services:
  - type: web
    name: timetoshopping-bot
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: python main.py
```

#### Fly.io
```toml
# fly.toml
app = "timetoshopping-bot"

[build]
  builder = "paketobuildpacks/builder:base"

[[services]]
  http_checks = []
  internal_port = 8000
  processes = ["app"]
  protocol = "tcp"
```

### Docker Deployment

```bash
# Build image
docker build -t timetoshopping-bot .

# Run container
docker run -d \
  --name timetoshopping-bot \
  --env-file .env \
  -p 8000:8000 \
  timetoshopping-bot
```

### Docker Compose
```yaml
# docker-compose.yml
version: '3.8'
services:
  bot:
    build: .
    env_file: .env
    ports:
      - "8000:8000"
    depends_on:
      - db
  
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: timetoshopping
      POSTGRES_USER: bot
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

## 📚 API Reference

### Internal API Endpoints

#### Health Check
```http
GET /health
HTTP/1.1 200 OK
Content-Type: text/plain

OK
```

#### Webhook Support (Optional)
```http
POST /webhook
Content-Type: application/json

{
  "update_id": 123456789,
  "message": {...}
}
```

### Database Schema

#### Posts Table
```sql
CREATE TABLE posts (
    id INTEGER PRIMARY KEY,
    title VARCHAR(255),
    keywords TEXT,
    text TEXT NOT NULL,
    media_type VARCHAR(50),  -- photo, video, gif
    file_id VARCHAR(255),
    status VARCHAR(50) NOT NULL DEFAULT 'draft',  -- draft, scheduled, published
    publish_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER,
    post_format VARCHAR(50)  -- selling, collection, info, promo
);
```

#### Analytics Table
```sql
CREATE TABLE analytics (
    id INTEGER PRIMARY KEY,
    post_id INTEGER NOT NULL REFERENCES posts(id),
    action VARCHAR(100) NOT NULL,  -- click_CTA, view, share, publish
    user_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata TEXT  -- JSON string for additional data
);
```

#### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    telegram_id INTEGER UNIQUE NOT NULL,
    username VARCHAR(100),
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    is_authorized VARCHAR(10) DEFAULT 'false',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🧪 Testing Strategy

### Test Categories

#### Unit Tests
```bash
# AI functionality
pytest tests/test_ai.py::TestPrompts -v
pytest tests/test_ai.py::TestOpenAIClient -v

# Database operations
pytest tests/test_database.py -v

# Utilities
pytest tests/test_utils.py -v
```

#### Integration Tests
```bash
# Full workflow tests
pytest tests/test_integration.py -v

# API integration
pytest tests/test_api_integration.py -v
```

#### Performance Tests
```bash
# Load testing
pytest tests/test_performance.py -v

# Memory usage
pytest tests/test_memory.py -v
```

### Test Coverage Goals
- **Unit Tests**: 90%+ coverage
- **Integration Tests**: Critical paths covered
- **Performance Tests**: Response time benchmarks
- **Security Tests**: Input validation and access control

## 🤝 Contributing

### Development Setup

1. **Fork the repository**
2. **Create feature branch**:
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Setup development environment**:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # Development dependencies
   ```
4. **Run tests**:
   ```bash
   pytest tests/ -v --cov=bot
   ```
5. **Submit pull request**

### Code Standards

#### Python Style
- **PEP 8**: Standard Python style guide
- **Type Hints**: Full type annotation coverage
- **Docstrings**: Google-style documentation
- **Black Formatting**: Automated code formatting

#### Commit Messages
```
feat: add new post format support
fix: resolve scheduling timezone issue
docs: update API documentation
test: add integration tests for AI module
```

#### Pull Request Template
- **Description**: Clear explanation of changes
- **Testing**: Evidence of testing performed
- **Documentation**: Updated relevant documentation
- **Breaking Changes**: Highlighted if applicable

## 📊 Performance Benchmarks

### Response Time Targets
- **Bot Commands**: < 500ms average
- **AI Generation**: < 5s for standard posts
- **Database Queries**: < 100ms for simple queries
- **File Exports**: < 10s for standard datasets

### Scalability Metrics
- **Concurrent Users**: 50+ simultaneous users
- **Posts Per Day**: 1000+ posts
- **Database Size**: 100MB+ with maintained performance
- **Memory Usage**: < 512MB in production

## 🔍 Troubleshooting

### Common Issues

#### Bot Not Responding
1. **Check bot token**: Verify `BOT_TOKEN` is correct
2. **Check network**: Ensure internet connectivity
3. **Check logs**: Review `bot.log` for errors
4. **Restart service**: `systemctl restart bot` or container restart

#### AI Generation Failing
1. **Check OpenAI key**: Verify `OPENAI_API_KEY` is valid
2. **Check quota**: Ensure OpenAI account has available credits
3. **Check rate limits**: Monitor API usage rates
4. **Fallback mode**: Use manual text entry

#### Database Connection Issues
1. **Check database URL**: Verify `DATABASE_URL` format
2. **Check permissions**: Ensure read/write access
3. **Check disk space**: Verify sufficient storage
4. **Run migrations**: Apply pending database changes

#### Scheduling Problems
1. **Check timezone**: Verify `SCHEDULER_TIMEZONE` setting
2. **Check system time**: Ensure server time is correct
3. **Check jobs**: Review scheduled jobs status
4. **Clear failed jobs**: Run cleanup commands

### Debug Mode

```bash
# Enable debug mode
export DEBUG=True
export LOG_LEVEL=DEBUG

# Run with verbose logging
python main.py
```

### Health Check Commands

```bash
# Check scheduler status
python -c "
from bot.utils.scheduler import scheduler_manager
print(f'Scheduler running: {scheduler_manager.scheduler.running}')
"

# Check database connectivity
python -c "
import asyncio
from bot.database.db import db
print(asyncio.run(db.check_database_health()))
"

# Test AI integration
python -c "
import asyncio
from bot.ai.openai_client import openai_client
print(asyncio.run(openai_client.test_connection()))
"
```

## 📖 Additional Resources

### Documentation
- **[Architecture Guide](docs/architecture.md)**: Detailed system architecture
- **[Flow Charts](docs/flow_chart.md)**: Process flow diagrams
- **[API Reference](docs/api_reference.md)**: Complete API documentation

### Community
- **Issues**: [GitHub Issues](https://github.com/your-repo/TimeToShopping_bot/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-repo/TimeToShopping_bot/discussions)
- **Telegram**: Contact bot administrator

### External Links
- **[aiogram Documentation](https://docs.aiogram.dev/)**: Bot framework docs
- **[OpenAI API](https://platform.openai.com/docs)**: AI integration guide
- **[SQLAlchemy Docs](https://docs.sqlalchemy.org/)**: Database ORM docs
- **[APScheduler](https://apscheduler.readthedocs.io/)**: Scheduler documentation

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **[aiogram](https://aiogram.dev/)**: Modern Telegram Bot API framework
- **[OpenAI](https://openai.com)**: AI-powered content generation
- **[Railway](https://railway.app)**: Simple deployment platform
- **[ShoppingTime Community](https://t.me/time_2_shopping)**: Testing and feedback

---

**Built with ❤️ for the ShoppingTime Telegram Channel**

*Ready for immediate deployment on Railway, Render, Fly.io, or any containerized platform!*

## 🚀 Deploy Now

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new)
[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com)

---

**Need help?** Check our [documentation](docs/) or open an [issue](https://github.com/your-repo/TimeToShopping_bot/issues).