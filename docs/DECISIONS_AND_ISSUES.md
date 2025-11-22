# Breakup Recovery Squad - Decisions & Issues Log

> **Last Updated:** November 2024
> **Purpose:** Document key decisions, issues faced, and their solutions for future reference

---

## Table of Contents

1. [Framework Selection](#framework-selection)
2. [Issues & Solutions](#issues--solutions)
3. [Key Decisions](#key-decisions)
4. [Features Removed](#features-removed)
5. [Known Limitations](#known-limitations)

---

## Framework Selection

### Why Streamlit?

**Chosen:** Streamlit
**Alternatives Considered:** Flask + React, Gradio, Panel

**Pros:**
- Rapid prototyping - Python only, no frontend code needed
- Built-in widgets for forms, file uploads, spinners
- Free deployment on Streamlit Cloud
- Native support for session state
- Easy integration with AI/ML libraries

**Cons (Limitations):**
- Full script reruns on every widget interaction
- Limited control over UI/UX (no custom CSS without hacks)
- Performance overhead - slow initial load (11s LCP observed)
- Cannot run JavaScript
- Fragment support is limited (no `st.sidebar` inside fragments)

### Why Agno + Google Gemini?

**Chosen:** Agno framework with Google Gemini models

**Reasons:**
- Agno provides clean agent abstraction with tool support
- Gemini offers free tier with generous limits
- Multi-modal support (text + images) for screenshot analysis
- Easy integration with DuckDuckGo search for Riya agent

---

## Issues & Solutions

### Issue 1: Email Submission Interrupts Agent Analysis

**Problem:**
When users submitted their email to join waitlist while agents were processing, the entire Streamlit app would rerun, stopping the analysis mid-way.

**Root Cause:**
Streamlit's execution model - the entire script reruns on ANY widget interaction (button click, form submit, etc.).

**Solution:**
Implemented `@st.fragment` decorator for the waitlist section:

```python
@st.fragment
def waitlist_section():
    # This section now reruns independently
    if st.button("Notify Me"):
        save_email_to_firestore(email)
        st.rerun(scope="fragment")  # Only reruns this fragment
```

**Key Learning:**
- Fragments allow isolated reruns since Streamlit 1.37.0
- Cannot use `st.sidebar` inside a fragment - must call fragment from within sidebar context
- Use `st.rerun(scope="fragment")` not `st.rerun()`

---

### Issue 2: SVG Icons Rendering as Raw Code

**Problem:**
Footer section with social media icons displayed raw SVG/HTML code instead of rendering the icons.

**Attempted Solution:**
```python
st.markdown("""
<a href="..."><svg>...</svg></a>
""", unsafe_allow_html=True)
```

**What Happened:**
SVG code appeared as text in the UI instead of rendering as icons.

**Final Solution:**
Removed footer entirely. Moved social links to sidebar using simple markdown hyperlinks:

```python
st.markdown(f"[LinkedIn]({linkedin_url}) · [Portfolio]({website_url}) · [Email](mailto:{email})")
```

**Key Learning:**
- Streamlit's HTML rendering is inconsistent with complex SVG
- Simple markdown links are more reliable and maintainable
- Less is more - hyperlinks work everywhere

---

### Issue 3: Music API Returning Non-English/Obscure Songs

**Problem:**
Last.fm API integration returned:
- Non-English songs (German, French, Korean)
- Obscure artists even with popularity filters
- Inconsistent quality for therapeutic purposes

**Attempted Solutions:**
1. Added popularity threshold (>500 listeners)
2. Tried filtering by tags
3. Tested different API endpoints

**Final Solution:**
Replaced API with curated 115-song database organized by:
- 3 categories (release, empowerment, healing)
- 4 eras per category (viral_now, gen_z, streaming_era, classics)

**Key Learning:**
- For therapeutic/emotional content, curation > automation
- APIs are great for discovery, not quality control
- Static data can still feel dynamic with random selection

---

### Issue 4: Function Signature Mismatch After Refactor

**Problem:**
```
ERROR: get_music_recommendations_text() got an unexpected keyword argument 'songs_per_category'
```

**Root Cause:**
Changed function signature during music database refactor but forgot to update call site.

**Solution:**
Removed the argument from the call:
```python
# Before (broken)
music_context = get_music_recommendations_text(songs_per_category=5)

# After (fixed)
music_context = get_music_recommendations_text()
```

**Key Learning:**
- Always grep for function name after changing signatures
- Consider using IDE refactoring tools
- Test after every change, not just at the end

---

### Issue 5: Firestore Authentication on Streamlit Cloud

**Problem:**
Streamlit Cloud uses TOML secrets (`st.secrets`), but Firestore libraries expect JSON key files.

**Solution:**
Created a converter function:

```python
def get_firestore_key_path():
    firebase_secrets = dict(st.secrets["firebase"])
    temp_path = os.path.join(tempfile.gettempdir(), "firebase_key.json")
    with open(temp_path, "w") as f:
        json.dump(firebase_secrets, f)
    return temp_path
```

**Key Learning:**
- Streamlit Cloud secrets are dictionaries, not files
- Temp files need cleanup (use `atexit.register`)
- Cache the Firestore client with `@st.cache_resource`

---

### Issue 6: Slow Initial Page Load

**Problem:**
Lighthouse reported:
- LCP: 11.0s (poor)
- Speed Index: 7.4s
- Time to Interactive: 2.9s

**Root Cause:**
Streamlit framework overhead - not application code.

**Attempted Mitigations:**
- Lazy loading where possible
- Caching with `@st.cache_resource`
- Minimizing imports

**Current Status:**
Accepted as Streamlit limitation. Trade-off for rapid development.

**Key Learning:**
- Streamlit is not optimized for performance
- For production apps needing speed, consider Flask/FastAPI + React
- Focus on functionality first, optimize later if needed

---

## Key Decisions

### Decision 1: Remove User API Key Option

**What:** Originally allowed users to enter their own Gemini API key.

**Decision:** Removed this feature, use only default key.

**Reasoning:**
- Simplified UX - one less step for users
- Default key always available
- Users don't need to understand API keys
- Security - users might accidentally share keys

---

### Decision 2: Curated Songs Over API

**What:** Replace Last.fm API with static curated database.

**Decision:** 115 songs manually curated, organized by category and era.

**Reasoning:**
- Quality control for therapeutic context
- No API rate limits or failures
- Predictable, tested recommendations
- Still feels dynamic with random selection per era

---

### Decision 3: Fragment for Waitlist Only

**What:** Which sections to make fragments.

**Decision:** Only waitlist section uses `@st.fragment`.

**Reasoning:**
- Waitlist is the only interactive section during analysis
- More fragments = more complexity
- Keep it simple until more issues arise

---

### Decision 4: Social Links in Sidebar, Not Footer

**What:** Where to display developer social links.

**Decision:** Moved from footer to sidebar.

**Reasoning:**
- SVG icons didn't render properly in footer
- Sidebar is always visible
- Cleaner main content area
- Simple hyperlinks more reliable than icons

---

### Decision 5: Environment Variables for All Config

**What:** How to manage configuration.

**Decision:**
- API keys → Environment variables / Streamlit secrets
- Prompts → YAML file
- Model settings → Environment variables with defaults

**Reasoning:**
- Separation of secrets from code
- Easy deployment across environments
- YAML for long text (prompts) is more readable
- Defaults ensure app works out of the box

---

## Features Removed

| Feature | Why Added | Why Removed |
|---------|-----------|-------------|
| User API Key Input | Flexibility | Unnecessary complexity, default key works |
| Last.fm API | Dynamic recommendations | Quality issues, non-English songs |
| Typewriter Effect | Fun animation | Caused reruns, added complexity |
| Footer Section | Developer attribution | SVG rendering issues, moved to sidebar |
| `songs_per_category` param | Customization | Simplified to fixed selection logic |

---

## Known Limitations

### Streamlit Limitations

1. **Full Reruns:** Every interaction reruns entire script
2. **No Custom CSS:** Limited styling options
3. **Slow Load:** Framework overhead causes 5-10s initial load
4. **No Background Tasks:** Can't run async operations easily
5. **Fragment Restrictions:** Can't use `st.sidebar` inside fragments

### Application Limitations

1. **No Conversation Memory:** Each submission is independent
2. **No User Accounts:** Can't save progress or history
3. **English Only:** Agents respond in English only
4. **Image Limit:** Streamlit has file upload size limits
5. **No Mobile Optimization:** Responsive but not mobile-first

### Future Considerations

If rebuilding or scaling:
- Consider Flask/FastAPI + React for better performance
- Add database for conversation history
- Implement proper user authentication
- Add rate limiting for API calls
- Consider WebSocket for real-time chat

---

*This document should be updated whenever significant decisions are made or issues are resolved.*
