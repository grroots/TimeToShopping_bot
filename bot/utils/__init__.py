"""
Utils package for TimeToShopping_bot
Utility functions and helper classes
"""

from .scheduler import scheduler_manager, SchedulerManager
from .csv_export import CSVExporter, export_analytics_to_csv, export_posts_to_csv

__all__ = [
    "scheduler_manager", 
    "SchedulerManager",
    "CSVExporter",
    "export_analytics_to_csv",
    "export_posts_to_csv"
]

# Utility functions for common operations

def format_datetime_armenian(dt) -> str:
    """Format datetime in Armenian locale"""
    if not dt:
        return "անհայտ"
    
    # Armenian month names
    armenian_months = [
        "Հունվար", "Փետրվար", "Մարտ", "Ապրիլ", "Մայիս", "Հունիս",
        "Հուլիս", "Օգոստոս", "Սեպտեմբեր", "Հոկտեմբեր", "Նոյեմբեր", "Դեկտեմբեր"
    ]
    
    armenian_month = armenian_months[dt.month - 1]
    return f"{dt.day} {armenian_month} {dt.year}, {dt.strftime('%H:%M')}"

def format_duration_armenian(seconds: int) -> str:
    """Format duration in Armenian"""
    if seconds < 60:
        return f"{seconds} վայրկյան"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes} րոպե"
    elif seconds < 86400:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours} ժամ {minutes} րոպե"
    else:
        days = seconds // 86400
        hours = (seconds % 86400) // 3600
        return f"{days} օր {hours} ժամ"

def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to specified length"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)].rstrip() + suffix

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file operations"""
    import re
    # Remove or replace invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove extra spaces and dots
    filename = re.sub(r'\.+', '.', filename)
    filename = re.sub(r'\s+', '_', filename)
    return filename.strip('._')

def get_file_extension(media_type: str) -> str:
    """Get file extension for media type"""
    extensions = {
        "photo": ".jpg",
        "video": ".mp4", 
        "gif": ".gif",
        "document": ".pdf",
        "audio": ".mp3"
    }
    return extensions.get(media_type, ".bin")

def calculate_reading_time(text: str, words_per_minute: int = 200) -> int:
    """Calculate estimated reading time in seconds"""
    word_count = len(text.split())
    reading_time_minutes = word_count / words_per_minute
    return max(1, int(reading_time_minutes * 60))

def extract_hashtags(text: str) -> list:
    """Extract hashtags from text"""
    import re
    return re.findall(r'#[\w\u0530-\u058F]+', text)

def extract_mentions(text: str) -> list:
    """Extract @mentions from text"""
    import re
    return re.findall(r'@[\w\u0530-\u058F]+', text)

def format_number_armenian(number: int) -> str:
    """Format number with Armenian locale"""
    if number < 1000:
        return str(number)
    elif number < 1000000:
        return f"{number/1000:.1f}հ"  # thousands
    else:
        return f"{number/1000000:.1f}մ"  # millions