# 💔 Breakup Recovery Squad

> Helping hearts heal, one conversation at a time

An AI-powered application designed to help you emotionally recover from breakups by providing support, guidance, and emotional outlet through a team of specialized AI agents. Built with **Streamlit** and **Agno**, powered by **Google's Gemini 2.5 Flash**.

**Made with ❤️ by Umang**

---

## ✨ Features

### 🧠 Multi-Agent Support Team
- **Maya:** Provides empathetic support with emotional validation, gentle humor, and relatable experiences
- **Harper:** Creates comprehensive closure toolkits with unsent message templates, release exercises, and rituals
- **Jonas:** Designs personalized 7-day recovery challenges with progressive activities and music playlists
- **Riya:** Offers objective analysis, root cause insights, and actionable growth opportunities

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

### ⚙️ Advanced Prompt Engineering
- **Optimized prompts** using best practices in prompt engineering
- **Structured outputs** with clear formatting and word count guidelines
- **Context-aware** instructions for handling text and image inputs
- **Actionable guidance** with specific, measurable instructions
- All prompts externalized to YAML - customize without code changes

---

## 🚀 Quick Start

### Installation

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/Umang00/Breakup-Recovery-Agent.git
   cd Breakup-Recovery-Agent
   ```

2. **Install Dependencies:**
   
   Using pip:
   ```bash
   pip install -r requirements.txt
   ```
   
   Or using uv (faster):
   ```bash
   uv pip install -r requirements.txt
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

All agent prompts are in `config/prompts.yaml`. The prompts are optimized using advanced prompt engineering techniques:

**What You Can Customize:**
- **Agent Instructions:** Role definitions, core principles, tone guidelines, and safety boundaries
- **Runtime Prompts:** Structured prompts with clear sections, formatting requirements, and word count guidelines
- **UI Elements:** App title, welcome messages, section titles, and loading messages
- **Model Settings:** Model ID, temperature, and token limits
- **Input Limits:** Maximum text length, file size, and file count

**Prompt Engineering Features:**
- Clear role definitions with specific expertise
- Structured output formats with markdown requirements
- Context-aware instructions for multi-modal inputs
- Progressive difficulty (for routine planner)
- Evidence-based suggestions
- Empowerment-focused language

Example:
```yaml
agents:
  therapist:
    instructions:
      - "You are a licensed mental health therapist specializing in relationship recovery..."
      - "Core Principles:"
      - "  1. Active Listening: Acknowledge and validate ALL emotions..."
    runtime_prompt: |
      **Context Analysis:**
      User's emotional state: {user_input}
      
      **Your Task:**
      Provide a compassionate response with:
      1. **Validates Their Feelings** (First paragraph)
      ...
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

### 🤗 Maya
Provides empathetic emotional support with a structured framework:
- **Emotional Validation:** Acknowledges and validates all feelings without judgment
- **Understanding:** Reflects back what you're experiencing and normalizes your pain
- **Gentle Perspective:** Offers insights with appropriate light humor when healing
- **Hope & Encouragement:** Ends with forward-looking, empowering statements
- **Multi-modal Analysis:** Analyzes emotional cues from both text and images

**Response Format:** 150-250 words with clear paragraph structure

### ✍️ Harper
Creates comprehensive closure toolkits with four distinct components:
- **Unsent Message Template:** Fill-in templates for expressing unsent feelings
- **Emotional Release Exercise:** Step-by-step exercises (5-7 steps) with therapeutic benefits
- **Closure Ritual:** Specific, meaningful rituals with symbolism and timing
- **Moving Forward Strategy:** 3-step action plan (immediate, short-term, long-term)

**Response Format:** 300-400 words with clear markdown sections

### 📅 Jonas
Designs personalized 7-day recovery challenges with progressive difficulty:
- **Day-by-Day Breakdown:** Morning, afternoon, and evening activities for each day
- **Progressive Structure:** Days 1-2 (emotional release) → Days 3-4 (movement/connection) → Days 5-6 (confidence building) → Day 7 (celebration)
- **Social Media Detox:** Specific guidelines with limits and alternative activities
- **Healing Playlists:** Three categories (Emotional Release, Empowerment, Hope & Healing) with 5-7 songs each and therapeutic explanations

**Response Format:** 500-700 words with specific, actionable activities

### 💪 Riya
Offers objective, constructive analysis in four comprehensive sections:
- **Objective Analysis:** Facts, patterns, red flags, and contributing factors
- **Root Cause Analysis:** Core issues, communication breakdowns, compatibility problems
- **Growth Opportunities:** Self-awareness, relationship skills, boundaries, values alignment
- **Actionable Steps:** 5-7 specific steps (immediate, short-term, medium-term, long-term, prevention)

**Response Format:** 400-600 words with direct but respectful language

---

## 🎨 Customization

### Changing Agent Behavior

Edit `config/prompts.yaml` to modify agent personalities, instructions, and runtime prompts. The prompts use advanced prompt engineering techniques:

**Key Areas to Customize:**
- **Instructions:** Define role, core principles, tone guidelines, and safety boundaries
- **Runtime Prompts:** Structure the prompts with clear sections, formatting requirements, and word counts
- **Response Format:** Specify markdown formatting, paragraph structure, and length guidelines

Example structure:
```yaml
agents:
  therapist:
    instructions:
      - "You are a licensed mental health therapist..."
      - "Core Principles:"
      - "  1. Active Listening: ..."
      - "Response Structure:"
      - "  - Start with emotional validation..."
    runtime_prompt: |
      **Context Analysis:**
      User's emotional state: {user_input}
      
      **Your Task:**
      Provide a compassionate response that:
      1. **Validates Their Feelings** (First paragraph)
      ...
```

### UI Customization

Update UI elements in `config/prompts.yaml`:

```yaml
ui:
  app_title: "Your Custom Title"
  welcome_message: "Your custom welcome message"
  privacy_notice: "Your custom privacy notice"
  section_titles:
    therapist: "🤗 Your Custom Title"
  loading_messages:
    therapist: "Your loading message..."
```

### Model Configuration

Adjust model settings in `config/prompts.yaml`:

```yaml
model:
  id: "gemini-2.5-flash"  # Change model version
  temperature: 0.7         # Adjust creativity (0.0-1.0)
  max_tokens: 2000         # Maximum response length
```

---

## 📦 Dependencies

All dependencies are pinned for stability:

```
streamlit==1.44.1          # Web framework
pillow==11.1.0             # Image processing
agno==2.2.10               # AI agent framework
google-genai==1.50.1       # Google Gemini API
ddgs                        # DuckDuckGo search (latest)
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
