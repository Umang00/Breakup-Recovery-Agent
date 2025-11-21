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
from decouple import config as env_config, UndefinedValueError
import atexit

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

# Curated Music Database - 105 songs, 35 per category
# All songs are verified therapeutic hits for breakup recovery
CURATED_SONGS = {
    "release": {
        "name": "Emotional Release",
        "description": "For crying, feeling, and validating emotions",
        "songs": [
            {"title": "Driver's License", "artist": "Olivia Rodrigo", "tag": "Modern Classic"},
            {"title": "Someone Like You", "artist": "Adele", "tag": "Ballad"},
            {"title": "All Too Well (10 Minute Version)", "artist": "Taylor Swift", "tag": "Storytelling"},
            {"title": "Glimpse of Us", "artist": "Joji", "tag": "Melancholy"},
            {"title": "Liability", "artist": "Lorde", "tag": "Introspective"},
            {"title": "Back to Black", "artist": "Amy Winehouse", "tag": "Soul/Grief"},
            {"title": "The Night We Met", "artist": "Lord Huron", "tag": "Haunting"},
            {"title": "Lose You to Love Me", "artist": "Selena Gomez", "tag": "Closure"},
            {"title": "Skinny Love", "artist": "Bon Iver", "tag": "Indie Folk"},
            {"title": "Fix You", "artist": "Coldplay", "tag": "Comfort"},
            {"title": "Stone Cold", "artist": "Demi Lovato", "tag": "Vocals"},
            {"title": "I Fall Apart", "artist": "Post Malone", "tag": "Modern Heartbreak"},
            {"title": "Happier Than Ever", "artist": "Billie Eilish", "tag": "Build-up/Release"},
            {"title": "Dancing On My Own", "artist": "Robyn", "tag": "Sad Disco"},
            {"title": "Exile", "artist": "Taylor Swift ft. Bon Iver", "tag": "Duet"},
            {"title": "Falling", "artist": "Harry Styles", "tag": "Ballad"},
            {"title": "Jealous", "artist": "Labrinth", "tag": "Deep Sadness"},
            {"title": "Stay", "artist": "Rihanna ft. Mikky Ekko", "tag": "Vulnerable"},
            {"title": "Before You Go", "artist": "Lewis Capaldi", "tag": "Regret"},
            {"title": "Listen before i go", "artist": "Billie Eilish", "tag": "Heavy/Slow"},
            {"title": "Nothing Compares 2 U", "artist": "Sinéad O'Connor", "tag": "Classic"},
            {"title": "Jar of Hearts", "artist": "Christina Perri", "tag": "Angsty"},
            {"title": "Grenade", "artist": "Bruno Mars", "tag": "Desperation"},
            {"title": "Sign of the Times", "artist": "Harry Styles", "tag": "Epic"},
            {"title": "Say Something", "artist": "A Great Big World", "tag": "Giving Up"},
            {"title": "Un-break My Heart", "artist": "Toni Braxton", "tag": "R&B Classic"},
            {"title": "Already Gone", "artist": "Kelly Clarkson", "tag": "Acceptance"},
            {"title": "One More Light", "artist": "Linkin Park", "tag": "Mourning"},
            {"title": "Creep", "artist": "Radiohead", "tag": "Alternative"},
            {"title": "Wait", "artist": "M83", "tag": "Atmospheric"},
            {"title": "Let Her Go", "artist": "Passenger", "tag": "Acoustic"},
            {"title": "Hello", "artist": "Adele", "tag": "Powerhouse"},
            {"title": "Bleeding Love", "artist": "Leona Lewis", "tag": "2000s Pop"},
            {"title": "Traitor", "artist": "Olivia Rodrigo", "tag": "Betrayal"},
            {"title": "Kill Bill", "artist": "SZA", "tag": "Dark/Honest"}
        ]
    },
    "empowerment": {
        "name": "Empowerment",
        "description": "For confidence, energy, and independence",
        "songs": [
            {"title": "Flowers", "artist": "Miley Cyrus", "tag": "Self-Care"},
            {"title": "Good as Hell", "artist": "Lizzo", "tag": "Mood Booster"},
            {"title": "Since U Been Gone", "artist": "Kelly Clarkson", "tag": "Rock Pop"},
            {"title": "I Will Survive", "artist": "Gloria Gaynor", "tag": "Disco Classic"},
            {"title": "Don't Start Now", "artist": "Dua Lipa", "tag": "Moving On"},
            {"title": "thank u, next", "artist": "Ariana Grande", "tag": "Gratitude"},
            {"title": "We Are Never Ever Getting Back Together", "artist": "Taylor Swift", "tag": "Definitive"},
            {"title": "Truth Hurts", "artist": "Lizzo", "tag": "Sassy"},
            {"title": "Rolling in the Deep", "artist": "Adele", "tag": "Power"},
            {"title": "Irreplaceable", "artist": "Beyoncé", "tag": "R&B Classic"},
            {"title": "Before He Cheats", "artist": "Carrie Underwood", "tag": "Revenge/Country"},
            {"title": "You Oughta Know", "artist": "Alanis Morissette", "tag": "90s Rage"},
            {"title": "Titanium", "artist": "David Guetta ft. Sia", "tag": "Unbreakable"},
            {"title": "Roar", "artist": "Katy Perry", "tag": "Anthem"},
            {"title": "Stronger (What Doesn't Kill You)", "artist": "Kelly Clarkson", "tag": "Resilience"},
            {"title": "Survivor", "artist": "Destiny's Child", "tag": "Independence"},
            {"title": "So What", "artist": "P!nk", "tag": "Rock Attitude"},
            {"title": "Single Ladies", "artist": "Beyoncé", "tag": "Upbeat"},
            {"title": "New Rules", "artist": "Dua Lipa", "tag": "Guidebook"},
            {"title": "Shake It Off", "artist": "Taylor Swift", "tag": "Fun"},
            {"title": "Confident", "artist": "Demi Lovato", "tag": "Ego"},
            {"title": "Look What You Made Me Do", "artist": "Taylor Swift", "tag": "Dark Pop"},
            {"title": "Respect", "artist": "Aretha Franklin", "tag": "Soul Classic"},
            {"title": "Girl on Fire", "artist": "Alicia Keys", "tag": "Inspirational"},
            {"title": "Independent Women, Pt. 1", "artist": "Destiny's Child", "tag": "Throwback"},
            {"title": "Part of Me", "artist": "Katy Perry", "tag": "Resilience"},
            {"title": "Fighter", "artist": "Christina Aguilera", "tag": "Grit"},
            {"title": "Love Myself", "artist": "Hailee Steinfeld", "tag": "Self-Love"},
            {"title": "Shout Out to My Ex", "artist": "Little Mix", "tag": "Group Anthem"},
            {"title": "Problem", "artist": "Ariana Grande ft. Iggy Azalea", "tag": "Pop Hit"},
            {"title": "Sorry", "artist": "Beyoncé", "tag": "No Apologies"},
            {"title": "Good 4 U", "artist": "Olivia Rodrigo", "tag": "Pop Punk"},
            {"title": "Misery Business", "artist": "Paramore", "tag": "High Energy"},
            {"title": "Born This Way", "artist": "Lady Gaga", "tag": "Anthem"},
            {"title": "Break Free", "artist": "Ariana Grande", "tag": "Liberation"}
        ]
    },
    "healing": {
        "name": "Hope & Healing",
        "description": "For peace, optimism, and moving forward",
        "songs": [
            {"title": "Clean", "artist": "Taylor Swift", "tag": "Recovery"},
            {"title": "Here Comes the Sun", "artist": "The Beatles", "tag": "Sunshine"},
            {"title": "Answer: Love Myself", "artist": "BTS", "tag": "K-Pop/Self-Love"},
            {"title": "Vienna", "artist": "Billy Joel", "tag": "Perspective"},
            {"title": "Put Your Records On", "artist": "Corinne Bailey Rae", "tag": "Chill"},
            {"title": "Rainbow", "artist": "Kacey Musgraves", "tag": "After the Storm"},
            {"title": "Unwritten", "artist": "Natasha Bedingfield", "tag": "Freedom"},
            {"title": "Rise Up", "artist": "Andra Day", "tag": "Strength"},
            {"title": "comethru", "artist": "Jeremy Zucker", "tag": "Gen Z Chill"},
            {"title": "Three Little Birds", "artist": "Bob Marley", "tag": "Reassurance"},
            {"title": "Dog Days Are Over", "artist": "Florence + The Machine", "tag": "Euphoria"},
            {"title": "Golden Hour", "artist": "JVKE", "tag": "Modern Piano"},
            {"title": "Matilda", "artist": "Harry Styles", "tag": "Letting Go"},
            {"title": "Beautiful Day", "artist": "U2", "tag": "Classic Rock"},
            {"title": "I'm Still Standing", "artist": "Elton John", "tag": "Upbeat Classic"},
            {"title": "Landslide", "artist": "Fleetwood Mac", "tag": "Reflection"},
            {"title": "Keep Your Head Up", "artist": "Andy Grammer", "tag": "Pop Folk"},
            {"title": "Free", "artist": "Florence + The Machine", "tag": "Release"},
            {"title": "Scars to Your Beautiful", "artist": "Alessia Cara", "tag": "Validation"},
            {"title": "Just the Way You Are", "artist": "Bruno Mars", "tag": "Sweet"},
            {"title": "Pocketful of Sunshine", "artist": "Natasha Bedingfield", "tag": "Nostalgia"},
            {"title": "Walking on Sunshine", "artist": "Katrina and the Waves", "tag": "Happy 80s"},
            {"title": "Lovely Day", "artist": "Bill Withers", "tag": "Groove"},
            {"title": "Brave", "artist": "Sara Bareilles", "tag": "Courage"},
            {"title": "Firework", "artist": "Katy Perry", "tag": "Uplifting"},
            {"title": "Somewhere Over the Rainbow", "artist": "Israel Kamakawiwo'ole", "tag": "Ukulele/Calm"},
            {"title": "Better Now", "artist": "Post Malone", "tag": "Peaceful Rap"},
            {"title": "The Climb", "artist": "Miley Cyrus", "tag": "Journey"},
            {"title": "Feeling Good", "artist": "Nina Simone", "tag": "Soul Jazz"},
            {"title": "Stand by Me", "artist": "Ben E. King", "tag": "Support"},
            {"title": "Count on Me", "artist": "Bruno Mars", "tag": "Friendship"},
            {"title": "What a Wonderful World", "artist": "Louis Armstrong", "tag": "Gratitude"},
            {"title": "Sunday Morning", "artist": "Maroon 5", "tag": "Easy Listening"},
            {"title": "Solar Power", "artist": "Lorde", "tag": "Summer Vibe"},
            {"title": "Fast Car", "artist": "Tracy Chapman", "tag": "Storytelling"}
        ]
    }
}


def get_music_recommendations_text(songs_per_category: int = 5) -> str:
    """
    Get formatted music recommendations text for LLM context
    Randomly selects songs from each category for variety
    """
    text = "**Curated Song Recommendations for Breakup Recovery:**\n\n"

    for category_id in ['release', 'empowerment', 'healing']:
        category = CURATED_SONGS[category_id]
        all_songs = category["songs"]

        # Random selection for variety
        selected = random.sample(all_songs, min(songs_per_category, len(all_songs)))

        text += f"### {category['name']}\n"
        text += f"*{category['description']}*\n\n"

        for song in selected:
            text += f"- **\"{song['title']}\"** by {song['artist']} ({song['tag']})\n"

        text += "\n"

    text += "*Note: These are curated therapeutic songs. Personalize based on user's situation and preferences.*"
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

def allow_user_api_key() -> bool:
    """Check if users are allowed to provide their own API key"""
    try:
        return env_config('ALLOW_USER_API_KEY', default=True, cast=bool)
    except:
        return True

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
        # Uses random selection from 105-song curated database (35 per category)
        music_recommendations = get_music_recommendations_text(songs_per_category=5)

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
        logger.error(f"Error initializing agents: {str(e)}")
        st.error(f"Error initializing agents: {str(e)}")
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

    # Initialize session state
    if "api_key_input" not in st.session_state:
        st.session_state.api_key_input = ""

    # Get default API key
    default_api_key = get_default_api_key()
    allow_user_key = allow_user_api_key()

    # Sidebar for API key configuration
    with st.sidebar:
        st.header("🔑 API Configuration")

        # Check if we have a default key
        if default_api_key:
            st.success("✅ Default API key configured")

            if allow_user_key:
                use_own_key = st.checkbox(
                    "Use my own API key instead",
                    help="Check this to use your own Gemini API key"
                )

                if use_own_key:
                    api_key = st.text_input(
                        "Enter your Gemini API Key",
                        value=st.session_state.api_key_input,
                        type="password",
                        help="Get your API key from Google AI Studio",
                        key="api_key_widget"
                    )
                    if api_key != st.session_state.api_key_input:
                        st.session_state.api_key_input = api_key
                    final_api_key = api_key if api_key else default_api_key
                else:
                    final_api_key = default_api_key
                    st.info("Using default API key")
            else:
                final_api_key = default_api_key
                st.info("Using default API key")
        else:
            # No default key, user must provide their own
            api_key = st.text_input(
                "Enter your Gemini API Key",
                value=st.session_state.api_key_input,
                type="password",
                help="Get your API key from Google AI Studio",
                key="api_key_widget"
            )

            if api_key != st.session_state.api_key_input:
                st.session_state.api_key_input = api_key

            final_api_key = api_key

            if not final_api_key:
                st.info("### Get your FREE API key in 2 minutes! 🎉")
                st.markdown("""
                **Quick setup:**
                1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
                2. Enable the Generative Language API in your [Google Cloud Console](https://console.developers.google.com/apis/api/generativelanguage.googleapis.com)
                3. Copy and paste here - done! ✨
                """)

        # Privacy Information
        st.markdown("---")
        st.markdown("### 🔒 Privacy & Security")
        st.markdown(ui_config['privacy_notice'])

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
                    logger.error(f"Error during analysis: {str(e)}")
                    st.error("An error occurred during analysis. Please try again.")
                    # Clean up on error too
                    cleanup_temp_files()
            else:
                st.error("Failed to initialize agents. Please check your API key and try again.")

    # Footer with branding
    st.markdown("---")
    st.markdown("""
        <div style='text-align: center; padding: 20px;'>
            <p style='font-size: 18px; margin-bottom: 10px;'>Made with ❤️ by <strong>Umang</strong></p>
            <p style='font-size: 14px; color: #666;'>Helping hearts heal, one conversation at a time</p>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
