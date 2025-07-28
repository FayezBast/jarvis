import os
import subprocess
import asyncio
import json
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from ai_core import AI_Core
from logger import log_info, log_error

class JarvisCore:
    """Enhanced JARVIS Core with PowerShell, Memory, and MCP support"""
    
    def __init__(self, voice_io):
        log_info("Initializing JARVIS Core...")
        api_key = os.getenv('GOOGLE_API_KEY')
        self.ai_core = AI_Core(api_key)
        self.voice_io = voice_io
        self.conversation_history = []
        self.session_id = str(uuid.uuid4())
        
        # Initialize memory storage (simple file-based for now)
        self.memory_file = "jarvis_memory.json"
        self.memory = self._load_memory()
        
        # MCP-related attributes
        self.mcp_processes = {}
        
        log_info("JARVIS Core initialized.")

    def process_command(self, command: str) -> str:
        """Process user command with enhanced capabilities"""
        log_info(f"Processing command: '{command}'")
        if not command:
            response = "How can I help you?"
            self.voice_io.speak(response)
            return response

        try:
            # Store user input for memory
            self._store_memory("user_input", command)
            
            # Get enhanced context with memory
            context = self._build_context_with_memory(command)
            
            # Analyze command with context
            analysis = self.ai_core.analyze_command(context, self.conversation_history)
            response = ""

            if analysis.get("response"):
                response = analysis["response"]
            else:
                intent = analysis.get("intent", "conversation")
                action = analysis.get("action", "chat")
                params = analysis.get("parameters", {})

                # Enhanced command routing
                if intent == "powershell_task":
                    response = self._handle_powershell_task(command, action, params)
                elif intent == "system_control":
                    response = self._handle_system_control(command, action, params)
                elif intent == "file_operation":
                    response = self._handle_file_operation(command, action, params)
                elif intent == "memory_query":
                    response = self._handle_memory_query(command, action, params)
                elif intent == "windows_automation":
                    response = self._handle_windows_automation(command, action, params)
                elif intent == "help":
                    response = self._get_help_text()
                else:
                    response = f"I understand you want to {intent}, but I need more specific instructions."

            # Store conversation
            self.conversation_history.append({"role": "user", "content": command})
            self.conversation_history.append({"role": "assistant", "content": response})
            self.conversation_history = self.conversation_history[-6:]  # Keep last 6 entries
            
            # Store response in memory
            self._store_memory("ai_response", response)
            
            # Extract and store facts
            self._extract_and_store_facts(command)

            self.voice_io.speak(response)
            return response

        except Exception as e:
            log_error(f"Command processing failed: {e}", exc_info=True)
            error_message = "An unexpected error occurred while processing your request."
            self.voice_io.speak(error_message)
            return error_message

    def _handle_powershell_task(self, command: str, action: str, params: Dict) -> str:
        """Enhanced PowerShell handling"""
        try:
            if action == "run_powershell":
                return self._run_powershell_from_gemini(command)
            elif action == "run_script":
                script_path = params.get("script_path", "")
                if script_path:
                    return self._run_powershell_script_file(script_path)
                else:
                    return "Please specify the PowerShell script file path."
            elif action == "get_system_info":
                info_type = params.get("info_type", "general")
                return self._get_system_info(info_type)
            else:
                return self._run_powershell_from_gemini(command)
        except Exception as e:
            log_error(f"PowerShell task failed: {e}")
            return f"PowerShell operation failed: {str(e)}"

    def _handle_system_control(self, command: str, action: str, params: Dict) -> str:
        """Handle system control operations"""
        try:
            if action == "open_application":
                app_name = params.get("application", "")
                return self._open_application(app_name)
            elif action == "get_processes":
                return self._get_running_processes()
            elif action == "kill_process":
                process_name = params.get("process_name", "")
                return self._kill_process(process_name)
            elif action == "get_services":
                return self._get_windows_services()
            else:
                return "System control action not recognized."
        except Exception as e:
            log_error(f"System control failed: {e}")
            return f"System control operation failed: {str(e)}"

    def _handle_file_operation(self, command: str, action: str, params: Dict) -> str:
        """Handle file operations via PowerShell"""
        try:
            if action == "list_files":
                directory = params.get("directory", ".")
                return self._list_files(directory)
            elif action == "read_file":
                file_path = params.get("file_path", "")
                return self._read_file(file_path)
            elif action == "create_file":
                file_path = params.get("file_path", "")
                content = params.get("content", "")
                return self._create_file(file_path, content)
            elif action == "delete_file":
                file_path = params.get("file_path", "")
                return self._delete_file(file_path)
            elif action == "copy_file":
                source = params.get("source", "")
                destination = params.get("destination", "")
                return self._copy_file(source, destination)
            else:
                return "File operation not recognized."
        except Exception as e:
            log_error(f"File operation failed: {e}")
            return f"File operation failed: {str(e)}"

    def _handle_memory_query(self, command: str, action: str, params: Dict) -> str:
        """Handle memory-related queries"""
        try:
            if action == "recall_conversation":
                return self._recall_conversation_history()
            elif action == "recall_facts":
                return self._recall_stored_facts()
            elif action == "clear_memory":
                return self._clear_memory()
            elif action == "search_memory":
                query = params.get("query", "")
                return self._search_memory(query)
            else:
                return "Memory query not recognized."
        except Exception as e:
            log_error(f"Memory query failed: {e}")
            return f"Memory operation failed: {str(e)}"

    def _handle_windows_automation(self, command: str, action: str, params: Dict) -> str:
        """Handle Windows UI automation (simplified version)"""
        try:
            if action == "click_coordinates":
                x = params.get("x", 0)
                y = params.get("y", 0)
                return self._click_at_coordinates(x, y)
            elif action == "send_keys":
                keys = params.get("keys", "")
                return self._send_keys(keys)
            elif action == "get_window_list":
                return self._get_window_list()
            else:
                return "Windows automation action not recognized."
        except Exception as e:
            log_error(f"Windows automation failed: {e}")
            return f"Windows automation failed: {str(e)}"

    # PowerShell execution methods
    def _run_powershell_from_gemini(self, instruction: str) -> str:
        """Generate and execute PowerShell script from natural language"""
        try:
            script = self.ai_core.generate_powershell_script(instruction)
            log_info(f"Generated PowerShell script:\n{script}")
            
            result = subprocess.run(
                ["powershell", "-Command", script], 
                capture_output=True, 
                text=True, 
                check=True,
                timeout=30  # 30 second timeout
            )
            
            output = result.stdout.strip()
            if result.stderr:
                output += f"\nWarnings: {result.stderr.strip()}"
            
            return output or "Command executed successfully."
            
        except subprocess.CalledProcessError as e:
            log_error(f"PowerShell script failed with exit code {e.returncode}")
            return f"PowerShell script failed: {e.stderr.strip() if e.stderr else 'Unknown error'}"
        except subprocess.TimeoutExpired:
            log_error("PowerShell script timed out")
            return "PowerShell script timed out (30 seconds exceeded)."
        except Exception as e:
            log_error(f"PowerShell execution failed: {e}")
            return f"Failed to execute PowerShell command: {str(e)}"

    def _run_powershell_script_file(self, script_path: str) -> str:
        """Execute a PowerShell script file"""
        try:
            if not os.path.exists(script_path):
                return f"Script file not found: {script_path}"
            
            result = subprocess.run(
                ["powershell", "-ExecutionPolicy", "Bypass", "-File", script_path],
                capture_output=True,
                text=True,
                check=True,
                timeout=60
            )
            
            output = result.stdout.strip()
            if result.stderr:
                output += f"\nWarnings: {result.stderr.strip()}"
            
            return output or "Script executed successfully."
            
        except subprocess.CalledProcessError as e:
            return f"Script execution failed: {e.stderr.strip() if e.stderr else 'Unknown error'}"
        except Exception as e:
            return f"Failed to execute script: {str(e)}"

    # System control methods
    def _open_application(self, app_name: str) -> str:
        """Open a Windows application"""
        try:
            script = f"Start-Process '{app_name}'"
            result = subprocess.run(["powershell", "-Command", script], capture_output=True, text=True)
            return f"Attempting to open {app_name}..."
        except Exception as e:
            return f"Failed to open {app_name}: {str(e)}"

    def _get_running_processes(self) -> str:
        """Get list of running processes"""
        try:
            script = "Get-Process | Select-Object Name, Id, CPU | Sort-Object CPU -Descending | Select-Object -First 10 | Format-Table -AutoSize"
            result = subprocess.run(["powershell", "-Command", script], capture_output=True, text=True, check=True)
            return f"Top 10 processes by CPU usage:\n{result.stdout}"
        except Exception as e:
            return f"Failed to get processes: {str(e)}"

    def _get_system_info(self, info_type: str) -> str:
        """Get system information"""
        try:
            if info_type == "cpu":
                script = "Get-WmiObject -Class Win32_Processor | Select-Object Name, NumberOfCores, NumberOfLogicalProcessors"
            elif info_type == "memory":
                script = "Get-WmiObject -Class Win32_ComputerSystem | Select-Object TotalPhysicalMemory"
            elif info_type == "disk":
                script = "Get-WmiObject -Class Win32_LogicalDisk | Select-Object DeviceID, Size, FreeSpace"
            else:
                script = "Get-ComputerInfo | Select-Object WindowsProductName, WindowsVersion, TotalPhysicalMemory"
            
            result = subprocess.run(["powershell", "-Command", script], capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except Exception as e:
            return f"Failed to get system info: {str(e)}"

    # File operation methods
    def _list_files(self, directory: str) -> str:
        """List files in directory"""
        try:
            script = f"Get-ChildItem -Path '{directory}' | Select-Object Name, Length, LastWriteTime | Format-Table -AutoSize"
            result = subprocess.run(["powershell", "-Command", script], capture_output=True, text=True, check=True)
            return f"Files in {directory}:\n{result.stdout}"
        except Exception as e:
            return f"Failed to list files: {str(e)}"

    def _read_file(self, file_path: str) -> str:
        """Read file content"""
        try:
            script = f"Get-Content -Path '{file_path}' -TotalCount 50"  # Limit to first 50 lines
            result = subprocess.run(["powershell", "-Command", script], capture_output=True, text=True, check=True)
            content = result.stdout.strip()
            if len(content) > 1000:  # Limit output length
                content = content[:1000] + "... (truncated)"
            return f"Content of {file_path}:\n{content}"
        except Exception as e:
            return f"Failed to read file: {str(e)}"

    def _create_file(self, file_path: str, content: str) -> str:
        """Create a new file"""
        try:
            escaped_content = content.replace("'", "''")  # Escape single quotes for PowerShell
            script = f"Set-Content -Path '{file_path}' -Value '{escaped_content}'"
            result = subprocess.run(["powershell", "-Command", script], capture_output=True, text=True, check=True)
            return f"File created successfully: {file_path}"
        except Exception as e:
            return f"Failed to create file: {str(e)}"

    # Memory management methods
    def _load_memory(self) -> Dict:
        """Load memory from file"""
        try:
            if os.path.exists(self.memory_file):
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            log_error(f"Failed to load memory: {e}")
        return {"facts": [], "conversations": [], "preferences": {}}

    def _save_memory(self):
        """Save memory to file"""
        try:
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(self.memory, f, indent=2, ensure_ascii=False)
        except Exception as e:
            log_error(f"Failed to save memory: {e}")

    def _store_memory(self, memory_type: str, content: str):
        """Store information in memory"""
        try:
            timestamp = datetime.now().isoformat()
            memory_entry = {
                "type": memory_type,
                "content": content,
                "timestamp": timestamp,
                "session_id": self.session_id
            }
            
            if "conversations" not in self.memory:
                self.memory["conversations"] = []
            
            self.memory["conversations"].append(memory_entry)
            
            # Keep only last 100 conversations
            self.memory["conversations"] = self.memory["conversations"][-100:]
            
            self._save_memory()
        except Exception as e:
            log_error(f"Failed to store memory: {e}")

    def _extract_and_store_facts(self, text: str):
        """Extract and store facts from user input"""
        try:
            # Simple fact extraction patterns
            import re
            
            fact_patterns = [
                (r"my name is (\w+)", "name"),
                (r"i am (\w+)", "name"),
                (r"call me (\w+)", "name"),
                (r"i like (.+)", "preference"),
                (r"i prefer (.+)", "preference"),
                (r"i work at (.+)", "job"),
                (r"my job is (.+)", "job"),
                (r"remember that (.+)", "important")
            ]
            
            for pattern, fact_type in fact_patterns:
                matches = re.findall(pattern, text.lower())
                for match in matches:
                    fact = {
                        "type": fact_type,
                        "content": match.strip(),
                        "timestamp": datetime.now().isoformat(),
                        "source": text
                    }
                    
                    if "facts" not in self.memory:
                        self.memory["facts"] = []
                    
                    # Avoid duplicates
                    if not any(f["type"] == fact_type and f["content"] == match.strip() 
                              for f in self.memory["facts"]):
                        self.memory["facts"].append(fact)
            
            self._save_memory()
        except Exception as e:
            log_error(f"Failed to extract facts: {e}")

    def _build_context_with_memory(self, command: str) -> str:
        """Build enhanced context with memory"""
        context_parts = [f"Current command: {command}"]
        
        # Add relevant facts
        if "facts" in self.memory and self.memory["facts"]:
            context_parts.append("\nRelevant facts about the user:")
            for fact in self.memory["facts"][-5:]:  # Last 5 facts
                context_parts.append(f"- {fact['type']}: {fact['content']}")
        
        # Add recent conversation
        if "conversations" in self.memory and self.memory["conversations"]:
            context_parts.append("\nRecent conversation context:")
            recent_conversations = self.memory["conversations"][-6:]  # Last 6 entries
            for conv in recent_conversations:
                context_parts.append(f"{conv['type']}: {conv['content'][:100]}...")
        
        return "\n".join(context_parts)

    def _recall_conversation_history(self) -> str:
        """Recall recent conversation history"""
        try:
            if not self.conversation_history:
                return "No conversation history available in this session."
            
            history_text = "Recent conversation:\n"
            for entry in self.conversation_history[-6:]:
                role = "You" if entry["role"] == "user" else "Me"
                history_text += f"{role}: {entry['content']}\n"
            
            return history_text
        except Exception as e:
            return f"Failed to recall conversation: {str(e)}"

    def _recall_stored_facts(self) -> str:
        """Recall stored facts about the user"""
        try:
            if "facts" not in self.memory or not self.memory["facts"]:
                return "I don't have any stored facts about you yet."
            
            facts_text = "Here's what I know about you:\n"
            for fact in self.memory["facts"]:
                facts_text += f"- {fact['type'].title()}: {fact['content']}\n"
            
            return facts_text
        except Exception as e:
            return f"Failed to recall facts: {str(e)}"

    # Windows automation (simplified)
    def _click_at_coordinates(self, x: int, y: int) -> str:
        """Click at specified coordinates using PowerShell"""
        try:
            script = f"""
            Add-Type -AssemblyName System.Windows.Forms
            [System.Windows.Forms.Cursor]::Position = New-Object System.Drawing.Point({x}, {y})
            Add-Type -AssemblyName System.Windows.Forms
            $signature = @'
            [DllImport("user32.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.StdCall)]
            public static extern void mouse_event(long dwFlags, long dx, long dy, long cButtons, long dwExtraInfo);
            '@
            $SendMouseClick = Add-Type -memberDefinition $signature -name "Win32MouseEventNew" -namespace Win32Functions -passThru
            $SendMouseClick::mouse_event(0x00000002, 0, 0, 0, 0)
            $SendMouseClick::mouse_event(0x00000004, 0, 0, 0, 0)
            """
            
            result = subprocess.run(["powershell", "-Command", script], capture_output=True, text=True)
            return f"Clicked at coordinates ({x}, {y})"
        except Exception as e:
            return f"Failed to click: {str(e)}"

    def _get_help_text(self) -> str:
        """Get help text for available commands"""
        return """
        JARVIS Enhanced Commands:
        
        🖥️ PowerShell Operations:
        - "Run PowerShell command to get system info"
        - "Execute PowerShell script to list processes"
        - "Get CPU information"
        - "Show running processes"
        
        📁 File Operations:
        - "List files in Documents folder"
        - "Read file config.ini"
        - "Create file test.txt with content 'Hello World'"
        
        🧠 Memory Features:
        - "Remember that I prefer dark mode"
        - "What do you know about me?"
        - "What did we discuss earlier?"
        
        💻 System Control:
        - "Open Calculator"
        - "Get system information"
        - "Show running services"
        
        🖱️ Basic Windows Automation:
        - "Click at coordinates 500, 300"
        - "Send keys Ctrl+C"
        - "List open windows"
        
        Just speak naturally - I'll understand what you want to do!
        """

    def cleanup(self):
        """Clean up resources"""
        try:
            self._save_memory()
            log_info("JARVIS Core cleanup completed.")
        except Exception as e:
            log_error(f"Cleanup failed: {e}")