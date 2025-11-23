from agno.agent import Agent
from agno.models.google import Gemini
from agno.media import Image as AgnoImage
from agno.tools.duckduckgo import DuckDuckGoTools
import streamlit as st
from typing import List, Optional, Dict, Any
import logging
from pathlib import Path
import tempfile
import os
import yaml
import random
import json
import re
from decouple import config as env_config, UndefinedValueError
import atexit
import streamlit_analytics2 as streamlit_analytics
from google.cloud import firestore
from google.oauth2 import service_account

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
CONFIG_PATH = Path(__file__).parent / "config" / "prompts.yaml"
MAX_INPUT_LENGTH = 5000
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
MAX_FILES = 5

# Track temp files for cleanup
temp_files_created = []

# Firestore credentials temp file path
_firestore_temp_key_path = None


def has_firebase_secrets() -> bool:
    """Quick check if Firebase secrets are configured without accessing them."""
    try:
        return "firebase" in st.secrets
    except Exception:
        return False


def get_firestore_key_path() -> Optional[str]:
    """
    Creates a temporary JSON file from st.secrets["firebase"] for Firestore authentication.
    Required because streamlit-analytics2 expects a file path, not a dict.
    Returns the path to the temporary credentials file, or None if secrets not configured.
    Uses caching to avoid repeated file creation.
    """
    global _firestore_temp_key_path

    # Return cached path if already created
    if _firestore_temp_key_path and os.path.exists(_firestore_temp_key_path):
        return _firestore_temp_key_path

    # Quick check before accessing secrets
    if not has_firebase_secrets():
        return None

    try:
        # Convert st.secrets["firebase"] to a dictionary
        firebase_secrets = dict(st.secrets["firebase"])

        # Create a temporary file for the credentials
        temp_dir = tempfile.gettempdir()
        _firestore_temp_key_path = os.path.join(temp_dir, "firestore_key_temp.json")

        # Write the credentials to the temp file
        with open(_firestore_temp_key_path, "w") as f:
            json.dump(firebase_secrets, f)

        logger.info("Firestore credentials temp file created successfully")
        return _firestore_temp_key_path

    except Exception as e:
        logger.error(f"Error creating Firestore credentials file: {str(e)}")
        return None


@st.cache_resource
def get_firestore_client() -> Optional[firestore.Client]:
    """
    Creates a Firestore client using credentials from st.secrets.
    Returns None if credentials are not configured.
    Uses Streamlit caching to avoid recreating client on every call.
    """
    try:
        if not has_firebase_secrets():
            return None

        # Create credentials from the secrets dictionary
        firebase_secrets = dict(st.secrets["firebase"])
        creds = service_account.Credentials.from_service_account_info(firebase_secrets)

        # Create and return the Firestore client
        db = firestore.Client(credentials=creds, project=firebase_secrets.get("project_id"))
        logger.info("Firestore client created and cached")
        return db

    except Exception as e:
        logger.error(f"Error creating Firestore client: {str(e)}")
        return None


def save_email_to_firestore(email: str) -> bool:
    """
    Saves an email address to the Firestore 'subscribers' collection.
    Returns True if successful, False otherwise.
    """
    try:
        db = get_firestore_client()
        if db is None:
            logger.error("Could not connect to Firestore")
            return False

        # Validate email format
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            logger.warning(f"Invalid email format: {email}")
            return False

        # Save to Firestore with server timestamp
        doc_ref = db.collection("subscribers").document()
        doc_ref.set({
            "email": email.lower().strip(),
            "subscribed_at": firestore.SERVER_TIMESTAMP,
            "source": "breakup_recovery_app"
        })

        logger.info(f"Email saved to Firestore: {email}")
        return True

    except Exception as e:
        logger.error(f"Error saving email to Firestore: {str(e)}")
        return False


def cleanup_firestore_temp_file():
    """Clean up the temporary Firestore credentials file"""
    global _firestore_temp_key_path
    if _firestore_temp_key_path and os.path.exists(_firestore_temp_key_path):
        try:
            os.remove(_firestore_temp_key_path)
            logger.info("Firestore temp credentials file cleaned up")
        except Exception as e:
            logger.error(f"Error cleaning up Firestore temp file: {str(e)}")
        _firestore_temp_key_path = None


# Register cleanup for Firestore temp file
atexit.register(cleanup_firestore_temp_file)


def get_social_urls() -> Dict[str, str]:
    """Get social media URLs from environment variables"""
    return {
        "linkedin": env_config("LINKEDIN_URL", default=""),
        "website": env_config("WEBSITE_URL", default=""),
        "email": env_config("CONTACT_EMAIL", default="")
    }


# Curated Music Database - 115 songs organized by category and era
# Structure: Category -> Era -> Songs (enables balanced selection across time periods)
CURATED_SONGS = {
    "release": {
        "name": "Emotional Release",
        "ui_header": "Let It All Out",
        "description": "Sadness, Grief, Crying, Catharsis",
        "eras": {
            "viral_now": {
                "name": "Viral Now (2023-2025)",
                "songs": [
                    {"title": "What Was I Made For?", "artist": "Billie Eilish", "tag": "Existential Sadness"},
                    {"title": "Die With A Smile", "artist": "Lady Gaga & Bruno Mars", "tag": "Power Ballad"},
                    {"title": "Vampire", "artist": "Olivia Rodrigo", "tag": "Betrayal"},
                    {"title": "The Smallest Man Who Ever Lived", "artist": "Taylor Swift", "tag": "Anger/Grief"},
                    {"title": "Casual", "artist": "Chappell Roan", "tag": "Situationship Pain"}
                ]
            },
            "gen_z": {
                "name": "Gen Z Anthems (2018-2022)",
                "songs": [
                    {"title": "Driver's License", "artist": "Olivia Rodrigo", "tag": "Modern Classic"},
                    {"title": "Glimpse of Us", "artist": "Joji", "tag": "Melancholy"},
                    {"title": "Liability", "artist": "Lorde", "tag": "Introspective"},
                    {"title": "Happier Than Ever", "artist": "Billie Eilish", "tag": "Build-up/Release"},
                    {"title": "Traitor", "artist": "Olivia Rodrigo", "tag": "Betrayal"},
                    {"title": "Listen before i go", "artist": "Billie Eilish", "tag": "Heavy/Slow"},
                    {"title": "Falling", "artist": "Harry Styles", "tag": "Ballad"},
                    {"title": "Lose You to Love Me", "artist": "Selena Gomez", "tag": "Closure"}
                ]
            },
            "streaming_era": {
                "name": "Streaming Era (2008-2017)",
                "songs": [
                    {"title": "All Too Well (10 Minute Version)", "artist": "Taylor Swift", "tag": "Storytelling"},
                    {"title": "Someone Like You", "artist": "Adele", "tag": "Ballad"},
                    {"title": "Back to Black", "artist": "Amy Winehouse", "tag": "Soul/Grief"},
                    {"title": "Skinny Love", "artist": "Bon Iver", "tag": "Indie Folk"},
                    {"title": "Stay", "artist": "Rihanna ft. Mikky Ekko", "tag": "Vulnerable"},
                    {"title": "Say Something", "artist": "A Great Big World", "tag": "Giving Up"},
                    {"title": "Jealous", "artist": "Labrinth", "tag": "Deep Sadness"},
                    {"title": "The Night We Met", "artist": "Lord Huron", "tag": "Haunting"},
                    {"title": "Stone Cold", "artist": "Demi Lovato", "tag": "Vocals"}
                ]
            },
            "classics": {
                "name": "Timeless Classics (Pre-2008)",
                "songs": [
                    {"title": "Fix You", "artist": "Coldplay", "tag": "Comfort"},
                    {"title": "Nothing Compares 2 U", "artist": "Sinéad O'Connor", "tag": "Classic"},
                    {"title": "Un-break My Heart", "artist": "Toni Braxton", "tag": "R&B Classic"},
                    {"title": "Creep", "artist": "Radiohead", "tag": "Alternative"},
                    {"title": "One More Light", "artist": "Linkin Park", "tag": "Mourning"},
                    {"title": "Let Her Go", "artist": "Passenger", "tag": "Acoustic"},
                    {"title": "Bleeding Love", "artist": "Leona Lewis", "tag": "2000s Pop"},
                    {"title": "Jar of Hearts", "artist": "Christina Perri", "tag": "Angsty"},
                    {"title": "Dancing On My Own", "artist": "Robyn", "tag": "Sad Disco"}
                ]
            }
        }
    },
    "empowerment": {
        "name": "Empowerment",
        "ui_header": "Reclaim Your Power",
        "description": "Anger, Confidence, Energy, Ego-Boost",
        "eras": {
            "viral_now": {
                "name": "Viral Now (2023-2025)",
                "songs": [
                    {"title": "Espresso", "artist": "Sabrina Carpenter", "tag": "Confidence"},
                    {"title": "Good Luck, Babe!", "artist": "Chappell Roan", "tag": "Sassy/80s Vibe"},
                    {"title": "Flowers", "artist": "Miley Cyrus", "tag": "Self-Care"},
                    {"title": "we can't be friends", "artist": "Ariana Grande", "tag": "Moving On"},
                    {"title": "Greedy", "artist": "Tate McRae", "tag": "Ego Boost"}
                ]
            },
            "gen_z": {
                "name": "Gen Z Anthems (2018-2022)",
                "songs": [
                    {"title": "Good 4 U", "artist": "Olivia Rodrigo", "tag": "Pop Punk"},
                    {"title": "Don't Start Now", "artist": "Dua Lipa", "tag": "Moving On"},
                    {"title": "thank u, next", "artist": "Ariana Grande", "tag": "Gratitude"},
                    {"title": "Truth Hurts", "artist": "Lizzo", "tag": "Sassy"},
                    {"title": "Good as Hell", "artist": "Lizzo", "tag": "Mood Booster"},
                    {"title": "New Rules", "artist": "Dua Lipa", "tag": "Guidebook"},
                    {"title": "Confident", "artist": "Demi Lovato", "tag": "Ego"},
                    {"title": "Look What You Made Me Do", "artist": "Taylor Swift", "tag": "Revenge"}
                ]
            },
            "streaming_era": {
                "name": "Streaming Era (2008-2017)",
                "songs": [
                    {"title": "Shake It Off", "artist": "Taylor Swift", "tag": "Fun"},
                    {"title": "Roar", "artist": "Katy Perry", "tag": "Anthem"},
                    {"title": "Titanium", "artist": "David Guetta ft. Sia", "tag": "Unbreakable"},
                    {"title": "Stronger (What Doesn't Kill You)", "artist": "Kelly Clarkson", "tag": "Resilience"},
                    {"title": "We Are Never Ever Getting Back Together", "artist": "Taylor Swift", "tag": "Definitive"},
                    {"title": "Rolling in the Deep", "artist": "Adele", "tag": "Power"},
                    {"title": "Love Myself", "artist": "Hailee Steinfeld", "tag": "Self-Love"},
                    {"title": "Shout Out to My Ex", "artist": "Little Mix", "tag": "Group Anthem"},
                    {"title": "Girl on Fire", "artist": "Alicia Keys", "tag": "Inspirational"}
                ]
            },
            "classics": {
                "name": "Timeless Classics (Pre-2008)",
                "songs": [
                    {"title": "Since U Been Gone", "artist": "Kelly Clarkson", "tag": "Rock Pop"},
                    {"title": "I Will Survive", "artist": "Gloria Gaynor", "tag": "Disco Classic"},
                    {"title": "Single Ladies", "artist": "Beyoncé", "tag": "Upbeat"},
                    {"title": "Irreplaceable", "artist": "Beyoncé", "tag": "R&B Classic"},
                    {"title": "Before He Cheats", "artist": "Carrie Underwood", "tag": "Revenge/Country"},
                    {"title": "You Oughta Know", "artist": "Alanis Morissette", "tag": "90s Rage"},
                    {"title": "Survivor", "artist": "Destiny's Child", "tag": "Independence"},
                    {"title": "So What", "artist": "P!nk", "tag": "Rock Attitude"},
                    {"title": "Respect", "artist": "Aretha Franklin", "tag": "Soul Classic"},
                    {"title": "Independent Women, Pt. 1", "artist": "Destiny's Child", "tag": "Throwback"}
                ]
            }
        }
    },
    "healing": {
        "name": "Hope & Healing",
        "ui_header": "New Beginnings",
        "description": "Calm, Optimism, Sunshine, Peace",
        "eras": {
            "viral_now": {
                "name": "Viral Now (2023-2025)",
                "songs": [
                    {"title": "Birds of a Feather", "artist": "Billie Eilish", "tag": "Light/Love"},
                    {"title": "Too Sweet", "artist": "Hozier", "tag": "Groove/Self-Worth"},
                    {"title": "Golden Hour", "artist": "JVKE", "tag": "Modern Piano"},
                    {"title": "Texas Hold 'Em", "artist": "Beyoncé", "tag": "Fun/Country"},
                    {"title": "Training Season", "artist": "Dua Lipa", "tag": "Standards"}
                ]
            },
            "gen_z": {
                "name": "Gen Z Anthems (2018-2022)",
                "songs": [
                    {"title": "Answer: Love Myself", "artist": "BTS", "tag": "K-Pop/Self-Love"},
                    {"title": "Rainbow", "artist": "Kacey Musgraves", "tag": "After the Storm"},
                    {"title": "comethru", "artist": "Jeremy Zucker", "tag": "Gen Z Chill"},
                    {"title": "Matilda", "artist": "Harry Styles", "tag": "Letting Go"},
                    {"title": "Solar Power", "artist": "Lorde", "tag": "Summer Vibe"},
                    {"title": "Scars to Your Beautiful", "artist": "Alessia Cara", "tag": "Validation"},
                    {"title": "Better Now", "artist": "Post Malone", "tag": "Peaceful Rap"},
                    {"title": "Levitating", "artist": "Dua Lipa", "tag": "Dance"}
                ]
            },
            "streaming_era": {
                "name": "Streaming Era (2008-2017)",
                "songs": [
                    {"title": "Clean", "artist": "Taylor Swift", "tag": "Recovery"},
                    {"title": "Rise Up", "artist": "Andra Day", "tag": "Strength"},
                    {"title": "Unwritten", "artist": "Natasha Bedingfield", "tag": "Freedom"},
                    {"title": "Pocketful of Sunshine", "artist": "Natasha Bedingfield", "tag": "Nostalgia"},
                    {"title": "The Climb", "artist": "Miley Cyrus", "tag": "Journey"},
                    {"title": "Brave", "artist": "Sara Bareilles", "tag": "Courage"},
                    {"title": "Just the Way You Are", "artist": "Bruno Mars", "tag": "Sweet"},
                    {"title": "Firework", "artist": "Katy Perry", "tag": "Uplifting"},
                    {"title": "Dog Days Are Over", "artist": "Florence + The Machine", "tag": "Euphoria"}
                ]
            },
            "classics": {
                "name": "Timeless Classics (Pre-2008)",
                "songs": [
                    {"title": "Here Comes the Sun", "artist": "The Beatles", "tag": "Sunshine"},
                    {"title": "Vienna", "artist": "Billy Joel", "tag": "Perspective"},
                    {"title": "Put Your Records On", "artist": "Corinne Bailey Rae", "tag": "Chill"},
                    {"title": "Three Little Birds", "artist": "Bob Marley", "tag": "Reassurance"},
                    {"title": "Beautiful Day", "artist": "U2", "tag": "Classic Rock"},
                    {"title": "I'm Still Standing", "artist": "Elton John", "tag": "Upbeat Classic"},
                    {"title": "Landslide", "artist": "Fleetwood Mac", "tag": "Reflection"},
                    {"title": "Lovely Day", "artist": "Bill Withers", "tag": "Groove"},
                    {"title": "What a Wonderful World", "artist": "Louis Armstrong", "tag": "Gratitude"},
                    {"title": "Fast Car", "artist": "Tracy Chapman", "tag": "Storytelling"}
                ]
            }
        }
    }
}

# Era IDs for balanced selection
ERA_IDS = ["viral_now", "gen_z", "streaming_era", "classics"]


def get_music_recommendations_text() -> str:
    """
    Get formatted music recommendations text for LLM context.
    Selects one song from each era per category for balanced variety across time periods.
    Total: 4 songs per category (one from each era) = 12 songs total.
    """
    text = "**Curated Song Recommendations for Breakup Recovery:**\n\n"

    for category_id in ['release', 'empowerment', 'healing']:
        category = CURATED_SONGS[category_id]

        text += f"### {category['name']}\n"
        text += f"*{category['description']}*\n\n"

        # Select one random song from each era
        for era_id in ERA_IDS:
            era_songs = category["eras"][era_id]["songs"]
            selected_song = random.choice(era_songs)
            text += f"- **\"{selected_song['title']}\"** by {selected_song['artist']} ({selected_song['tag']})\n"

        text += "\n"

    text += "*Note: These songs span different eras. Personalize based on user's situation and music preferences.*"
    return text

def cleanup_temp_files():
    """Clean up all temporary files created during the session"""
    for temp_path in temp_files_created:
        try:
            if os.path.exists(temp_path):
                os.remove(temp_path)
                logger.info(f"Cleaned up temporary file: {temp_path}")
        except Exception as e:
            logger.error(f"Error cleaning up {temp_path}: {str(e)}")
    temp_files_created.clear()

# Register cleanup function to run on exit
atexit.register(cleanup_temp_files)

def load_config() -> Dict[str, Any]:
    """Load configuration from YAML file"""
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        logger.info(f"Configuration loaded successfully from {CONFIG_PATH}")
        return config
    except Exception as e:
        logger.error(f"Error loading configuration: {str(e)}")
        st.error(f"Failed to load configuration file. Please check {CONFIG_PATH}")
        st.stop()

def get_default_api_key() -> Optional[str]:
    """Get default API key from environment variables"""
    try:
        api_key = env_config('DEFAULT_GEMINI_API_KEY', default='')
        return api_key if api_key else None
    except UndefinedValueError:
        return None


def get_model_config(yaml_config: Dict[str, Any]) -> Dict[str, Any]:
    """Get model configuration from environment variables with YAML fallback"""
    model_config = {
        'id': env_config('GEMINI_MODEL_ID', default=yaml_config['model']['id']),
        'temperature': env_config('GEMINI_TEMPERATURE', default=yaml_config['model']['temperature'], cast=float),
        'max_tokens': env_config('GEMINI_MAX_TOKENS', default=yaml_config['model']['max_tokens'], cast=int)
    }
    logger.info(f"Model configuration loaded: {model_config['id']}, temp={model_config['temperature']}, max_tokens={model_config['max_tokens']}")
    return model_config

def validate_input(text: str, max_length: int = MAX_INPUT_LENGTH) -> bool:
    """Validate user input length"""
    return len(text) <= max_length

def validate_file_size(file) -> bool:
    """Validate uploaded file size"""
    try:
        file_size = len(file.getvalue())
        return file_size <= MAX_FILE_SIZE
    except:
        return False

def sanitize_input(text: str) -> str:
    """Basic input sanitization to prevent injection"""
    # Remove any potential code injection attempts
    dangerous_patterns = ['```', '<script>', 'javascript:', 'eval(', 'exec(']
    sanitized = text
    for pattern in dangerous_patterns:
        if pattern.lower() in sanitized.lower():
            logger.warning(f"Potentially dangerous pattern detected: {pattern}")
    return sanitized

def initialize_agents(api_key: str, config: Dict[str, Any]) -> tuple[Optional[Agent], Optional[Agent], Optional[Agent], Optional[Agent]]:
    """Initialize all AI agents with configuration"""
    try:
        # Get model configuration from environment variables (with YAML fallback)
        model_config = get_model_config(config)
        model = Gemini(id=model_config['id'], api_key=api_key)

        agents_config = config['agents']

        therapist_agent = Agent(
            model=model,
            name=agents_config['therapist']['name'],
            instructions=agents_config['therapist']['instructions'],
            markdown=True
        )

        closure_agent = Agent(
            model=model,
            name=agents_config['closure']['name'],
            instructions=agents_config['closure']['instructions'],
            markdown=True
        )

        # Get curated music recommendations for Jonas (routine planner)
        # Uses era-based selection: one song from each era per category (12 songs total)
        music_recommendations = get_music_recommendations_text()

        # Add music recommendations context to Jonas's instructions
        jonas_instructions = agents_config['routine_planner']['instructions']
        jonas_instructions = f"{jonas_instructions}\n\n## 🎵 Curated Music Recommendations\n\n{music_recommendations}"
        logger.info("Added curated music recommendations to Jonas agent")

        routine_planner_agent = Agent(
            model=model,
            name=agents_config['routine_planner']['name'],
            instructions=jonas_instructions,
            markdown=True
        )

        brutal_honesty_agent = Agent(
            model=model,
            name=agents_config['brutal_honesty']['name'],
            tools=[DuckDuckGoTools()],
            instructions=agents_config['brutal_honesty']['instructions'],
            markdown=True
        )

        logger.info("All agents initialized successfully")
        return therapist_agent, closure_agent, routine_planner_agent, brutal_honesty_agent

    except Exception as e:
        error_str = str(e).lower()
        logger.error(f"Error initializing agents: {str(e)}")

        # User-friendly error messages based on error type
        if "quota" in error_str or "quota exceeded" in error_str:
            st.error("⚠️ We're experiencing high demand! API quota exceeded. Please try again later.")
        elif "rate limit" in error_str or "429" in error_str:
            st.error("⏳ Too many requests right now. Please wait a moment and try again.")
        elif "503" in error_str or "service unavailable" in error_str:
            st.error("🔧 Service temporarily unavailable. Please try again in a few minutes.")
        else:
            st.error("Our service is temporarily unavailable. Please try again in a few minutes.")

        return None, None, None, None

def process_images(files) -> List[AgnoImage]:
    """Process uploaded image files and return Agno Image objects"""
    processed_images = []
    for file in files:
        try:
            # Validate file size
            if not validate_file_size(file):
                st.warning(f"File {file.name} exceeds maximum size of 10MB and will be skipped")
                continue

            temp_dir = tempfile.gettempdir()
            temp_path = os.path.join(temp_dir, f"temp_{file.name}")

            with open(temp_path, "wb") as f:
                f.write(file.getvalue())

            # Track temp file for cleanup
            temp_files_created.append(temp_path)

            agno_image = AgnoImage(filepath=Path(temp_path))
            processed_images.append(agno_image)
            logger.info(f"Processed image: {file.name}")

        except Exception as e:
            logger.error(f"Error processing image {file.name}: {str(e)}")
            st.warning(f"Could not process image {file.name}")
            continue

    return processed_images

def main():
    """Main application entry point"""

    # Load configuration
    config = load_config()
    ui_config = config['ui']
    agents_config = config['agents']

    # Set page config
    st.set_page_config(
        page_title=ui_config['app_title'],
        page_icon=ui_config['page_icon'],
        layout="wide"
    )

    # Hide Streamlit branding (keep menu for user features like Print)
    hide_streamlit_style = """
        <style>
        footer {visibility: hidden;}
        .stDeployButton {display: none;}
        div[data-testid="stDecoration"] {visibility: hidden; height: 0%; position: fixed;}
        div[data-testid="stStatusWidget"] {visibility: hidden; height: 0%; position: fixed;}
        /* Hide header branding elements but keep menu visible */
        header[data-testid="stHeader"] > div:first-child {display: none;}
        /* Ensure menu stays visible */
        #MainMenu {visibility: visible !important;}
        button[title="View app source"] {display: none;}
        </style>
    """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)

    # Configure analytics tracking (lazy initialization)
    analytics_kwargs = {}

    # Only initialize Firestore analytics if secrets are configured
    if has_firebase_secrets():
        firestore_key_path = get_firestore_key_path()
        if firestore_key_path:
            try:
                firebase_secrets = dict(st.secrets["firebase"])
                analytics_kwargs = {
                    "firestore_key_file": firestore_key_path,
                    "firestore_collection_name": "analytics",
                    "firestore_project_name": firebase_secrets.get("project_id")
                }
            except Exception as e:
                logger.warning(f"Could not configure Firestore analytics: {str(e)}")

    # Wrap app with analytics tracking
    with streamlit_analytics.track(**analytics_kwargs):
        _main_content(config, ui_config, agents_config)


@st.fragment
def waitlist_section():
    """
    Waitlist email signup section as a fragment.
    Using @st.fragment allows this section to rerun independently
    without interrupting the main app (e.g., during agent analysis).
    """
    st.markdown("### 💬 Join the Waitlist")

    st.markdown("Want to have a real conversation with **Maya**?")

    st.markdown("""
Currently, our agents listen and guide. Soon, you can chat with them back-and-forth like a real friend.

**You decide if they remember you or not.**
100% Private. 100% Your Control.
    """)

    # Initialize session state for email subscription
    if "email_subscribed" not in st.session_state:
        st.session_state.email_subscribed = False

    if not st.session_state.email_subscribed:
        email_input = st.text_input(
            "Get Early Access",
            placeholder="you@example.com",
            key="waitlist_email_input"
        )
        if st.button("Notify Me", type="primary", key="waitlist_submit"):
            if email_input:
                if save_email_to_firestore(email_input):
                    st.session_state.email_subscribed = True
                    st.rerun(scope="fragment")
                else:
                    st.error("Please enter a valid email address.")
            else:
                st.warning("Please enter your email address.")
    else:
        st.success("You're on the list!")


def _main_content(config, ui_config, agents_config):
    """Main content of the application (wrapped by analytics)"""

    # Use default API key directly
    final_api_key = get_default_api_key()

    # Get social URLs for About section
    social_urls = get_social_urls()

    # Sidebar
    with st.sidebar:
        # About Developer Section
        st.header("👨‍💻 About the Developer")
        st.markdown("**Umang Thakkar**")
        st.markdown("Helping hearts heal, one conversation at a time.")

        # Social links as hyperlinks
        social_links = []
        if social_urls["linkedin"]:
            social_links.append(f"[LinkedIn]({social_urls['linkedin']})")
        if social_urls["website"]:
            social_links.append(f"[Portfolio]({social_urls['website']})")
        if social_urls["email"]:
            social_links.append(f"[Email](mailto:{social_urls['email']})")

        if social_links:
            st.markdown(" · ".join(social_links))

        # Privacy Information
        st.markdown("---")
        st.markdown("### 🔒 Privacy & Security")
        st.markdown(ui_config['privacy_notice'])

        # Waitlist Section (fragment to prevent main app rerun during analysis)
        st.markdown("---")
        waitlist_section()

    # Main content
    st.title(ui_config['app_title'])
    st.markdown(ui_config['welcome_message'])

    # Input section
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Share Your Feelings")
        user_input = st.text_area(
            "How are you feeling? What happened?",
            height=150,
            placeholder="Tell us your story...",
            max_chars=MAX_INPUT_LENGTH,
            help=f"Maximum {MAX_INPUT_LENGTH} characters"
        )

    with col2:
        st.subheader("Upload Chat Screenshots (Optional)")
        uploaded_files = st.file_uploader(
            f"Upload up to {MAX_FILES} screenshots (max 10MB each)",
            type=["jpg", "jpeg", "png"],
            accept_multiple_files=True,
            key="screenshots",
            help="Screenshots are processed temporarily and deleted immediately after"
        )

        if uploaded_files:
            if len(uploaded_files) > MAX_FILES:
                st.warning(f"Maximum {MAX_FILES} files allowed. Only the first {MAX_FILES} will be processed.")
                uploaded_files = uploaded_files[:MAX_FILES]

            for file in uploaded_files:
                st.image(file, caption=file.name, use_container_width=True)

    # Process button
    if st.button("Get Recovery Plan 💝", type="primary"):
        if not final_api_key:
            st.warning("Please configure your API key in the sidebar first!")
        elif not user_input and not uploaded_files:
            st.warning("Please share your feelings or upload screenshots to get help.")
        elif user_input and not validate_input(user_input):
            st.error(f"Your message is too long. Please keep it under {MAX_INPUT_LENGTH} characters.")
        else:
            # Sanitize input
            sanitized_input = sanitize_input(user_input) if user_input else ""

            # Initialize agents
            therapist_agent, closure_agent, routine_planner_agent, brutal_honesty_agent = initialize_agents(
                final_api_key, config
            )

            if all([therapist_agent, closure_agent, routine_planner_agent, brutal_honesty_agent]):
                try:
                    st.header("Your Personalized Recovery Plan")

                    # Process images if uploaded
                    all_images = process_images(uploaded_files) if uploaded_files else []

                    # Therapist Analysis
                    with st.spinner(ui_config['loading_messages']['therapist']):
                        therapist_prompt = agents_config['therapist']['runtime_prompt'].format(
                            user_input=sanitized_input
                        )

                        response = therapist_agent.run(
                            therapist_prompt,
                            images=all_images
                        )

                        # Maya's response with blue border
                        st.markdown("""<div style="border-left: 4px solid #4A90E2; padding-left: 15px; margin: 25px 0;">""", unsafe_allow_html=True)
                        st.subheader(ui_config['section_titles']['therapist'])
                        st.markdown(response.content)
                        st.markdown("</div>", unsafe_allow_html=True)

                    # Closure Messages
                    with st.spinner(ui_config['loading_messages']['closure']):
                        closure_prompt = agents_config['closure']['runtime_prompt'].format(
                            user_input=sanitized_input
                        )

                        response = closure_agent.run(
                            closure_prompt,
                            images=all_images
                        )

                        # Harper's response with purple border
                        st.markdown("""<div style="border-left: 4px solid #9B59B6; padding-left: 15px; margin: 25px 0;">""", unsafe_allow_html=True)
                        st.subheader(ui_config['section_titles']['closure'])
                        st.markdown(response.content)
                        st.markdown("</div>", unsafe_allow_html=True)

                    # Recovery Plan
                    with st.spinner(ui_config['loading_messages']['routine_planner']):
                        routine_prompt = agents_config['routine_planner']['runtime_prompt'].format(
                            user_input=sanitized_input
                        )

                        response = routine_planner_agent.run(
                            routine_prompt,
                            images=all_images
                        )

                        # Jonas's response with green border
                        st.markdown("""<div style="border-left: 4px solid #2ECC71; padding-left: 15px; margin: 25px 0;">""", unsafe_allow_html=True)
                        st.subheader(ui_config['section_titles']['routine_planner'])
                        st.markdown(response.content)
                        st.markdown("</div>", unsafe_allow_html=True)

                    # Honest Feedback
                    with st.spinner(ui_config['loading_messages']['brutal_honesty']):
                        honesty_prompt = agents_config['brutal_honesty']['runtime_prompt'].format(
                            user_input=sanitized_input
                        )

                        response = brutal_honesty_agent.run(
                            honesty_prompt,
                            images=all_images
                        )

                        # Riya's response with red border
                        st.markdown("""<div style="border-left: 4px solid #E74C3C; padding-left: 15px; margin: 25px 0;">""", unsafe_allow_html=True)
                        st.subheader(ui_config['section_titles']['brutal_honesty'])
                        st.markdown(response.content)
                        st.markdown("</div>", unsafe_allow_html=True)

                    # Clean up temp files after processing
                    cleanup_temp_files()
                    logger.info("Processing complete, temp files cleaned up")

                except Exception as e:
                    error_str = str(e).lower()
                    logger.error(f"Error during analysis: {str(e)}")

                    # User-friendly error messages based on error type
                    if "quota" in error_str or "quota exceeded" in error_str:
                        st.error("⚠️ We're experiencing high demand! API quota exceeded. Please try again later.")
                    elif "rate limit" in error_str or "429" in error_str:
                        st.error("⏳ Too many requests right now. Please wait a moment and try again.")
                    elif "503" in error_str or "service unavailable" in error_str:
                        st.error("🔧 Service temporarily unavailable. Please try again in a few minutes.")
                    else:
                        st.error("An error occurred during analysis. Please try again.")

                    # Clean up on error too
                    cleanup_temp_files()
            else:
                st.error("Our service is temporarily unavailable. Please try again in a few minutes.")

    # Footer section
    st.markdown("---")
    if social_urls["email"]:
        st.markdown(f"""
<div style="text-align: center;">
<h3>👨‍💻 A Humble Request</h3>
<p>It takes 10s to break a system, but days to build one. Please spare my API credits!</p>
<p>Rather than stress-testing, <a href="mailto:{social_urls['email']}">drop me a mail</a> and I'll share the full list of limitations myself. Let's collaborate instead!</p>
</div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
<div style="text-align: center;">
<h3>👨‍💻 A Humble Request</h3>
<p>It takes 10s to break a system, but days to build one. Please spare my API credits!</p>
<p>Rather than stress-testing, drop me a mail and I'll share the full list of limitations myself. Let's collaborate instead!</p>
</div>
        """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
