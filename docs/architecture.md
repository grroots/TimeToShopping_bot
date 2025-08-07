# 🏗️ TimeToShopping_bot Architecture Documentation

## Overview

TimeToShopping_bot is a sophisticated Telegram bot designed to manage the ShoppingTime channel (@time_2_shopping) with AI-powered content generation in Armenian. The bot provides a comprehensive admin interface for creating, editing, scheduling, and analyzing posts with multiple format support.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    TimeToShopping_bot System                    │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐        │
│  │   Admin     │    │  Analytics  │    │  Scheduler  │        │
│  │  Handlers   │    │  Handlers   │    │  Handlers   │        │
│  └─────────────┘    └─────────────┘    └─────────────┘        │
│         │                   │                   │              │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              Aiogram Dispatcher                         │   │
│  └─────────────────────────────────────────────────────────┘   │
│         │                                                      │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐        │
│  │    Access   │    │  Keyboards  │    │   Utils     │        │
│  │ Middleware  │    │  Manager    │    │  Package    │        │
│  └─────────────┘    └─────────────┘    └─────────────┘        │
└─────────────────────────────────────────────────────────────────┘
                              │
         ┌────────────────────┼────────────────────┐
         │                    │                    │
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   OpenAI    │    │  Database   │    │   Telegram  │
│    API      │    │ (SQLite/PG) │    │ Bot API     │
│ (GPT-4o)    │    │             │    │             │
└─────────────┘    └─────────────┘    └─────────────┘
```

## Core Components

### 1. Handlers Layer (`bot/handlers/`)

#### Admin Handler (`admin.py`)
- **Purpose**: Manages post creation, editing, and publication workflow
- **Key Features**:
  - Multi-step post creation with FSM (Finite State Machine)
  - AI-powered Armenian content generation
  - Media upload handling (photos, videos, GIFs)
  - Post preview and editing capabilities
  - Immediate and scheduled publication

#### Analytics Handler (`analytics.py`)
- **Purpose**: Provides comprehensive analytics and reporting
- **Key Features**:
  - Real-time statistics (daily, weekly, monthly)
  - Top-performing posts analysis
  - Format-based performance metrics
  - CSV export functionality
  - CTA click tracking from published posts

#### Scheduler Handler (`scheduler.py`)
- **Purpose**: Manages scheduled post operations
- **Key Features**:
  - Calendar-based date selection
  - Time picker for precise scheduling
  - Rescheduling and immediate publication options
  - Scheduler status monitoring
  - Failed job cleanup utilities

### 2. AI Integration Layer (`bot/ai/`)

#### OpenAI Client (`openai_client.py`)
- **Purpose**: Interfaces with OpenAI API for content generation
- **Capabilities**:
  - Armenian post generation for 4 different formats
  - Text improvement based on user instructions
  - Content quality analysis and scoring
  - Translation between Armenian, Russian, and English
  - Connection testing and error handling

#### Prompts Manager (`prompts.py`)
- **Purpose**: Manages AI prompts and format definitions
- **Features**:
  - System prompts in Armenian for each post format
  - Dynamic user prompt generation
  - CTA button suggestions
  - Emoji sets for different post types
  - Format validation and name mapping

### 3. Database Layer (`bot/database/`)

#### Models (`models.py`)
```sql
Posts Table:
- id (Primary Key)
- title, keywords, text
- media_type, file_id
- status (draft/scheduled/published)
- publish_at, created_at, updated_at
- created_by, post_format

Analytics Table:
- id (Primary Key)  
- post_id (Foreign Key)
- action, user_id
- created_at, metadata

Users Table:
- id (Primary Key)
- telegram_id, username
- first_name, last_name
- is_authorized, last_activity
```

#### Database Manager (`db.py`)
- **Features**:
  - Async SQLAlchemy operations
  - Connection pooling and management
  - CRUD operations for all models
  - Analytics aggregation queries
  - Migration support (SQLite → PostgreSQL)

### 4. User Interface Layer (`bot/keyboards/`)

#### Keyboard Manager (`common.py`)
- **Purpose**: Provides rich interactive interfaces
- **Components**:
  - Main menu with Armenian labels
  - Post format selection keyboards
  - Calendar picker for scheduling
  - Time selection interface
  - Media type selection
  - Analytics dashboard navigation

### 5. Security Layer (`bot/middlewares/`)

#### Access Control (`access.py`)
- **Purpose**: Restricts bot usage to authorized users
- **Features**:
  - Whitelist-based user authorization
  - Request blocking for unauthorized users
  - Comprehensive access logging
  - User information extraction and validation

### 6. Utilities Layer (`bot/utils/`)

#### Scheduler Manager (`scheduler.py`)
- **Purpose**: Background task management with APScheduler
- **Capabilities**:
  - Async job scheduling and execution
  - Post publication to Telegram channel
  - Job cancellation and rescheduling
  - Health monitoring and failure recovery
  - Timezone-aware scheduling

#### CSV Exporter (`csv_export.py`)
- **Purpose**: Data export functionality
- **Features**:
  - Posts data export with analytics
  - Analytics data export with filtering
  - Summary reports with key metrics
  - Multiple format support (CSV, JSON)
  - Excel-compatible UTF-8 encoding

## Data Flow

### Post Creation Flow

```
User Input → Format Selection → Keywords Entry → AI Generation → 
Text Review → Media Upload → Preview → Publication/Scheduling → 
Channel Publication → Analytics Logging
```

### Analytics Flow

```
User Actions → Database Logging → Aggregation Queries → 
Report Generation → Export/Display → User Insights
```

### Scheduling Flow

```
Post Creation → Schedule Selection → APScheduler Job → 
Background Execution → Channel Publication → Status Update
```

## Technology Stack

### Core Framework
- **Python 3.13+**: Modern Python features and performance
- **aiogram 3.x**: Async Telegram Bot API framework
- **asyncio**: Asynchronous programming support

### AI & NLP
- **OpenAI API**: GPT-4o-mini model for content generation
- **Armenian Language Processing**: Custom text validation and analysis

### Database
- **SQLAlchemy 2.0**: Modern async ORM
- **Aiosqlite**: Async SQLite support
- **PostgreSQL**: Production database option
- **Alembic**: Database migrations

### Task Management
- **APScheduler**: Advanced Python scheduler
- **Background Jobs**: Async task execution
- **Cron-like Scheduling**: Time-based job management

### Development & Deployment
- **Docker**: Containerization support
- **Railway/Render**: Cloud deployment platforms
- **Environment Configuration**: 12-factor app methodology
- **Structured Logging**: loguru-based logging system

## Configuration Management

### Environment Variables
```bash
# Required
BOT_TOKEN=your_telegram_bot_token
OPENAI_API_KEY=your_openai_api_key
AUTHORIZED_USERS=user_id1,user_id2

# Optional
DATABASE_URL=sqlite:///bot_database.db
LOG_LEVEL=INFO
SCHEDULER_TIMEZONE=Asia/Yerevan
```

### Feature Flags
- **Debug Mode**: Enhanced logging and error details
- **Strict Access Control**: Additional security measures
- **Analytics Detailed Tracking**: Extended user behavior tracking
- **Scheduler Health Checks**: Automatic job monitoring

## Security Considerations

### Access Control
- **User Whitelist**: Telegram user ID based authorization
- **Session Validation**: Middleware-based request filtering
- **Input Sanitization**: XSS and injection prevention

### Data Protection
- **Sensitive Data**: Environment variable storage
- **Database Security**: Parameterized queries
- **API Key Management**: Secure credential handling

### Rate Limiting
- **Request Throttling**: Protection against spam
- **Resource Limits**: Memory and CPU usage control
- **Error Handling**: Graceful failure management

## Scalability & Performance

### Database Optimization
- **Connection Pooling**: Efficient connection management
- **Query Optimization**: Index usage and query planning
- **Batch Operations**: Bulk data processing

### Memory Management
- **Async Operations**: Non-blocking I/O operations
- **Resource Cleanup**: Proper connection and file handling
- **Garbage Collection**: Memory usage optimization

### Monitoring & Observability
- **Structured Logging**: JSON-formatted logs
- **Health Checks**: Application status monitoring
- **Performance Metrics**: Response time tracking
- **Error Reporting**: Exception tracking and alerting

## Deployment Architecture

### Development Environment
```
Local Machine → Python Virtual Environment → 
SQLite Database → File-based Logging
```

### Production Environment
```
Cloud Platform (Railway/Render) → Docker Container → 
PostgreSQL Database → Cloud Logging → 
Health Check Endpoints
```

### CI/CD Pipeline
```
Code Push → Automated Tests → Container Build → 
Deployment → Health Verification → Monitoring
```

## Extension Points

### Adding New Post Formats
1. Update `POST_FORMAT_PROMPTS` in `prompts.py`
2. Add format to keyboard in `common.py`
3. Update validation in AI utilities

### Adding New Analytics
1. Extend `Analytics` model in `models.py`
2. Add logging calls in relevant handlers
3. Update export functionality in `csv_export.py`

### Adding New Languages
1. Add language support in AI utilities
2. Create language-specific prompts
3. Update validation and processing functions

## Maintenance & Operations

### Database Maintenance
- **Regular Backups**: Automated backup procedures
- **Index Optimization**: Performance tuning
- **Data Cleanup**: Old analytics data archival

### Security Updates
- **Dependency Updates**: Regular package updates
- **Security Patches**: Vulnerability management
- **Access Review**: Regular authorization audits

### Performance Monitoring
- **Response Time Tracking**: API and database performance
- **Resource Usage**: Memory and CPU monitoring
- **Error Rate Analysis**: Failure pattern identification

---

This architecture provides a robust, scalable, and maintainable foundation for the TimeToShopping_bot, supporting both current requirements and future enhancements.