import os
import speech_recognition as sr
from elevenlabs.client import ElevenLabs
import io
import pygame
import threading
import queue
import time
import re
from config import Config
from logger import log_info, log_error, log_warning

class VoiceIO:
    def __init__(self, api_key: str):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.eleven_client = None
        
        self.audio_queue = queue.Queue()
        self.audio_thread = None
        self.is_playing = False
        self.current_audio_id = 0
    
        self.is_listening = False
        self.listen_timeout = 5  # seconds to wait for speech
        self.phrase_timeout = 10 
        
        try:
            pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=512)
            pygame.mixer.init()
            log_info("Pygame mixer initialized for audio playback.")
        except Exception as e:
            log_error(f"Failed to initialize pygame mixer: {e}")
            
        if api_key:
            try:

                self.eleven_client = ElevenLabs(api_key=api_key)
                log_info("ElevenLabs client initialized successfully.")
            except Exception as e:
                log_error(f"Failed to initialize ElevenLabs client: {e}")
        else:
            log_error("ElevenLabs API key not found. Voice output will be disabled.")

        # Calibrate microphone on startup
        self._calibrate_microphone()
        
        # Start the audio processing thread
        self._start_audio_thread()

    def _calibrate_microphone(self):
        """Calibrate microphone for ambient noise once at startup."""
        try:
            with self.microphone as source:
                log_info("Calibrating microphone for ambient noise...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                log_info("Microphone calibration complete.")
        except Exception as e:
            log_error(f"Failed to calibrate microphone: {e}")

    def listen(self) -> str | None:
        """
        Captures audio from the microphone and returns the transcribed text.
        This method is called when the mic button is pressed.
        """
        if self.is_listening:
            log_warning("Already listening...")
            return None
            
        self.is_listening = True
        
        try:
            with self.microphone as source:
                log_info("🎤 Listening for command...")
                
                # Listen for audio with timeout
                audio = self.recognizer.listen(
                    source, 
                    timeout=self.listen_timeout,
                    phrase_time_limit=self.phrase_timeout
                )
                
                log_info("🔄 Processing audio...")
                
                # Recognize speech
                command = self.recognizer.recognize_google(audio)
                log_info(f"✅ Recognized: {command}")
                
                return command
                
        except sr.WaitTimeoutError:
            log_warning("⏰ Listening timed out - no speech detected.")
            return None
        except sr.UnknownValueError:
            log_warning("❓ Could not understand the audio.")
            return None
        except sr.RequestError as e:
            log_error(f"❌ Speech recognition service error: {e}")
            return None
        except Exception as e:
            log_error(f"❌ Unexpected error during listening: {e}")
            return None
        finally:
            self.is_listening = False

    def listen_for_wake_word(self, wake_word: str = "jarvis") -> bool:
        """
        Continuously listen for a wake word. Used for always-on listening mode.
        """
        try:
            with self.microphone as source:
                log_info(f"🎧 Listening for wake word '{wake_word}'...")
                
                audio = self.recognizer.listen(source, timeout=10)
                transcript = self.recognizer.recognize_google(audio)
                
                log_info(f"🗣 Heard: {transcript}")
                
                if wake_word.lower() in transcript.lower():
                    log_info(f"🎯 Wake word '{wake_word}' detected!")
                    return True
                    
                return False
                
        except sr.WaitTimeoutError:
            return False
        except sr.UnknownValueError:
            return False
        except Exception as e:
            log_error(f"Wake word detection error: {e}")
            return False

    def speak(self, text: str):
        """Converts text to speech using streaming chunks."""
        if not self.eleven_client or not text:
            if not text:
                log_warning("No text provided for speech.")
            else:
                log_error("Cannot speak: ElevenLabs client not ready.")
            return

        # Stop any current audio
        self.stop_audio()
        
        # Split text into chunks for streaming
        chunks = self._split_text_into_chunks(text)
        
        # Generate audio ID for this speech session
        audio_id = self.current_audio_id
        self.current_audio_id += 1
        
        # Add chunks to queue with audio ID
        for chunk in chunks:
            if chunk.strip():  # Only add non-empty chunks
                self.audio_queue.put((chunk.strip(), audio_id))

    def speak_streaming(self, text_generator):
        """Speaks text as it's being generated (for streaming responses)."""
        if not self.eleven_client:
            log_error("Cannot speak: ElevenLabs client not ready.")
            return

        # Clear previous audio queue
        self.clear_audio_queue()
        
        # Generate audio ID for this speech session
        audio_id = self.current_audio_id
        self.current_audio_id += 1
        
        # Start a thread to process streaming text
        threading.Thread(
            target=self._process_streaming_text, 
            args=(text_generator, audio_id),
            daemon=True
        ).start()

    def _process_streaming_text(self, text_generator, audio_id):
        """Process streaming text and convert to audio chunks."""
        accumulated_text = ""
        
        for text_chunk in text_generator:
            accumulated_text += text_chunk
            
            # Check if we have a complete sentence or phrase
            sentences = self._extract_complete_sentences(accumulated_text)
            
            for sentence in sentences:
                if sentence.strip():
                    self.audio_queue.put((sentence.strip(), audio_id))
                    accumulated_text = accumulated_text.replace(sentence, "", 1)
        
        # Add any remaining text
        if accumulated_text.strip():
            self.audio_queue.put((accumulated_text.strip(), audio_id))

    def _extract_complete_sentences(self, text):
        """Extract complete sentences from text."""
        sentences = []
        
        # Look for sentence endings
        sentence_endings = re.findall(r'[^.!?]*[.!?]+', text)
        
        # Also split on natural pauses (commas, semicolons) for faster speech
        if not sentence_endings:
            clause_endings = re.findall(r'[^,;]*[,;]+', text)
            if clause_endings:
                return clause_endings[:1]  # Return first clause
        
        return sentence_endings

    def _split_text_into_chunks(self, text, max_chunk_size=200):
        """Split text into manageable chunks for faster processing."""
        if len(text) <= max_chunk_size:
            return [text]
        
        chunks = []
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        current_chunk = ""
        for sentence in sentences:
            if len(current_chunk + sentence) <= max_chunk_size:
                current_chunk += sentence + " "
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + " "
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks

    def _start_audio_thread(self):
        """Start the background audio processing thread."""
        self.audio_thread = threading.Thread(target=self._process_audio_queue, daemon=True)
        self.audio_thread.start()
        log_info("Audio processing thread started.")

    def _process_audio_queue(self):
        """Process audio generation in background thread."""
        current_session_id = None
        
        while True:
            try:
                item = self.audio_queue.get(timeout=1)
                text, audio_id = item
                
                # Skip if this is from an old session
                if current_session_id is not None and audio_id != current_session_id:
                    current_session_id = audio_id
                    continue
                
                current_session_id = audio_id
                
                if text:
                    self._generate_and_play_audio(text)
                self.audio_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                log_error(f"Error in audio processing thread: {e}")

    def _generate_and_play_audio(self, text: str):
        """Generate and play audio synchronously."""
        try:
            self.is_playing = True
            log_info(f"🔊 Generating audio for: '{text[:50]}...'")

            # Use turbo model for faster generation
            audio_generator = self.eleven_client.text_to_speech.convert(
                voice_id=Config.ELEVENLABS_VOICE_ID,
                text=text,
                model_id="eleven_turbo_v2",  # Faster model
                voice_settings={
                    "stability": 0.5,
                    "similarity_boost": 0.75,
                    "style": 0.0,
                    "use_speaker_boost": True
                }
            )

            # Convert generator to bytes
            audio_bytes = b"".join(audio_generator)
            
            log_info("▶️ Playing audio...")
            self._play_audio_with_pygame(audio_bytes)
            
        except Exception as e:
            log_error(f"ElevenLabs error during audio generation: {e}")
            
            # Try alternative method
            try:
                response = self.eleven_client.text_to_speech.convert_as_stream(
                    voice_id=Config.ELEVENLABS_VOICE_ID,
                    text=text,
                    model_id="eleven_turbo_v2"
                )
                
                audio_bytes = b"".join(response)
                log_info("🔄 Playing audio with alternative method...")
                self._play_audio_with_pygame(audio_bytes)
                
            except Exception as fallback_error:
                log_error(f"Fallback audio generation also failed: {fallback_error}")
        finally:
            self.is_playing = False

    def _play_audio_with_pygame(self, audio_bytes: bytes):
        """Play audio using pygame mixer with optimizations."""
        try:
            # Create a BytesIO object from the audio bytes
            audio_io = io.BytesIO(audio_bytes)
            
            # Wait for any previous audio to finish to maintain order
            while pygame.mixer.music.get_busy():
                pygame.time.wait(50)
            
            # Load and play the audio
            pygame.mixer.music.load(audio_io)
            pygame.mixer.music.play()
            
            # Wait for the audio to finish playing
            while pygame.mixer.music.get_busy():
                pygame.time.wait(50)
                
            log_info("✅ Audio playback completed.")
            
        except Exception as e:
            log_error(f"Error playing audio with pygame: {e}")

    def clear_audio_queue(self):
        """Clear the audio queue (for interrupting current speech)."""
        with self.audio_queue.mutex:
            self.audio_queue.queue.clear()

    def stop_audio(self):
        """Stop any currently playing audio."""
        try:
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()
                log_info("🛑 Audio playback stopped.")
            self.clear_audio_queue()
        except Exception as e:
            log_error(f"Error stopping audio: {e}")

    def is_audio_playing(self):
        """Check if audio is currently playing."""
        return self.is_playing or pygame.mixer.music.get_busy()

    def wait_for_audio_complete(self):
        """Wait for all queued audio to complete."""
        self.audio_queue.join()
        while self.is_audio_playing():
            time.sleep(0.1)

    def set_listen_timeout(self, timeout: int):
        """Set the timeout for listening operations."""
        self.listen_timeout = timeout
        log_info(f"Listen timeout set to {timeout} seconds.")

    def set_phrase_timeout(self, timeout: int):
        """Set the maximum phrase length timeout."""
        self.phrase_timeout = timeout
        log_info(f"Phrase timeout set to {timeout} seconds.")

    def get_listening_status(self):
        """Get current listening status."""
        return {
            "is_listening": self.is_listening,
            "is_playing": self.is_audio_playing(),
            "queue_size": self.audio_queue.qsize()
        }

# Standalone conversation loop for JARVIS (similar to your original code)
def jarvis_conversation_loop(voice_io, process_command_func, wake_word="jarvis", conversation_timeout=30):
    """
    Main conversation loop that can work with or without GUI.
    
    Args:
        voice_io: VoiceIO instance
        process_command_func: Function that processes commands and returns responses
        wake_word: Wake word to trigger conversation mode
        conversation_timeout: Seconds of inactivity before exiting conversation mode
    """
    conversation_mode = False
    last_interaction_time = None
    
    log_info("🤖 JARVIS conversation loop started.")
    
    while True:
        try:
            if not conversation_mode:
                # Wake word detection mode
                log_info(f"👂 Listening for wake word '{wake_word}'...")
                if voice_io.listen_for_wake_word(wake_word):
                    voice_io.speak("Yes sir?")
                    conversation_mode = True
                    last_interaction_time = time.time()
                    log_info("🎯 Entered conversation mode.")
            else:
                # Command processing mode
                log_info("🎤 Listening for command...")
                command = voice_io.listen()
                
                if command:
                    log_info(f"📝 Processing command: {command}")
                    
                    # Process the command
                    response = process_command_func(command)
                    
                    if response:
                        print(f"JARVIS: {response}")
                        # The process_command_func should handle speaking via voice_io
                    
                    last_interaction_time = time.time()
                
                # Check for conversation timeout
                if time.time() - last_interaction_time > conversation_timeout:
                    log_info("⏰ Conversation timeout - returning to wake word mode.")
                    conversation_mode = False
        
        except KeyboardInterrupt:
            log_info("👋 Shutting down JARVIS conversation loop...")
            voice_io.speak("Goodbye sir.")
            voice_io.wait_for_audio_complete()
            break
        except Exception as e:
            log_error(f"❌ Error in conversation loop: {e}")
            time.sleep(1)