# 💔 Breakup Recovery Squad

> Helping hearts heal, one conversation at a time

An AI-powered application designed to help you emotionally recover from breakups by providing support, guidance, and emotional outlet through a team of specialized AI agents. Built with **Streamlit** and **Agno**, powered by **Google's Gemini 2.5 Flash**.

**Made with ❤️ by Umang**

---

## ✨ Features

### 🧠 Multi-Agent Support Team
- **Therapist Agent:** Offers empathetic support and coping strategies
- **Closure Agent:** Helps you write emotional messages for cathartic release
- **Routine Planner Agent:** Creates personalized 7-day recovery plans
- **Brutal Honesty Agent:** Provides direct, objective feedback when you need it

### 🔒 Privacy-First Design
- **No user accounts** - Start immediately without registration
- **No data storage** - Your conversations are never saved on our servers
- **Automatic cleanup** - Screenshots are temporarily processed and immediately deleted
- **Local processing** - Everything happens in your browser session
- **No tracking** - We don't collect analytics or personal information

### 📷 Smart Chat Analysis
- Upload screenshots of your conversations for deeper context
- AI analyzes both text and visual emotional cues
- Supports JPG, JPEG, and PNG formats (up to 10MB each)

### 🔑 Flexible API Key Management
- **Easy setup** - Use default API key (if configured) to start instantly
- **Bring your own** - Option to use your personal Gemini API key
- **Secure handling** - Keys are password-masked and never logged

### ⚙️ Configurable Prompts
- All AI prompts externalized to YAML configuration
- Easy to customize agent personalities and behaviors
- No code changes required to tune responses

---

## 🚀 Quick Start

### Installation

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/Umang00/Breakup-Recovery-Agent.git
   cd Breakup-Recovery-Agent
   ```

2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure API Key (Optional):**

   If you want to provide a default API key so users don't need their own:

   ```bash
   cp .env.example .env
   # Edit .env and add your Gemini API key
   ```

   Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)

4. **Run the Application:**
   ```bash
   streamlit run ai_breakup_recovery_agent.py
   ```

5. **Open your browser** to `http://localhost:8501`

---

## 🛠️ Configuration

### Environment Variables (`.env`)

```bash
# Optional: Provide a default Gemini API key
DEFAULT_GEMINI_API_KEY=your_key_here

# Optional: Allow users to use their own API key (true/false)
ALLOW_USER_API_KEY=true
```

### Customizing Prompts

All agent prompts are in `config/prompts.yaml`. You can customize:

- Agent instructions (personality and behavior)
- Runtime prompts (what they ask the AI)
- UI text and loading messages
- Input limits and model settings

Example:
```yaml
agents:
  therapist:
    instructions:
      - "You are an empathetic therapist that:"
      - "1. Listens with empathy and validates feelings"
      # Add or modify instructions here
```

---

## 📋 Usage

1. **Enter Your Feelings** - Share what you're going through in the text area
2. **Upload Screenshots (Optional)** - Add chat screenshots for context
3. **Get Your Recovery Plan** - Click the button to receive personalized support from all four agents
4. **Follow the Guidance** - Review emotional support, closure exercises, recovery routines, and honest feedback

---

## 🧑‍💻 Technical Stack

- **Frontend:** Streamlit (Python)
- **AI Framework:** Agno
- **AI Model:** Google Gemini 2.5 Flash
- **Image Processing:** Pillow + Agno Image
- **Configuration:** PyYAML, python-decouple
- **Search Integration:** DuckDuckGo (for Brutal Honesty Agent)

---

## 🔐 Privacy & Security

We take your privacy seriously:

- ✅ **No user accounts or authentication** - Use anonymously
- ✅ **No server-side data storage** - Conversations aren't saved
- ✅ **Automatic file cleanup** - Uploaded images deleted after processing
- ✅ **Input validation** - Protection against injection attacks
- ✅ **Secure API key handling** - Keys are masked and never exposed
- ✅ **No third-party tracking** - No analytics or cookies

### Security Features

- Input sanitization to prevent prompt injection
- File size limits (10MB per file, 5 files max)
- Text length limits (5000 characters)
- Automatic cleanup of temporary files
- Error handling to prevent information leakage

---

## 🎯 Agents Overview

### 🤗 Therapist Agent
Provides empathetic emotional support with:
- Validation of your feelings
- Gentle, comforting words
- Relatable breakup experiences
- Encouragement and hope

### ✍️ Closure Agent
Helps you find closure through:
- Templates for unsent messages
- Emotional release exercises
- Closure rituals and practices
- Strategies for moving forward

### 📅 Routine Planner Agent
Creates personalized recovery plans with:
- 7-day daily activity challenges
- Self-care routines
- Social media detox strategies
- Mood-lifting music suggestions

### 💪 Brutal Honesty Agent
Offers direct, unfiltered feedback:
- Objective analysis of the situation
- Clear explanations of what went wrong
- Growth opportunities
- Actionable steps for the future

---

## 🎨 Customization

### Changing Agent Behavior

Edit `config/prompts.yaml` to modify:

```yaml
agents:
  therapist:
    instructions:
      - "Your custom instructions here"
    runtime_prompt: |
      Your custom prompt template here
      User input: {user_input}
```

### UI Customization

Update UI elements in `config/prompts.yaml`:

```yaml
ui:
  app_title: "Your Custom Title"
  welcome_message: "Your custom welcome message"
  privacy_notice: "Your custom privacy notice"
```

---

## 📦 Dependencies

All dependencies are pinned for stability:

```
streamlit==1.44.1          # Web framework
pillow==11.1.0             # Image processing
agno==2.2.10               # AI agent framework
google-genai==1.50.1       # Google Gemini API
ddgs==0.2.0                # DuckDuckGo search
python-decouple==3.8       # Environment config
PyYAML==6.0.2              # YAML parsing
```

---

## 🤝 Contributing

Contributions are welcome! Feel free to:

- Report bugs
- Suggest new features
- Improve prompts and agent behaviors
- Enhance privacy and security
- Improve documentation

---

## 📝 License

This project is open source and available under the MIT License.

---

## 🙏 Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Powered by [Google Gemini](https://deepmind.google/technologies/gemini/)
- Agent framework by [Agno](https://github.com/agno-ai/agno)

---

## 💬 Support

If you find this helpful, please:
- ⭐ Star this repository
- 🐛 Report issues
- 💡 Share your feedback
- 🤝 Contribute improvements

---

**Made with ❤️ by Umang** | Helping hearts heal, one conversation at a time

---

## ⚠️ Disclaimer

This application provides AI-generated support and should not replace professional mental health services. If you're experiencing severe emotional distress, please seek help from a qualified mental health professional.

**Crisis Resources:**
- National Suicide Prevention Lifeline: 988
- Crisis Text Line: Text HOME to 741741
- International Association for Suicide Prevention: https://www.iasp.info/resources/Crisis_Centres/
