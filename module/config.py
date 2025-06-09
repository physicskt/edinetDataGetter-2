"""
Configuration management for EDINET Data Getter
"""
import os
from pathlib import Path


def _load_env_file():
    """Load environment variables from .env file"""
    # Look for .env file in parent directory (project root)
    env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()


# Load environment variables first
_load_env_file()

# Setup base directory (use parent directory as project root)
base_dir = Path(__file__).parent.parent

# Get folder paths and create directories if they don't exist
json_folder = base_dir / os.getenv('JSON_FOLDER', 'json')
log_folder = base_dir / os.getenv('LOG_FOLDER', 'log')
md_folder = base_dir / os.getenv('MD_FOLDER', 'md')
xbrl_folder = base_dir / os.getenv('XBRL_FOLDER', 'xbrl_files')

# Create directories if they don't exist
for folder in [json_folder, log_folder, md_folder, xbrl_folder]:
    folder.mkdir(exist_ok=True)

# Configuration dictionary
config = {
    # API Configuration
    'edinet_api_key': os.getenv('EDINET_API_KEY'),
    'google_drive_folder_url': os.getenv('GOOGLE_SPREADSHEET_URL'),
    'google_service_account_file': base_dir / os.getenv('GOOGLE_SERVICE_ACCOUNT_FILE', '_gcp_key.json'),
    
    # Folder Paths
    'json_folder': json_folder,
    'log_folder': log_folder,
    'md_folder': md_folder,
    'xbrl_folder': xbrl_folder,
    
    # Default Settings
    'default_company_count': int(os.getenv('DEFAULT_COMPANY_COUNT', '1')),
    'default_start_date': os.getenv('DEFAULT_START_DATE', '2024-03-08'),
    'sheet_name': os.getenv('SHEET_NAME', 'EDINET_Data'),
    
    # Log Settings
    'log_file': log_folder / os.getenv('LOG_FILE', 'logfile.log'),
    'max_log_lines': int(os.getenv('MAX_LOG_LINES', '10000')),
    'delete_log_lines': int(os.getenv('DELETE_LOG_LINES', '2000')),
    
    # Skip company word list
    'skip_company_words': [
        "アセットマネジメントＯｎｅ", "アセットマネジメント", "アセット", 
        "ブラックロック・ジャパン株式会社", "ピクテ・ジャパン株式会社",
        "インベストメン", "投信",
    ]
}