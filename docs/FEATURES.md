# Breakup Recovery Squad - Feature Documentation

> **Last Updated:** November 2024
> **Version:** 1.0
> **Author:** Umang Thakkar

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [AI Agents](#ai-agents)
4. [Music Recommendations](#music-recommendations)
5. [Analytics & Email Collection](#analytics--email-collection)
6. [User Interface](#user-interface)
7. [Configuration System](#configuration-system)
8. [Security & Privacy](#security--privacy)

---

## Overview

**Breakup Recovery Squad** is an AI-powered web application that helps users navigate through breakups by providing emotional support, practical advice, and personalized recovery plans through four specialized AI agents.

### Tech Stack

| Component | Technology |
|-----------|------------|
| Frontend | Streamlit |
| AI Framework | Agno (with Google Gemini) |
| Database | Google Firestore |
| Analytics | streamlit-analytics2 |
| Deployment | Streamlit Cloud |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Streamlit App                          │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │   Sidebar   │  │    Main     │  │    Agent Response   │  │
│  │             │  │   Content   │  │       Area          │  │
│  │ - About Dev │  │             │  │                     │  │
│  │ - Privacy   │  │ - Input     │  │ - Maya (Therapist)  │  │
│  │ - Waitlist  │  │ - Upload    │  │ - Harper (Closure)  │  │
│  │   (Fragment)│  │ - Submit    │  │ - Jonas (Planner)   │  │
│  └─────────────┘  └─────────────┘  │ - Riya (Honesty)    │  │
│                                     └─────────────────────┘  │
├─────────────────────────────────────────────────────────────┤
│                    streamlit-analytics2                      │
│                  (Wrapped around entire app)                 │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      External Services                       │
├──────────────────┬──────────────────┬───────────────────────┤
│   Google Gemini  │  Google Firestore │    DuckDuckGo API    │
│   (AI Responses) │  (Analytics/Email)│   (Web Search-Riya)  │
└──────────────────┴──────────────────┴───────────────────────┘
```

---

## AI Agents

### How Agents Work

Each agent is built using the **Agno framework** with Google's Gemini model. They receive:
1. User's text input (feelings/situation)
2. Uploaded chat screenshots (optional, processed as images)
3. Curated context (music recommendations for Jonas)

### Agent Profiles

#### 1. Maya (Therapist Agent)
- **Role:** Emotional validation and support
- **Personality:** Warm, empathetic, non-judgmental
- **Output:** Emotional analysis, validation, coping strategies
- **Visual:** Blue border (`#4A90E2`)

#### 2. Harper (Closure Agent)
- **Role:** Help craft unsent messages for emotional release
- **Personality:** Thoughtful, poetic, healing-focused
- **Output:** Draft messages the user might want to say but won't send
- **Visual:** Purple border (`#9B59B6`)

#### 3. Jonas (Routine Planner Agent)
- **Role:** Create personalized 7-day recovery challenge
- **Personality:** Structured, motivating, practical
- **Output:** Day-by-day activities, music recommendations, self-care tips
- **Visual:** Green border (`#2ECC71`)
- **Special Feature:** Receives curated music database for recommendations

#### 4. Riya (Brutal Honesty Agent)
- **Role:** Provide objective, constructive feedback
- **Personality:** Direct but kind, truth-teller
- **Output:** Honest perspective, pattern recognition, growth areas
- **Visual:** Red border (`#E74C3C`)
- **Special Feature:** Has DuckDuckGo search tool for fact-checking

### Agent Configuration

Agents are configured via `config/prompts.yaml`:

```yaml
agents:
  therapist:
    name: "Maya"
    instructions: "..." # System prompt
    runtime_prompt: "..." # User-facing prompt template
```

Model settings can be overridden via environment variables:
- `GEMINI_MODEL_ID` - Model to use (default: gemini-2.5-flash-preview-09-2025)
- `GEMINI_TEMPERATURE` - Creativity (default: 0.7)
- `GEMINI_MAX_TOKENS` - Response length (default: 2000)

---

## Music Recommendations

### Overview

Jonas (Routine Planner) receives a curated database of 115 therapeutic songs to include in recovery plans.

### Database Structure

Songs are organized by:
1. **Category** (3 categories)
   - `release` - Emotional Release (Let It All Out)
   - `empowerment` - Empowerment (Reclaim Your Power)
   - `healing` - Hope & Healing (New Beginnings)

2. **Era** (4 eras per category)
   - `viral_now` - Viral Now (2023-2025)
   - `gen_z` - Gen Z Anthems (2018-2022)
   - `streaming_era` - Streaming Era (2008-2017)
   - `classics` - Timeless Classics (Pre-2008)

### Selection Algorithm

```python
# One song from each era per category = 12 songs total
for category in ['release', 'empowerment', 'healing']:
    for era in ['viral_now', 'gen_z', 'streaming_era', 'classics']:
        selected_song = random.choice(songs[category][era])
```

This ensures:
- Balanced variety across time periods
- Different songs on each run (infinite playlist feel)
- Age-appropriate recommendations for all users

### Why Curated List (Not API)?

We initially implemented Last.fm API integration but removed it because:
- API returned non-English songs (German, French, Korean)
- Obscure artists even with popularity filters
- Inconsistent quality for therapeutic purposes

See `docs/MUSIC_API_NOTES.md` for Last.fm implementation details if you want to revisit.

---

## Analytics & Email Collection

### Analytics (streamlit-analytics2)

**Purpose:** Track user interactions without storing personal data.

**Implementation:**
```python
with streamlit_analytics.track(
    firestore_key_file=get_firestore_key_path(),
    firestore_collection_name="analytics",
    firestore_project_name=project_id
):
    _main_content(...)
```

**What's Tracked:**
- Page views
- Button clicks
- Widget interactions
- Session duration

**Storage:** Google Firestore (`analytics` collection)

### Email Collection (Waitlist)

**Purpose:** Collect emails for upcoming two-way chat feature.

**Implementation:**
- Uses `@st.fragment` decorator to prevent interrupting main app
- Saves to Firestore `subscribers` collection
- Fields: `email`, `subscribed_at`, `source`

**Fragment Pattern:**
```python
@st.fragment
def waitlist_section():
    # Runs independently of main app
    if st.button("Notify Me"):
        save_email_to_firestore(email)
        st.rerun(scope="fragment")  # Only reruns this section
```

### Firestore Authentication

Since Streamlit Cloud uses TOML secrets but libraries expect JSON files:

```python
def get_firestore_key_path():
    # Convert st.secrets["firebase"] dict to temp JSON file
    firebase_secrets = dict(st.secrets["firebase"])
    with open(temp_path, "w") as f:
        json.dump(firebase_secrets, f)
    return temp_path
```

---

## User Interface

### Sidebar Sections

1. **About the Developer**
   - Name, tagline
   - Social links (LinkedIn, Portfolio, Email) as hyperlinks

2. **Privacy & Security**
   - No data storage notice
   - Screenshot handling policy

3. **Join the Waitlist** (Fragment)
   - Email signup for upcoming features
   - Runs independently to not interrupt analysis

### Main Content

1. **Welcome Section**
   - App title and agent introductions

2. **Input Section** (2 columns)
   - Left: Text area for feelings
   - Right: File uploader for screenshots

3. **Response Section**
   - Color-coded borders for each agent
   - Spinner during processing

### Visual Design

| Agent | Color | Hex Code |
|-------|-------|----------|
| Maya | Blue | `#4A90E2` |
| Harper | Purple | `#9B59B6` |
| Jonas | Green | `#2ECC71` |
| Riya | Red | `#E74C3C` |

---

## Configuration System

### Environment Variables (.env)

```bash
# API Key (required)
DEFAULT_GEMINI_API_KEY=your_key_here

# Model Configuration
GEMINI_MODEL_ID=gemini-2.5-flash-preview-09-2025
GEMINI_TEMPERATURE=0.7
GEMINI_MAX_TOKENS=2000

# Social Links
LINKEDIN_URL=https://linkedin.com/in/yourprofile
WEBSITE_URL=https://yourwebsite.com
CONTACT_EMAIL=you@example.com
```

### Streamlit Secrets (.streamlit/secrets.toml)

```toml
[firebase]
type = "service_account"
project_id = "your-project-id"
private_key_id = "..."
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email = "...@....iam.gserviceaccount.com"
# ... other Firebase service account fields
```

### YAML Configuration (config/prompts.yaml)

Contains:
- UI text (titles, messages, privacy notice)
- Agent prompts and instructions
- Default model settings

---

## Security & Privacy

### Data Handling

| Data Type | Stored? | Where | Duration |
|-----------|---------|-------|----------|
| User text input | No | Memory only | Session |
| Screenshots | No | Temp files | Deleted after processing |
| Email (waitlist) | Yes | Firestore | Permanent |
| Analytics | Yes | Firestore | Permanent |
| Conversations | No | Not stored | - |

### Temp File Cleanup

```python
# Registered with atexit for automatic cleanup
atexit.register(cleanup_temp_files)
atexit.register(cleanup_firestore_temp_file)
```

### API Key Security

- Default key stored in environment variables
- Never exposed to frontend
- User API key option removed (was optional, now uses default only)

---

## Features Removed

### 1. User API Key Input
- **What:** Option for users to enter their own Gemini API key
- **Why Removed:** Simplified UX, default key always available
- **Code Removed:** `allow_user_api_key()` function, sidebar API section

### 2. Last.fm API Integration
- **What:** Live music recommendations from Last.fm
- **Why Removed:** Quality issues (non-English songs, obscure artists)
- **Replaced With:** Curated 115-song database
- **Documentation:** `docs/MUSIC_API_NOTES.md`

### 3. Typewriter Effect for Agent Names
- **What:** Animated cycling through Maya, Harper, Jonas, Riya in waitlist
- **Why Removed:** Caused unnecessary reruns, complexity
- **Replaced With:** Static "Maya" reference

### 4. Footer Section
- **What:** "Made with love by Umang" footer with social icons
- **Why Removed:** Moved to sidebar for cleaner layout
- **Issue:** SVG icons rendered as raw code

---

## File Structure

```
Breakup Recovery Agent/
├── ai_breakup_recovery_agent.py  # Main application
├── config/
│   └── prompts.yaml              # Agent prompts & UI config
├── docs/
│   ├── FEATURES.md               # This file
│   ├── DECISIONS_AND_ISSUES.md   # Issues & key decisions
│   └── MUSIC_API_NOTES.md        # Last.fm implementation notes
├── .streamlit/
│   ├── secrets.toml.example      # Firebase config template
│   └── .gitignore                # Protects actual secrets
├── .env.example                  # Environment variable template
├── requirements.txt              # Python dependencies
└── README.md                     # Project overview
```

---

## Quick Reference

### To Run Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your Gemini API key

# Optional: Set up Firestore
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# Edit with Firebase credentials

# Run
streamlit run ai_breakup_recovery_agent.py
```

### To Deploy on Streamlit Cloud

1. Push to GitHub
2. Connect repo to Streamlit Cloud
3. Add secrets in app settings:
   - `DEFAULT_GEMINI_API_KEY`
   - `[firebase]` section (if using analytics)

---

*This documentation is auto-generated and maintained alongside the codebase.*
