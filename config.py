# config.py - Updated with all supported intents and configurations
from pathlib import Path

class Config:
    """Configuration settings for JARVIS AI"""
    
    # Directories and Files
    WORKSPACE_DIR = Path.home() / "JARVIS_Workspace"
    LOG_FILE = "jarvis.log"
    HISTORY_FILE = "command_history.json"
    MEMORY_FILE = "jarvis_memory.json"
    
    # AI and Search Settings
    MAX_SEARCH_RESULTS = 10
    MAX_HISTORY_ENTRIES = 100
    MAX_MEMORY_ITEMS = 100
    
    # Supported file formats for creation
    SUPPORTED_FORMATS = ['docx', 'xlsx', 'pdf', 'txt', 'py', 'json', 'csv', 'html', 'md']
    
    # Application aliases for the system controller
    APP_ALIASES = {
        # Browsers
        "chrome": "chrome",
        "google chrome": "chrome",
        "firefox": "firefox",
        "edge": "msedge",
        "browser": "chrome",  # Default browser
        
        # Office Applications
        "word": "winword",
        "microsoft word": "winword",
        "excel": "excel",
        "microsoft excel": "excel",
        "powerpoint": "powerpnt",
        "microsoft powerpoint": "powerpnt",
        
        # Development Tools
        "visual studio code": "code",
        "vscode": "code",
        "vs code": "code",
        "notepad": "notepad",
        "notepad++": "notepad++",
        "sublime": "sublime_text",
        "atom": "atom",
        
        # System Applications
        "calculator": "calc",
        "calc": "calc",
        "command prompt": "cmd",
        "cmd": "cmd",
        "powershell": "powershell",
        "task manager": "taskmgr",
        "control panel": "control",
        "file explorer": "explorer",
        "explorer": "explorer",
        
        # Media Applications
        "vlc": "vlc",
        "media player": "wmplayer",
        "spotify": "spotify",
        "discord": "discord",
        "skype": "skype",
        "zoom": "zoom",
        
        # Other Common Applications
        "paint": "mspaint",
        "snipping tool": "snippingtool",
        "registry editor": "regedit",
        "device manager": "devmgmt.msc"
    }
    
    # Complete list of supported intents
    VALID_INTENTS = [
        # Core intents
        "file_creation",
        "file_management", 
        "system_control",
        "web_browse",
        "conversation",
        "help",
        
        # Extended intents
        "powershell_task",
        "weather_inquiry",
        "knowledge_inquiry",
        "memory_query",
        "clipboard_management",
        "windows_automation",
        "system_status",
        "network_operations",
        "media_control"
    ]
    
    # Action mappings for each intent
    INTENT_ACTIONS = {
        "file_creation": [
            "create_word", "create_excel", "create_pdf", "create_text", 
            "create_code", "create_json", "create_html", "create_markdown"
        ],
        "file_management": [
            "list_files", "read_file", "delete_file", "copy_file", 
            "move_file", "open_file", "find_file", "rename_file"
        ],
        "system_control": [
            "open_application", "close_application", "take_screenshot",
            "get_processes", "get_services", "get_system_info",
            "restart_system", "shutdown_system", "lock_screen"
        ],
        "web_browse": [
            "web_search", "visit_website", "open_url", "google_search"
        ],
        "powershell_task": [
            "run_powershell", "execute_script", "run_command"
        ],
        "weather_inquiry": [
            "get_weather", "get_temperature", "get_forecast", "get_climate"
        ],
        "knowledge_inquiry": [
            "get_summary", "explain_topic", "define_term", "get_information"
        ],
        "memory_query": [
            "store_memory", "recall_memory", "recall_facts", 
            "recall_conversation", "clear_memory", "search_memory"
        ],
        "clipboard_management": [
            "read_clipboard", "write_clipboard", "copy_text", "paste_text"
        ],
        "windows_automation": [
            "click_coordinates", "send_keys", "type_text", 
            "get_window_list", "minimize_window", "maximize_window"
        ],
        "system_status": [
            "get_cpu_usage", "get_memory_usage", "get_disk_usage", 
            "get_network_status", "get_battery_status"
        ],
        "conversation": [
            "chat", "respond", "acknowledge"
        ],
        "help": [
            "show_help", "list_commands", "get_examples"
        ]
    }
    
    # File type mappings
    FILE_TYPE_MAPPINGS = {
        'document': 'docx',
        'doc': 'docx',
        'word': 'docx',
        'spreadsheet': 'xlsx',
        'excel': 'xlsx',
        'presentation': 'pptx',
        'powerpoint': 'pptx',
        'pdf': 'pdf',
        'text': 'txt',
        'txt': 'txt',
        'code': 'py',
        'python': 'py',
        'script': 'py',
        'json': 'json',
        'data': 'json',
        'html': 'html',
        'webpage': 'html',
        'markdown': 'md',
        'md': 'md',
        'csv': 'csv'
    }
    
    # PowerShell command templates
    POWERSHELL_TEMPLATES = {
        'system_info': "Get-ComputerInfo | Select-Object WindowsProductName, WindowsVersion, TotalPhysicalMemory",
        'processes': "Get-Process | Sort-Object CPU -Descending | Select-Object -First 10 | Format-Table Name, Id, CPU",
        'services': "Get-Service | Where-Object {$_.Status -eq 'Running'} | Select-Object -First 10 | Format-Table Name, Status",
        'disk_usage': "Get-WmiObject -Class Win32_LogicalDisk | Select-Object DeviceID, Size, FreeSpace | Format-Table",
        'network_info': "Get-NetAdapter | Where-Object {$_.Status -eq 'Up'} | Format-Table Name, InterfaceDescription, LinkSpeed"
    }
    
    # Response templates for common scenarios
    RESPONSE_TEMPLATES = {
        'file_created': "Successfully created {file_type} file: {filename}",
        'file_not_found': "File not found: {filename}",
        'application_opened': "Opening {application_name}...",
        'application_not_found': "Could not find application: {application_name}",
        'command_executed': "Command executed successfully",
        'command_failed': "Command failed: {error}",
        'memory_stored': "Stored in memory: {content}",
        'memory_empty': "I don't have any stored memories yet.",
        'help_request': "Here are the available commands and examples...",
        'understanding_error': "I'm not sure how to help with that. Could you please rephrase your request?"
    }
    
    # Security settings
    SECURITY_SETTINGS = {
        'max_file_size': 10 * 1024 * 1024,  # 10MB
        'allowed_extensions': SUPPORTED_FORMATS,
        'blocked_commands': [
            'format', 'del /f', 'rm -rf', 'shutdown /s /f', 
            'taskkill /f', 'reg delete', 'rmdir /s'
        ],
        'safe_directories': [
            str(WORKSPACE_DIR),
            str(Path.home() / "Documents"),
            str(Path.home() / "Desktop"),
            str(Path.home() / "Downloads")
        ]
    }
    
    # Performance settings
    PERFORMANCE_SETTINGS = {
        'ai_timeout': 30,  # seconds
        'powershell_timeout': 30,  # seconds
        'file_read_limit': 2000,  # characters
        'memory_item_limit': 50,  # number of items
        'conversation_history_limit': 10,  # number of exchanges
        'process_list_limit': 20,  # number of processes to show
        'file_list_limit': 50  # number of files to show
    }
    
    # Voice settings
    VOICE_SETTINGS = {
        'listen_timeout': 5,  # seconds
        'phrase_timeout': 10,  # seconds
        'voice_response_delay': 0.1,  # seconds
        'audio_chunk_size': 200,  # characters
        'max_response_length': 1000  # characters
    }
    
    # ElevenLabs Voice Settings
    ELEVENLABS_VOICE_ID = 'JBFqnCBsd6RMkjVDRZzb'  # Replace with your voice ID
    ELEVENLABS_MODEL = 'eleven_turbo_v2'  # Fast model for better performance
    ELEVENLABS_VOICE_SETTINGS = {
        'stability': 0.5,
        'similarity_boost': 0.75,
        'style': 0.0,
        'use_speaker_boost': True
    }
    
    # Logging settings
    LOG_SETTINGS = {
        'level': 'INFO',
        'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        'max_file_size': 5 * 1024 * 1024,  # 5MB
        'backup_count': 3
    }
    
    # API settings (placeholders - set via environment variables)
    API_SETTINGS = {
        'google_api_key': None,  # Set via GOOGLE_API_KEY env var
        'elevenlabs_api_key': None,  # Set via ELEVEN_API_KEY env var
        'weather_api_key': None,  # Set via WEATHER_API_KEY env var (optional)
        'openai_api_key': None  # Set via OPENAI_API_KEY env var (optional)
    }
    
    # Feature flags
    FEATURE_FLAGS = {
        'enable_ai_analysis': True,
        'enable_voice_output': True,
        'enable_voice_input': True,
        'enable_memory_system': True,
        'enable_powershell_execution': True,
        'enable_web_browsing': True,
        'enable_file_operations': True,
        'enable_system_control': True,
        'enable_automation': True,
        'enable_clipboard_access': True,
        'safe_mode': False  # Set to True to disable potentially risky operations
    }
    
    # Error messages
    ERROR_MESSAGES = {
        'ai_not_available': "AI analysis is not available. Please check your API key configuration.",
        'voice_not_available': "Voice features are not available. Please check your audio configuration.",
        'permission_denied': "Permission denied. This operation requires administrator privileges.",
        'file_access_denied': "Cannot access file. Please check file permissions and path.",
        'network_error': "Network error occurred. Please check your internet connection.",
        'timeout_error': "Operation timed out. Please try again with a simpler request.",
        'invalid_parameter': "Invalid parameter provided. Please check your command syntax.",
        'feature_disabled': "This feature is currently disabled in the configuration."
    }
    
    # Success messages
    SUCCESS_MESSAGES = {
        'operation_completed': "Operation completed successfully.",
        'file_operation_success': "File operation completed successfully.",
        'system_operation_success': "System operation completed successfully.",
        'memory_operation_success': "Memory operation completed successfully.",
        'automation_success': "Automation task completed successfully."
    }
    
    @classmethod
    def get_app_command(cls, app_name: str) -> str:
        """Get the command to launch an application"""
        return cls.APP_ALIASES.get(app_name.lower(), app_name)
    
    @classmethod
    def get_file_extension(cls, file_type: str) -> str:
        """Get file extension for a given file type"""
        return cls.FILE_TYPE_MAPPINGS.get(file_type.lower(), 'txt')
    
    @classmethod
    def is_safe_command(cls, command: str) -> bool:
        """Check if a command is safe to execute"""
        command_lower = command.lower()
        return not any(blocked in command_lower for blocked in cls.SECURITY_SETTINGS['blocked_commands'])
    
    @classmethod
    def is_safe_directory(cls, directory_path: str) -> bool:
        """Check if a directory is in the safe list"""
        try:
            path = Path(directory_path).resolve()
            return any(str(path).startswith(safe_dir) for safe_dir in cls.SECURITY_SETTINGS['safe_directories'])
        except Exception:
            return False
    
    @classmethod
    def validate_file_size(cls, file_path: str) -> bool:
        """Validate file size against limits"""
        try:
            size = Path(file_path).stat().st_size
            return size <= cls.SECURITY_SETTINGS['max_file_size']
        except Exception:
            return False
    
    @classmethod
    def get_powershell_template(cls, template_name: str) -> str:
        """Get a PowerShell command template"""
        return cls.POWERSHELL_TEMPLATES.get(template_name, "")
    
    @classmethod
    def format_response(cls, template_name: str, **kwargs) -> str:
        """Format a response using templates"""
        template = cls.RESPONSE_TEMPLATES.get(template_name, "{message}")
        try:
            return template.format(**kwargs)
        except KeyError:
            return template
    
    @classmethod
    def is_feature_enabled(cls, feature_name: str) -> bool:
        """Check if a feature is enabled"""
        return cls.FEATURE_FLAGS.get(feature_name, False)
    
    @classmethod
    def get_error_message(cls, error_type: str) -> str:
        """Get an error message"""
        return cls.ERROR_MESSAGES.get(error_type, "An unknown error occurred.")
    
    @classmethod
    def get_success_message(cls, success_type: str) -> str:
        """Get a success message"""
        return cls.SUCCESS_MESSAGES.get(success_type, "Operation completed successfully.")