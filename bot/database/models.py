"""
Database models for TimeToShopping_bot
SQLAlchemy models for posts and analytics
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Post(Base):
    """Model for storing posts"""
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=True)
    keywords = Column(Text, nullable=True)
    text = Column(Text, nullable=False)
    media_type = Column(String(50), nullable=True)  # photo, video, gif
    file_id = Column(String(255), nullable=True)
    status = Column(String(50), nullable=False, default="draft")  # draft, scheduled, published
    publish_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # User who created the post
    created_by = Column(Integer, nullable=True)
    
    # Post format type
    post_format = Column(String(50), nullable=True)  # selling, collection, info, promo
    
    # Relationship with analytics
    analytics = relationship("Analytics", back_populates="post", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Post(id={self.id}, status='{self.status}', created_at='{self.created_at}')>"
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "title": self.title,
            "keywords": self.keywords,
            "text": self.text,
            "media_type": self.media_type,
            "file_id": self.file_id,
            "status": self.status,
            "publish_at": self.publish_at.isoformat() if self.publish_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "created_by": self.created_by,
            "post_format": self.post_format
        }

class Analytics(Base):
    """Model for storing analytics data"""
    __tablename__ = "analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    action = Column(String(100), nullable=False)  # click_CTA, view, share, etc.
    user_id = Column(String(100), nullable=True)  # Telegram user_id
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Additional metadata
    metadata = Column(Text, nullable=True)  # JSON string for extra data
    
    # Relationship with post
    post = relationship("Post", back_populates="analytics")
    
    def __repr__(self):
        return f"<Analytics(id={self.id}, post_id={self.post_id}, action='{self.action}')>"
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "post_id": self.post_id,
            "action": self.action,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "metadata": self.metadata
        }

class User(Base):
    """Model for storing user information"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    username = Column(String(100), nullable=True)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    is_authorized = Column(String(10), default="false")  # true/false as string
    created_at = Column(DateTime, default=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<User(telegram_id={self.telegram_id}, username='{self.username}')>"
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "telegram_id": self.telegram_id,
            "username": self.username,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "is_authorized": self.is_authorized,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_activity": self.last_activity.isoformat() if self.last_activity else None
        }