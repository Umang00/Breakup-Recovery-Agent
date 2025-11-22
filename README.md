# 💔 Breakup Recovery Squad

### Your AI-Powered Healing Journey Starts Here

**The web app that helps you navigate heartbreak with four AI companions who actually understand.**

[![Try it Live](https://img.shields.io/badge/Try%20it%20Live-Streamlit-FF4B4B?style=for-the-badge&logo=streamlit)](https://umang-breakup-recovery-agent.streamlit.app/)
[![Made with Love](https://img.shields.io/badge/Made%20with-Love-red?style=for-the-badge&logo=heart)](https://github.com/Umang00)
[![Powered by Gemini](https://img.shields.io/badge/Powered%20by-Gemini%202.5-4285F4?style=for-the-badge&logo=google)](https://deepmind.google/technologies/gemini/)

---

## What's New in v1.0

- **Multi-Agent Support** - Four specialized AI agents working together
- **Screenshot Analysis** - Upload chat screenshots for deeper context
- **Curated Music Therapy** - 115 healing songs across 4 eras
- **Privacy-First** - No accounts, no data storage, 100% private
- **Smart Fragments** - Email signup won't interrupt your analysis

**Try Now:** [umang-breakup-recovery-agent.streamlit.app](https://umang-breakup-recovery-agent.streamlit.app/)

---

## What is Breakup Recovery Squad?

An AI-powered web application that helps you emotionally recover from breakups through:

- **Emotional Support** - Get validated, understood, and gently guided forward
- **Closure Tools** - Write unsent letters, perform release rituals, find peace
- **7-Day Recovery Plan** - Progressive challenges with music therapy
- **Honest Feedback** - Objective analysis without the sugarcoating

### Why This Works

| Feature | Benefit |
|---------|---------|
| **4 AI Agents** | Different perspectives for complete support |
| **Multi-Modal** | Analyzes text AND screenshot images |
| **Curated Songs** | 115 therapeutic songs spanning decades |
| **No Account** | Start healing immediately, no barriers |
| **100% Private** | Nothing stored, everything deleted |

---

## Meet Your Recovery Squad

<table>
<tr>
<td width="25%" align="center">

### Maya
**The Therapist**

Warm, empathetic support with gentle humor

*"Your feelings are valid"*

</td>
<td width="25%" align="center">

### Harper
**The Closure Coach**

Unsent letters, rituals, and release exercises

*"Let it go, beautifully"*

</td>
<td width="25%" align="center">

### Jonas
**The Planner**

7-day challenges with music therapy

*"One day at a time"*

</td>
<td width="25%" align="center">

### Riya
**The Truth-Teller**

Honest analysis, patterns, growth areas

*"The truth heals faster"*

</td>
</tr>
</table>

---

## Features

### Multi-Agent AI Support
- **Maya** - Emotional validation, gentle perspective, hope & encouragement
- **Harper** - Unsent message templates, release exercises, closure rituals
- **Jonas** - 7-day progressive challenge, morning/afternoon/evening activities
- **Riya** - Root cause analysis, pattern recognition, actionable growth steps

### Smart Screenshot Analysis
- Upload chat screenshots for context
- AI reads emotional cues from images
- Supports JPG, PNG (up to 10MB each, 5 max)

### Curated Music Therapy
Jonas provides healing playlists from a database of 115 songs:

| Category | Mood | Examples |
|----------|------|----------|
| **Emotional Release** | Sadness, Grief | Driver's License, Someone Like You |
| **Empowerment** | Anger, Confidence | Good 4 U, Flowers, thank u next |
| **Hope & Healing** | Calm, Optimism | Here Comes the Sun, Golden |

Songs span 4 eras: Viral Now (2023-25), Gen Z (2018-22), Streaming Era (2008-17), Classics (Pre-2008)

### Privacy-First Design
- No user accounts required
- No conversation storage
- Screenshots deleted immediately after processing
- No tracking or analytics on your content

---

## Quick Start

### Prerequisites
- Python 3.9+
- Gemini API key ([Get one free](https://makersuite.google.com/app/apikey))

### Installation

```bash
# Clone the repository
git clone https://github.com/Umang00/Breakup-Recovery-Agent.git
cd Breakup-Recovery-Agent

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env and add: DEFAULT_GEMINI_API_KEY=your_key_here

# Run the app
streamlit run ai_breakup_recovery_agent.py
```

The app opens at **http://localhost:8501**

### Optional: Firebase Analytics

For email collection and analytics, set up Firebase:
```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# Add your Firebase service account credentials
```

---

## Tech Stack

### Frontend
| Technology | Purpose |
|------------|---------|
| **Streamlit** | Web framework |
| **Pillow** | Image processing |

### Backend & AI
| Technology | Purpose |
|------------|---------|
| **Agno** | AI agent framework |
| **Google Gemini 2.5 Flash** | Multi-modal AI model |
| **DuckDuckGo** | Web search (Riya agent) |

### Data & Config
| Technology | Purpose |
|------------|---------|
| **Firestore** | Email collection & analytics |
| **PyYAML** | Prompt configuration |
| **python-decouple** | Environment variables |

---

## Configuration

### Environment Variables

```bash
# Required
DEFAULT_GEMINI_API_KEY=your_gemini_key

# Model Settings
GEMINI_MODEL_ID=gemini-2.5-flash-preview-09-2025
GEMINI_TEMPERATURE=0.7
GEMINI_MAX_TOKENS=2000

# Social Links (sidebar)
LINKEDIN_URL=https://linkedin.com/in/yourprofile
WEBSITE_URL=https://yoursite.com
CONTACT_EMAIL=you@example.com
```

### Customizing Prompts

All agent prompts are in `config/prompts.yaml`:

```yaml
agents:
  therapist:
    name: "Maya"
    instructions: "..."  # System prompt
    runtime_prompt: "..."  # User-facing template
```

---

## Project Structure

```
Breakup Recovery Agent/
├── ai_breakup_recovery_agent.py  # Main application
├── config/
│   └── prompts.yaml              # Agent prompts & UI config
├── docs/
│   ├── FEATURES.md               # Feature documentation
│   ├── DECISIONS_AND_ISSUES.md   # Issues & key decisions
│   └── MUSIC_API_NOTES.md        # Music implementation notes
├── .streamlit/
│   └── secrets.toml.example      # Firebase config template
├── .env.example                  # Environment variable template
├── requirements.txt              # Python dependencies
└── README.md                     # You are here!
```

---

## Deployment

### Streamlit Cloud (Recommended)

1. Push to GitHub
2. Connect to [Streamlit Cloud](https://streamlit.io/cloud)
3. Add secrets in app settings:
   - `DEFAULT_GEMINI_API_KEY`
   - `[firebase]` section (optional, for analytics)
4. Deploy!

**Live Demo:** [umang-breakup-recovery-agent.streamlit.app](https://umang-breakup-recovery-agent.streamlit.app/)

---

## Contributing

Want to make this even better?

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a PR

**Ideas welcome:**
- New agent personalities
- Improved prompts
- Additional music categories
- UI enhancements

---

## License

MIT License - Feel free to use, modify, and share!

---

## Star This Repo!

If this helped you heal, give it a star!

Made with love by **Umang**

*Helping hearts heal, one conversation at a time.*

---

## Disclaimer

This application provides AI-generated support and should not replace professional mental health services. If you're experiencing severe emotional distress, please seek help from a qualified mental health professional.

**Crisis Resources:**
- **National Suicide Prevention Lifeline:** 988
- **Crisis Text Line:** Text HOME to 741741
- **International Resources:** [iasp.info/resources/Crisis_Centres](https://www.iasp.info/resources/Crisis_Centres/)

---

**[Try it Live](https://umang-breakup-recovery-agent.streamlit.app/)** | **[Report Issues](https://github.com/Umang00/Breakup-Recovery-Agent/issues)** | **[Star on GitHub](https://github.com/Umang00/Breakup-Recovery-Agent)**
