# Bubi AI Chat

An interactive chat client featuring a friendly dog personality named Bubi. The application supports both English and German.
![Bildschirmfoto 2025-06-02 um 13 47 43](https://github.com/user-attachments/assets/3275009e-a629-424f-8184-5aa826b204e7)

## Features

- Interactive chat with Bubi
- Bilingual support (English/German)
- Real-time streaming of responses
- User-friendly GUI with PyQt5
- Conversation history
- Secure API key management

## Requirements

- Python 3.x
- Ollama (installed locally)
- Mistral model in Ollama (or DeepSeek R1, see below)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/YourUsername/Bubi-AI.git
cd Bubi-AI
```

2. Install the required Python packages:
```bash
pip install -r requirements.txt
```

3. **Configure Environment Variables** (for DeepSeek API):
   - Copy the example environment file:
     ```bash
     cp .env.example .env
     ```
   - Edit `.env` and add your DeepSeek API key:
     ```
     DEEPSEEK_API_KEY=your_actual_api_key_here
     ```

4. Make sure Ollama is installed and running:
```bash
ollama run mistral
```

## Usage

### Main Chat Application

1. Start the application:
```bash
python main.py
```

2. Enter your message in the text field and press Enter or click "Talk to Bubi!"

3. Use the language switch button to toggle between English and German.

### DeepSeek API Test

To test the DeepSeek API integration:
```bash
python deepseek_simple.py
```

**⚠️ Important:** Make sure your `.env` file is properly configured with your DeepSeek API key before running this test.

## Project Structure

- `main.py` - Main PyQt5 application file
- `deepseek_simple.py` - DeepSeek API test script
- `assets/` - Directory for images and other resources
- `requirements.txt` - Python dependencies
- `.env` - Environment variables (not tracked in git)
- `.env.example` - Example environment configuration

## Security

- API keys are stored in `.env` file (automatically ignored by git)
- Never commit your actual API keys to the repository
- Use `.env.example` as a template for required environment variables

## License

MIT

## Connecting with DeepSeek R1

You can also use this project with the DeepSeek R1 model. To do so, change the model name in the API request in `main.py`:

```python
response = requests.post(
    "http://localhost:11434/api/generate",
    json={"model": "deepseek-coder:latest",  # or the name of your DeepSeek R1 model
          "prompt": prompt_message,
          "stream": True}
)
```

Make sure the DeepSeek R1 model is installed and running in Ollama:

```bash
ollama run deepseek-coder:latest
```

For more information on using DeepSeek R1 with Ollama, refer to the official documentation of Ollama and DeepSeek.
