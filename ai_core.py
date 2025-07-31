# ai_core.py - Redesigned for better intent analysis and action mapping
import os
import re
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

import google.generativeai as genai
from config import Config
from security import SecurityValidator
from logger import log_info, log_error, log_warning

@dataclass
class CommandAnalysis:
    """Structured result of command analysis"""
    intent: str
    action: str
    parameters: Dict[str, Any]
    response: Optional[str] = None
    confidence: float = 0.0
    requires_confirmation: bool = False

class IntentClassifier:
    """Fast rule-based intent classification for common commands"""
    
    INTENT_PATTERNS = {
        'file_creation': [
            r'create.*(?:file|document|doc|txt|pdf)',
            r'make.*(?:file|document|doc|txt|pdf)',
            r'new.*(?:file|document|doc|txt|pdf)',
            r'generate.*(?:file|document|doc|txt|pdf)'
        ],
        'file_management': [
            r'list.*files?',
            r'show.*files?',
            r'open.*(?:file|folder|directory)',
            r'delete.*(?:file|folder)',
            r'copy.*(?:file|folder)',
            r'move.*(?:file|folder)',
            r'read.*file',
            r'find.*file'
        ],
        'system_control': [
            r'open.*(?:application|app|program)',
            r'start.*(?:application|app|program)',
            r'launch.*(?:application|app|program)',
            r'run.*(?:application|app|program)',
            r'close.*(?:application|app|program)',
            r'kill.*process',
            r'restart.*(?:computer|system)',
            r'shutdown.*(?:computer|system)',
            r'take.*screenshot',
            r'get.*(?:processes|services)',
            r'system.*(?:info|status)'
        ],
        'web_browse': [
            r'search.*(?:for|about)',
            r'google.*',
            r'browse.*',
            r'visit.*(?:website|site)',
            r'open.*(?:website|site|url)',
            r'look.*up'
        ],
        'powershell_task': [
            r'powershell.*',
            r'run.*(?:command|script)',
            r'execute.*(?:command|script)',
            r'cmd.*',
            r'terminal.*'
        ],
        'weather_inquiry': [
            r'weather.*(?:in|for|at)',
            r'temperature.*(?:in|for|at)',
            r'forecast.*(?:in|for|at)',
            r'climate.*(?:in|for|at)'
        ],
        'knowledge_inquiry': [
            r'what.*is',
            r'tell.*me.*about',
            r'explain.*',
            r'define.*',
            r'describe.*',
            r'how.*(?:does|do|to)',
            r'why.*(?:does|do|is)'
        ],
        'memory_query': [
            r'remember.*',
            r'recall.*',
            r'what.*(?:do you know|did we discuss)',
            r'forget.*',
            r'clear.*memory'
        ],
        'clipboard_management': [
            r'copy.*(?:to clipboard|clipboard)',
            r'paste.*(?:from clipboard|clipboard)',
            r'read.*clipboard',
            r'clipboard.*'
        ],
        'windows_automation': [
            r'click.*(?:at|on)',
            r'press.*(?:key|keys)',
            r'type.*',
            r'send.*keys',
            r'window.*list',
            r'minimize.*window',
            r'maximize.*window'
        ]
    }
    
    @classmethod
    def classify_intent(cls, command: str) -> Optional[str]:
        """Fast intent classification using regex patterns"""
        command_lower = command.lower().strip()
        
        for intent, patterns in cls.INTENT_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, command_lower):
                    return intent
        
        return None

class ActionMapper:
    """Maps commands to specific actions within intents"""
    
    ACTION_MAPPING = {
        'file_creation': {
            r'word|doc|docx': 'create_word',
            r'excel|xlsx|spreadsheet': 'create_excel',
            r'pdf': 'create_pdf',
            r'text|txt': 'create_text',
            r'python|py|code': 'create_code',
            r'json': 'create_json'
        },
        'file_management': {
            r'list.*files?': 'list_files',
            r'open.*(?:file|folder)': 'open_file',
            r'delete.*(?:file|folder)': 'delete_file',
            r'copy.*(?:file|folder)': 'copy_file',
            r'move.*(?:file|folder)': 'move_file',
            r'read.*file': 'read_file',
            r'find.*file': 'find_file'
        },
        'system_control': {
            r'open.*(?:application|app)': 'open_application',
            r'close.*(?:application|app)': 'close_application',
            r'take.*screenshot': 'take_screenshot',
            r'get.*processes': 'get_processes',
            r'get.*services': 'get_services',
            r'system.*info': 'get_system_info',
            r'restart': 'restart_system',
            r'shutdown': 'shutdown_system'
        },
        'web_browse': {
            r'search.*for': 'web_search',
            r'google': 'web_search',
            r'visit.*(?:website|site)': 'visit_website',
            r'open.*(?:website|site|url)': 'visit_website'
        },
        'powershell_task': {
            r'run.*(?:command|script)': 'run_powershell',
            r'execute.*(?:command|script)': 'run_powershell',
            r'powershell': 'run_powershell'
        },
        'weather_inquiry': {
            r'weather': 'get_weather',
            r'temperature': 'get_temperature',
            r'forecast': 'get_forecast'
        },
        'memory_query': {
            r'remember': 'store_memory',
            r'recall': 'recall_memory',
            r'what.*know': 'recall_facts',
            r'what.*discuss': 'recall_conversation',
            r'forget': 'clear_memory'
        }
    }
    
    @classmethod
    def get_action(cls, intent: str, command: str) -> str:
        """Get specific action for intent and command"""
        if intent not in cls.ACTION_MAPPING:
            return 'default_action'
        
        command_lower = command.lower()
        actions = cls.ACTION_MAPPING[intent]
        
        for pattern, action in actions.items():
            if re.search(pattern, command_lower):
                return action
        
        return 'default_action'

class ParameterExtractor:
    """Extract parameters from commands"""
    
    PARAMETER_PATTERNS = {
        'file_path': r'(?:file|path)\s+["\']?([^"\']+)["\']?',
        'application_name': r'(?:open|start|launch)\s+([a-zA-Z\s]+)',
        'search_query': r'(?:search|google)\s+(?:for\s+)?["\']?([^"\']+)["\']?',
        'city_name': r'(?:weather|temperature|forecast)\s+(?:in|for|at)\s+([a-zA-Z\s]+)',
        'topic': r'(?:about|explain|tell me about)\s+([^.!?]+)',
        'content': r'(?:create|make|write)\s+.*?(?:about|with|containing)\s+([^.!?]+)',
        'coordinates': r'(?:click|at)\s+(?:coordinates\s+)?(?:[\(\[])?(\d+)[\s,]+(\d+)(?:[\)\]])?',
        'keys': r'(?:press|send|type)\s+(?:keys?\s+)?["\']?([^"\']+)["\']?',
        'directory': r'(?:in|from|at)\s+(?:folder|directory)\s+["\']?([^"\']+)["\']?'
    }
    
    @classmethod
    def extract_parameters(cls, command: str, intent: str, action: str) -> Dict[str, Any]:
        """Extract parameters based on intent and action"""
        parameters = {}
        command_lower = command.lower()
        
        # Extract common parameters
        for param_name, pattern in cls.PARAMETER_PATTERNS.items():
            match = re.search(pattern, command_lower)
            if match:
                if param_name == 'coordinates':
                    parameters['x'] = int(match.group(1))
                    parameters['y'] = int(match.group(2))
                else:
                    parameters[param_name] = match.group(1).strip()
        
        # Intent-specific parameter extraction
        if intent == 'file_creation':
            parameters['file_type'] = cls._extract_file_type(command)
            if 'content' not in parameters:
                parameters['content_topic'] = cls._extract_topic_from_creation_command(command)
        
        elif intent == 'weather_inquiry':
            if 'city_name' not in parameters:
                # Try to extract city from different patterns
                city_match = re.search(r'(?:weather|temperature|forecast).*?(?:in|for|at|of)\s+([a-zA-Z\s]+)', command_lower)
                if city_match:
                    parameters['city'] = city_match.group(1).strip()
        
        elif intent == 'system_control' and action == 'open_application':
            if 'application_name' not in parameters:
                # Try to extract app name after 'open'
                app_match = re.search(r'open\s+([a-zA-Z\s]+)', command_lower)
                if app_match:
                    parameters['application'] = app_match.group(1).strip()
        
        return parameters
    
    @classmethod
    def _extract_file_type(cls, command: str) -> str:
        """Extract file type from command"""
        command_lower = command.lower()
        
        type_mappings = {
            'word': 'docx',
            'doc': 'docx',
            'document': 'docx',
            'excel': 'xlsx',
            'spreadsheet': 'xlsx',
            'pdf': 'pdf',
            'text': 'txt',
            'txt': 'txt',
            'python': 'py',
            'code': 'py',
            'json': 'json'
        }
        
        for keyword, file_type in type_mappings.items():
            if keyword in command_lower:
                return file_type
        
        return 'txt'  # Default
    
    @classmethod
    def _extract_topic_from_creation_command(cls, command: str) -> str:
        """Extract topic from file creation command"""
        # Remove common words to get the topic
        clean_command = re.sub(r'(?:create|make|new|generate|write|file|document|about|on|for)', '', command.lower())
        clean_command = re.sub(r'(?:word|excel|pdf|text|txt|python|code|json)', '', clean_command)
        clean_command = ' '.join(clean_command.split())  # Remove extra spaces
        
        return clean_command.strip() or "general topic"

class AI_Core:
    """Redesigned AI Core with better intent handling and fallbacks"""
    
    def __init__(self, api_key: str):
        self.gemini_client = None
        self.use_ai_analysis = False
        
        if api_key:
            try:
                genai.configure(api_key=api_key)
                self.gemini_client = genai.GenerativeModel('gemini-2.0-flash-exp')
                self.use_ai_analysis = True
                log_info("Google Gemini AI initialized successfully.")
            except Exception as e:
                log_error(f"Failed to initialize Gemini AI: {e}")
                log_warning("Falling back to rule-based analysis only.")
        else:
            log_warning("Gemini AI not initialized: API key is missing.")

    def analyze_command(self, command: str, history: List[Dict[str, str]] = None) -> CommandAnalysis:
        """
        Analyze command with hybrid approach: fast rule-based + AI fallback
        """
        if not command.strip():
            return CommandAnalysis(
                intent='conversation',
                action='chat',
                parameters={},
                response="How can I help you?"
            )

        # Step 1: Try fast rule-based classification
        intent = IntentClassifier.classify_intent(command)
        
        if intent and intent != 'conversation':
            # Rule-based analysis succeeded
            action = ActionMapper.get_action(intent, command)
            parameters = ParameterExtractor.extract_parameters(command, intent, action)
            
            return CommandAnalysis(
                intent=intent,
                action=action,
                parameters=parameters,
                confidence=0.8
            )
        
        # Step 2: Try AI analysis if available
        if self.use_ai_analysis:
            try:
                return self._ai_analyze_command(command, history or [])
            except Exception as e:
                log_error(f"AI analysis failed: {e}")
        
        # Step 3: Final fallback - treat as conversation
        return CommandAnalysis(
            intent='conversation',
            action='chat',
            parameters={},
            response=self._generate_fallback_response(command),
            confidence=0.3
        )

    def _ai_analyze_command(self, command: str, history: List[Dict[str, str]]) -> CommandAnalysis:
        """AI-powered command analysis with structured output"""
        
        formatted_history = "\n".join([
            f"{msg['role'].capitalize()}: {msg['content'][:100]}..." 
            for msg in history[-4:]  # Last 4 exchanges
        ])

        prompt = f"""
        Analyze this command and return a JSON response:
        
        COMMAND: "{command}"
        RECENT CONTEXT: {formatted_history}
        
        Available intents: {', '.join(Config.VALID_INTENTS + ['weather_inquiry', 'knowledge_inquiry', 'memory_query', 'clipboard_management', 'powershell_task', 'windows_automation'])}
        
        Rules:
        1. If it's a task/action, set "response" to null and provide intent/action/parameters
        2. If it's a question/chat, set intent to "conversation", action to "chat", and provide a helpful response
        3. Extract ALL relevant parameters from the command
        
        Examples:
        - "create a word document about AI" → {{"intent": "file_creation", "action": "create_word", "parameters": {{"content_topic": "AI", "file_type": "docx"}}, "response": null}}
        - "what's the weather in Paris" → {{"intent": "weather_inquiry", "action": "get_weather", "parameters": {{"city": "Paris"}}, "response": null}}
        - "how are you today" → {{"intent": "conversation", "action": "chat", "parameters": {{}}, "response": "I'm doing well, thank you for asking! How can I assist you today?"}}
        
        Return ONLY valid JSON:
        """
        
        try:
            response = self.gemini_client.generate_content(prompt)
            json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
            
            if json_match:
                analysis_data = json.loads(json_match.group(0))
                
                return CommandAnalysis(
                    intent=analysis_data.get('intent', 'conversation'),
                    action=analysis_data.get('action', 'chat'),
                    parameters=analysis_data.get('parameters', {}),
                    response=analysis_data.get('response'),
                    confidence=0.9
                )
            else:
                raise ValueError("No valid JSON found in AI response")
                
        except Exception as e:
            log_error(f"AI analysis parsing failed: {e}")
            raise

    def _generate_fallback_response(self, command: str) -> str:
        """Generate a fallback response for unrecognized commands"""
        responses = [
            "I'm not sure how to help with that. Could you please rephrase your request?",
            "I don't understand that command. Try asking me to create a file, open an application, or search for something.",
            "Could you be more specific about what you'd like me to do?",
            "I'm having trouble understanding. Try commands like 'create a document', 'open calculator', or 'search for AI'."
        ]
        
        import random
        return random.choice(responses)

    def generate_file_content(self, topic: str, file_type: str) -> str:
        """Generate content for file creation"""
        if not self.gemini_client:
            return self._generate_fallback_content(topic, file_type)

        content_prompts = {
            'docx': f"Write a professional document about '{topic}'. Include an introduction, main points, and conclusion. Use clear headings and bullet points where appropriate.",
            'xlsx': f"Create a structured data layout about '{topic}' in text format that could be used in a spreadsheet. Include column headers and sample data rows.",
            'pdf': f"Write a comprehensive report about '{topic}' suitable for PDF format. Include title, sections with headings, and detailed content.",
            'txt': f"Write informative content about '{topic}' in plain text format with clear structure.",
            'py': f"Write a complete, well-documented Python script for: '{topic}'. Include imports, functions, error handling, and a main execution block.",
            'json': f"Create a realistic JSON structure containing information about '{topic}'. Include nested objects and arrays where appropriate."
        }

        prompt = content_prompts.get(file_type, content_prompts['txt'])

        try:
            response = self.gemini_client.generate_content(prompt)
            content = response.text.strip()
            
            # Clean up code blocks if present
            if file_type in ['py', 'json']:
                content = re.sub(r'^```\w*\n?', '', content)
                content = re.sub(r'\n?```$', '', content)
            
            return SecurityValidator.sanitize_content(content)
            
        except Exception as e:
            log_error(f"AI content generation failed: {e}")
            return self._generate_fallback_content(topic, file_type)

    def _generate_fallback_content(self, topic: str, file_type: str) -> str:
        """Fallback content generation without AI"""
        templates = {
            'docx': f"# {topic.title()}\n\nThis document covers information about {topic}.\n\n## Introduction\n\n[Content about {topic}]\n\n## Main Points\n\n- Point 1\n- Point 2\n- Point 3\n\n## Conclusion\n\n[Summary of {topic}]",
            'txt': f"{topic.title()}\n{'=' * len(topic)}\n\nThis file contains information about {topic}.\n\nAdd your content here...",
            'py': f"#!/usr/bin/env python3\n# -*- coding: utf-8 -*-\n\"\"\"\n{topic.title()} Script\n\nDescription: Script related to {topic}\n\"\"\"\n\ndef main():\n    \"\"\"Main function\"\"\"\n    print(\"This script is about {topic}\")\n    # Add your code here\n    pass\n\nif __name__ == \"__main__\":\n    main()",
            'json': f'{{\n  "topic": "{topic}",\n  "description": "Data about {topic}",\n  "data": [],\n  "metadata": {{\n    "created": "auto-generated",\n    "type": "{file_type}"\n  }}\n}}'
        }
        
        return templates.get(file_type, f"Content about {topic}\n\nAdd your information here...")

    def generate_powershell_script(self, instruction: str) -> str:
        """Generate PowerShell script from natural language instruction"""
        if not self.gemini_client:
            return self._generate_fallback_powershell(instruction)

        prompt = f"""
        Generate a PowerShell script for: "{instruction}"
        
        Requirements:
        - Return ONLY the PowerShell code, no explanations
        - Use proper error handling with try-catch
        - Include appropriate output formatting
        - Keep it secure and safe
        - Use built-in cmdlets when possible
        
        Examples:
        - "get system info" → Get-ComputerInfo | Select-Object WindowsProductName, WindowsVersion
        - "list running processes" → Get-Process | Sort-Object CPU -Descending | Select-Object -First 10
        """

        try:
            response = self.gemini_client.generate_content(prompt)
            script = response.text.strip()
            
            # Clean up code blocks
            script = re.sub(r'^```powershell\n?', '', script)
            script = re.sub(r'^```\n?', '', script)
            script = re.sub(r'\n?```$', '', script)
            
            return script.strip()
            
        except Exception as e:
            log_error(f"PowerShell generation failed: {e}")
            return self._generate_fallback_powershell(instruction)

    def _generate_fallback_powershell(self, instruction: str) -> str:
        """Fallback PowerShell script generation"""
        instruction_lower = instruction.lower()
        
        if any(word in instruction_lower for word in ['system', 'info', 'computer']):
            return "Get-ComputerInfo | Select-Object WindowsProductName, WindowsVersion, TotalPhysicalMemory"
        elif any(word in instruction_lower for word in ['process', 'running', 'task']):
            return "Get-Process | Sort-Object CPU -Descending | Select-Object -First 10 | Format-Table Name, Id, CPU"
        elif any(word in instruction_lower for word in ['service']):
            return "Get-Service | Where-Object {$_.Status -eq 'Running'} | Format-Table Name, Status"
        elif any(word in instruction_lower for word in ['file', 'list', 'directory']):
            return "Get-ChildItem | Format-Table Name, Length, LastWriteTime"
        else:
            return f"Write-Host 'Executing: {instruction}'"