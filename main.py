import sys
import json
import threading
import urllib.request
import os
from dotenv import load_dotenv
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                             QWidget, QTextEdit, QLineEdit, QPushButton, QLabel, QFrame)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap, QTextCursor, QFont, QPalette

# Lade Umgebungsvariablen aus .env-Datei
load_dotenv()

# Default language mode: 0 = English, 1 = German
language_mode = 0

class StreamingThread(QThread):
    text_received = pyqtSignal(str)
    response_finished = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, prompt_message):
        super().__init__()
        self.prompt_message = prompt_message

    def run(self):
        try:
            url = "https://api.deepseek.com/chat/completions"
            api_key = os.getenv('DEEPSEEK_API_KEY')
            
            if not api_key:
                self.error_occurred.emit("❌ Fehler: DEEPSEEK_API_KEY nicht in .env-Datei gefunden!")
                return
            
            data = {
                "model": "deepseek-chat",
                "messages": [
                    {
                        "role": "user",
                        "content": self.prompt_message
                    }
                ],
                "max_tokens": 1000,
                "temperature": 0.7,
                "stream": True  # Aktiviere Streaming falls unterstützt
            }
            
            json_data = json.dumps(data).encode('utf-8')
            request = urllib.request.Request(
                url,
                data=json_data,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {api_key}'
                },
                method='POST'
            )
            
            with urllib.request.urlopen(request) as response:
                if response.status == 200:
                    # Versuche zuerst Streaming
                    full_response = ""
                    for line in response:
                        line = line.decode('utf-8').strip()
                        if line.startswith('data: '):
                            line = line[6:]  # Entferne 'data: ' Präfix
                            if line == '[DONE]':
                                break
                            try:
                                chunk = json.loads(line)
                                if 'choices' in chunk and len(chunk['choices']) > 0:
                                    delta = chunk['choices'][0].get('delta', {})
                                    if 'content' in delta:
                                        text = delta['content']
                                        full_response += text
                                        self.text_received.emit(text)
                            except json.JSONDecodeError:
                                # Falls Streaming nicht funktioniert, versuche normale Antwort
                                response_data = json.loads(response.read().decode('utf-8'))
                                full_response = response_data['choices'][0]['message']['content']
                                # Simuliere Streaming durch Zeichenweise Ausgabe
                                for char in full_response:
                                    self.text_received.emit(char)
                                    self.msleep(20)  # Kleine Verzögerung für Streaming-Effekt
                                break
                    
                    self.response_finished.emit(full_response)
                else:
                    self.error_occurred.emit(f"HTTP Fehler: {response.status}")
                    
        except Exception as e:
            # Fallback ohne Streaming
            try:
                url = "https://api.deepseek.com/chat/completions"
                api_key = os.getenv('DEEPSEEK_API_KEY')
                
                if not api_key:
                    self.error_occurred.emit("❌ Fehler: DEEPSEEK_API_KEY nicht in .env-Datei gefunden!")
                    return
                
                data = {
                    "model": "deepseek-chat",
                    "messages": [
                        {
                            "role": "user",
                            "content": self.prompt_message
                        }
                    ],
                    "max_tokens": 1000,
                    "temperature": 0.7
                }
                
                json_data = json.dumps(data).encode('utf-8')
                request = urllib.request.Request(
                    url,
                    data=json_data,
                    headers={
                        'Content-Type': 'application/json',
                        'Authorization': f'Bearer {api_key}'
                    },
                    method='POST'
                )
                
                with urllib.request.urlopen(request) as response:
                    if response.status == 200:
                        response_data = json.loads(response.read().decode('utf-8'))
                        full_response = response_data['choices'][0]['message']['content']
                        
                        # Simuliere Streaming durch Zeichenweise Ausgabe
                        for char in full_response:
                            self.text_received.emit(char)
                            self.msleep(30)  # Kleine Verzögerung für Streaming-Effekt
                        
                        self.response_finished.emit(full_response)
                    else:
                        self.error_occurred.emit(f"HTTP Fehler: {response.status}")
            except Exception as fallback_error:
                self.error_occurred.emit(f"Verbindungsfehler: {str(fallback_error)}")

class BubiApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.chat_history = []
        self.init_ui()
        self.apply_styles()
        self.update_language()

    def init_ui(self):
        self.setWindowTitle("Bubi AI Assistant")
        self.setGeometry(100, 100, 600, 900)

        # Central widget with frame
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout with margins
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Header frame with image and title
        header_frame = QFrame()
        header_frame.setObjectName("headerFrame")
        header_layout = QVBoxLayout(header_frame)
        header_layout.setContentsMargins(20, 20, 20, 20)

        # Title label
        self.title_label = QLabel("Bubi AI Assistant")
        self.title_label.setObjectName("titleLabel")
        self.title_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(self.title_label)

        # Image
        self.image_label = QLabel()
        self.image_label.setObjectName("imageLabel")
        try:
            pixmap = QPixmap("assets/Bubi.JPG")
            pixmap = pixmap.scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.image_label.setPixmap(pixmap)
            self.image_label.setAlignment(Qt.AlignCenter)
        except:
            self.image_label.setText("🐕 Bubi")
            self.image_label.setAlignment(Qt.AlignCenter)
            self.image_label.setStyleSheet("font-size: 48px; color: #4A90E2;")
        header_layout.addWidget(self.image_label)

        layout.addWidget(header_frame)

        # Chat display frame
        chat_frame = QFrame()
        chat_frame.setObjectName("chatFrame")
        chat_frame_layout = QVBoxLayout(chat_frame)
        chat_frame_layout.setContentsMargins(15, 15, 15, 15)

        # Chat display
        self.chat_display = QTextEdit()
        self.chat_display.setObjectName("chatDisplay")
        self.chat_display.setReadOnly(True)
        self.chat_display.setFont(QFont("Segoe UI", 11))
        chat_frame_layout.addWidget(self.chat_display)

        layout.addWidget(chat_frame)

        # Input frame
        input_frame = QFrame()
        input_frame.setObjectName("inputFrame")
        input_layout = QHBoxLayout(input_frame)
        input_layout.setContentsMargins(15, 15, 15, 15)
        input_layout.setSpacing(10)
        
        # Input field
        self.entry = QLineEdit()
        self.entry.setObjectName("inputField")
        self.entry.setFont(QFont("Segoe UI", 12))
        self.entry.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.entry)

        # Send button
        self.send_button = QPushButton()
        self.send_button.setObjectName("sendButton")
        self.send_button.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.send_button.clicked.connect(self.send_message)
        self.send_button.setFixedSize(120, 45)
        input_layout.addWidget(self.send_button)

        layout.addWidget(input_frame)

        # Language switch button
        self.language_button = QPushButton()
        self.language_button.setObjectName("languageButton")
        self.language_button.setFont(QFont("Segoe UI", 10))
        self.language_button.clicked.connect(self.toggle_language)
        self.language_button.setFixedHeight(35)
        layout.addWidget(self.language_button)

    def apply_styles(self):
        """Apply modern styling to the application."""
        style = """
        QMainWindow {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                      stop:0 #f8f9fa, stop:1 #e9ecef);
        }
        
        #headerFrame {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                      stop:0 #4A90E2, stop:1 #357ABD);
            border-radius: 15px;
            margin: 5px;
        }
        
        #titleLabel {
            color: white;
            font-size: 24px;
            font-weight: bold;
            font-family: 'Segoe UI';
            margin: 10px;
        }
        
        #imageLabel {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            padding: 10px;
            margin: 10px;
        }
        
        #chatFrame {
            background: white;
            border-radius: 12px;
            border: 1px solid #dee2e6;
            margin: 5px;
        }
        
        #chatDisplay {
            background: white;
            border: none;
            border-radius: 8px;
            padding: 15px;
            line-height: 1.4;
            selection-background-color: #4A90E2;
        }
        
        #inputFrame {
            background: white;
            border-radius: 12px;
            border: 1px solid #dee2e6;
            margin: 5px;
        }
        
        #inputField {
            background: #f8f9fa;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            padding: 12px 15px;
            font-size: 12px;
            color: #495057;
        }
        
        #inputField:focus {
            border: 2px solid #4A90E2;
            background: white;
            outline: none;
        }
        
        #sendButton {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                      stop:0 #4A90E2, stop:1 #357ABD);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 12px 20px;
            font-weight: bold;
        }
        
        #sendButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                      stop:0 #357ABD, stop:1 #2E6DA4);
        }
        
        #sendButton:pressed {
            background: #2E6DA4;
            transform: translateY(1px);
        }
        
        #languageButton {
            background: #6c757d;
            color: white;
            border: none;
            border-radius: 8px;
            padding: 8px 15px;
            margin: 5px;
        }
        
        #languageButton:hover {
            background: #5a6268;
        }
        
        #languageButton:pressed {
            background: #545b62;
        }
        
        QScrollBar:vertical {
            background: #f8f9fa;
            width: 12px;
            border-radius: 6px;
        }
        
        QScrollBar::handle:vertical {
            background: #ced4da;
            border-radius: 6px;
            min-height: 20px;
        }
        
        QScrollBar::handle:vertical:hover {
            background: #adb5bd;
        }
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            border: none;
            background: none;
        }
        """
        self.setStyleSheet(style)

    def update_language(self):
        """Update UI elements when switching languages."""
        global language_mode

        if language_mode == 0:
            self.bot_name = "Bubi"
            self.user_prefix = "User: "
            self.bot_prefix = "\nBubi: "
            self.initial_text = "What is your favorite food?"
            self.prompt_text = "You are Bubi, a friendly dog. Respond enthusiastically without parentheses. "
            self.error_message = "\nConnection error: "
            self.button_text = "Send 💬"
            self.language_button.setText("🇩🇪 Switch to German")
            self.title_label.setText("Bubi AI Assistant")
            self.user_display_name = "You"
        else:
            self.bot_name = "Bubi"
            self.user_prefix = "Benutzer: "
            self.bot_prefix = "\nBubi: "
            self.initial_text = "Was ist dein Lieblingsessen?"
            self.prompt_text = "Du bist Bubi, ein freundlicher Hund. Antworte enthusiastisch und ohne Klammern. "
            self.error_message = "\nVerbindungsfehler: "
            self.button_text = "Senden 💬"
            self.language_button.setText("🇬🇧 Wechsel zu Englisch")
            self.title_label.setText("Bubi KI Assistent")
            self.user_display_name = "Du"

        # Update UI elements
        self.entry.setPlaceholderText(self.initial_text)
        self.send_button.setText(self.button_text)

    def toggle_language(self):
        """Toggle between English (0) and German (1)."""
        global language_mode
        language_mode = 1 if language_mode == 0 else 0
        self.update_language()

    def send_message(self):
        user_input = self.entry.text().strip()
        if not user_input:
            return

        # Display user message with styling
        self.chat_display.append(f"<div style='background: #e3f2fd; padding: 10px; margin: 5px 0; border-radius: 8px; border-left: 4px solid #2196f3;'><b>{self.user_display_name}:</b> {user_input}</div>")
        self.chat_history.append(f"{self.user_prefix}{user_input}")
        self.entry.clear()

        # Generate prompt
        history_context = "\n".join(self.chat_history[-5:])
        if language_mode == 0:
            prompt_message = f"{self.prompt_text} Here is our conversation so far:\n{history_context}\n{self.bot_name}:"
        else:
            prompt_message = f"{self.prompt_text} Hier ist unser bisheriges Gespräch:\n{history_context}\n{self.bot_name}:"

        # Start streaming response with styling
        self.chat_display.append("<div style='background: #f3e5f5; padding: 10px; margin: 5px 0; border-radius: 8px; border-left: 4px solid #9c27b0;'><b>Bubi:</b> ")
        self.streaming_thread = StreamingThread(prompt_message)
        self.streaming_thread.text_received.connect(self.append_ai_text)
        self.streaming_thread.response_finished.connect(self.save_ai_response)
        self.streaming_thread.error_occurred.connect(self.handle_error)
        self.streaming_thread.start()

    def append_ai_text(self, text):
        """Append AI text to chat display."""
        cursor = self.chat_display.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(text)
        self.chat_display.setTextCursor(cursor)
        self.chat_display.ensureCursorVisible()

    def save_ai_response(self, full_response):
        """Save the complete AI response to chat history."""
        self.chat_history.append(f"{self.bot_name}: {full_response}")
        # Close the HTML div properly without showing the tags
        cursor = self.chat_display.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertHtml("</div><br>")
        self.chat_display.setTextCursor(cursor)

    def handle_error(self, error):
        """Handle connection errors."""
        self.chat_display.append(f"<div style='background: #ffebee; padding: 10px; margin: 5px 0; border-radius: 8px; border-left: 4px solid #f44336; color: #d32f2f;'><b>Fehler:</b> {error}</div>")

def main():
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Set global font
    font = QFont("Segoe UI", 9)
    app.setFont(font)
    
    window = BubiApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()