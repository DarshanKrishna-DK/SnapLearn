"""
Utility functions for SnapLearn AI Backend
"""

import os
import logging
import sys
from typing import Dict, Any, List
from pathlib import Path

def setup_logging():
    """Setup logging configuration"""
    
    # Create logs directory
    logs_dir = Path("../logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(logs_dir / "snaplearn.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Set specific loggers
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)

def validate_environment() -> Dict[str, Any]:
    """Validate required environment variables and dependencies"""
    
    validation_results = {
        "valid": True,
        "errors": [],
        "warnings": [],
        "environment": {},
        "dependencies": {}
    }
    
    # Check environment variables
    required_env_vars = [
        ("GOOGLE_API_KEY", "Gemini API key"),
        ("GEMINI_API_KEY", "Alternative Gemini API key")
    ]
    
    optional_env_vars = [
        ("SUPABASE_URL", "Supabase database URL"),
        ("SUPABASE_ANON_KEY", "Supabase anonymous key"),
        ("ENVIRONMENT", "Application environment (dev/prod)")
    ]
    
    # Check for at least one Gemini API key
    has_gemini_key = bool(os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY"))
    if not has_gemini_key:
        validation_results["errors"].append(
            "No Gemini API key found. Set GOOGLE_API_KEY or GEMINI_API_KEY environment variable."
        )
        validation_results["valid"] = False
    else:
        validation_results["environment"]["gemini_api"] = "✓ Available"
    
    # Check Supabase (optional)
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_ANON_KEY")
    
    if supabase_url and supabase_key:
        validation_results["environment"]["supabase"] = "✓ Configured"
    else:
        validation_results["environment"]["supabase"] = "⚠ Not configured (will use local mode)"
        validation_results["warnings"].append(
            "Supabase not configured. Using local JSON storage."
        )
    
    # Check Python dependencies
    dependencies = [
        ("fastapi", "FastAPI framework"),
        ("uvicorn", "ASGI server"),
        ("pydantic", "Data validation"),
        ("google.genai", "Google Gemini API", "google-genai"),
        ("manim", "Animation engine", "manim")
    ]
    
    for dep_name, description, *install_name in dependencies:
        try:
            __import__(dep_name)
            validation_results["dependencies"][dep_name] = "✓ Available"
        except ImportError:
            pkg_name = install_name[0] if install_name else dep_name
            validation_results["dependencies"][dep_name] = f"✗ Missing (pip install {pkg_name})"
            
            if dep_name in ["fastapi", "uvicorn", "pydantic"]:
                validation_results["errors"].append(f"Missing required dependency: {pkg_name}")
                validation_results["valid"] = False
            else:
                validation_results["warnings"].append(f"Missing optional dependency: {pkg_name}")
    
    # Check directory structure
    required_dirs = [
        "../data",
        "../prompts", 
        "../static",
        "../videos",
        "../logs"
    ]
    
    for dir_path in required_dirs:
        path = Path(dir_path)
        if not path.exists():
            try:
                path.mkdir(parents=True, exist_ok=True)
                validation_results["environment"][f"dir_{path.name}"] = "✓ Created"
            except Exception as e:
                validation_results["errors"].append(f"Cannot create directory {dir_path}: {str(e)}")
                validation_results["valid"] = False
        else:
            validation_results["environment"][f"dir_{path.name}"] = "✓ Exists"
    
    return validation_results

def print_validation_results(results: Dict[str, Any]):
    """Print validation results in a formatted way"""
    
    print("\n" + "="*60)
    print("SnapLearn AI Environment Validation")
    print("="*60)
    
    # Environment status
    print("\nEnvironment Variables:")
    for key, status in results["environment"].items():
        if not key.startswith("dir_"):
            print(f"  {key}: {status}")
    
    # Dependencies status
    print("\nDependencies:")
    for dep, status in results["dependencies"].items():
        print(f"  {dep}: {status}")
    
    # Directory status
    print("\nDirectories:")
    for key, status in results["environment"].items():
        if key.startswith("dir_"):
            dir_name = key.replace("dir_", "")
            print(f"  {dir_name}: {status}")
    
    # Errors and warnings
    if results["errors"]:
        print("\n❌ ERRORS:")
        for error in results["errors"]:
            print(f"  - {error}")
    
    if results["warnings"]:
        print("\n⚠️  WARNINGS:")
        for warning in results["warnings"]:
            print(f"  - {warning}")
    
    # Final status
    status_emoji = "✅" if results["valid"] else "❌"
    status_text = "READY" if results["valid"] else "NOT READY"
    
    print(f"\n{status_emoji} Environment Status: {status_text}")
    
    if not results["valid"]:
        print("\nPlease fix the errors above before starting the server.")
        print("\nQuick setup commands:")
        print("  pip install fastapi uvicorn pydantic google-genai manim")
        print("  export GOOGLE_API_KEY='your-gemini-api-key'")
    
    print("="*60)

def get_system_info() -> Dict[str, Any]:
    """Get system information for debugging"""
    
    import platform
    import psutil
    
    return {
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "architecture": platform.architecture()[0],
            "processor": platform.processor()
        },
        "python": {
            "version": platform.python_version(),
            "executable": sys.executable
        },
        "memory": {
            "total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
            "available_gb": round(psutil.virtual_memory().available / (1024**3), 2),
            "used_percent": psutil.virtual_memory().percent
        },
        "disk": {
            "total_gb": round(psutil.disk_usage('.').total / (1024**3), 2),
            "free_gb": round(psutil.disk_usage('.').free / (1024**3), 2),
            "used_percent": round((psutil.disk_usage('.').used / psutil.disk_usage('.').total) * 100, 1)
        }
    }

def create_default_env_file():
    """Create a default .env file with placeholder values"""
    
    env_content = """# SnapLearn AI Environment Configuration

# Gemini API Configuration (Required)
# Get your API key from: https://aistudio.google.com/app/apikey
GOOGLE_API_KEY=your_gemini_api_key_here
# GEMINI_API_KEY=alternative_key_here

# Supabase Configuration (Optional - will use local mode if not set)
# SUPABASE_URL=https://your-project.supabase.co
# SUPABASE_ANON_KEY=your_supabase_anon_key

# Application Settings
ENVIRONMENT=development
LOG_LEVEL=INFO

# Server Configuration  
HOST=0.0.0.0
PORT=8000
RELOAD=true

# Video Generation Settings
MAX_VIDEO_DURATION=600
VIDEO_QUALITY=1080p60
CLEANUP_VIDEOS_AFTER_DAYS=7

# Memory Settings
MAX_STUDENT_PROFILES=1000
MAX_INTERACTION_HISTORY=1000

# Security (for production)
# SECRET_KEY=your-secret-key-here
# CORS_ORIGINS=http://localhost:3000,http://localhost:5173
"""
    
    env_file = Path(".env")
    if not env_file.exists():
        with open(env_file, 'w') as f:
            f.write(env_content)
        print(f"Created default .env file at: {env_file.absolute()}")
        print("Please edit the .env file and add your API keys.")
    else:
        print(".env file already exists")

def load_environment():
    """Load environment variables from .env file"""
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("Loaded environment variables from .env file")
    except ImportError:
        print("python-dotenv not installed. Using system environment variables only.")
        print("Install with: pip install python-dotenv")

def check_port_available(port: int) -> bool:
    """Check if a port is available"""
    
    import socket
    
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind(('', port))
            return True
    except OSError:
        return False

def get_available_port(start_port: int = 8000, max_attempts: int = 100) -> int:
    """Find an available port starting from start_port"""
    
    for port in range(start_port, start_port + max_attempts):
        if check_port_available(port):
            return port
    
    raise Exception(f"No available ports found in range {start_port}-{start_port + max_attempts}")

def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"

def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to max_length with ellipsis"""
    
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file system use"""
    
    import re
    
    # Remove or replace invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove leading/trailing whitespace and dots
    filename = filename.strip(' .')
    
    # Limit length
    if len(filename) > 100:
        filename = filename[:100]
    
    # Ensure it's not empty
    if not filename:
        filename = "unnamed"
    
    return filename

def create_video_thumbnail(video_path: str, output_path: str, time_offset: str = "00:00:01") -> bool:
    """Create a thumbnail from video using ffmpeg"""
    
    try:
        import subprocess
        
        cmd = [
            "ffmpeg", "-i", video_path, "-ss", time_offset, 
            "-vframes", "1", "-y", output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0
        
    except Exception as e:
        logging.error(f"Error creating video thumbnail: {str(e)}")
        return False

def measure_execution_time(func):
    """Decorator to measure function execution time"""
    
    import functools
    import time
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        execution_time = end_time - start_time
        logging.info(f"{func.__name__} executed in {execution_time:.2f} seconds")
        
        return result
    
    return wrapper

if __name__ == "__main__":
    """Run validation when script is executed directly"""
    
    print("SnapLearn AI Backend Utilities")
    print("Running environment validation...")
    
    # Load environment
    load_environment()
    
    # Run validation
    results = validate_environment()
    print_validation_results(results)
    
    # Create .env if needed
    if not Path(".env").exists():
        create_default_env_file()
    
    # Show system info
    print("\nSystem Information:")
    info = get_system_info()
    
    print(f"  Platform: {info['platform']['system']} {info['platform']['release']}")
    print(f"  Python: {info['python']['version']}")
    print(f"  Memory: {info['memory']['available_gb']:.1f}GB available / {info['memory']['total_gb']:.1f}GB total")
    print(f"  Disk: {info['disk']['free_gb']:.1f}GB free / {info['disk']['total_gb']:.1f}GB total")