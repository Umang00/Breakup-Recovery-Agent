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
        with open(CONFIG_PATH, 'r') as f:
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
        model = Gemini(id=config['model']['id'], api_key=api_key)

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

        routine_planner_agent = Agent(
            model=model,
            name=agents_config['routine_planner']['name'],
            instructions=agents_config['routine_planner']['instructions'],
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
                st.warning("Please enter your API key to proceed")
                st.markdown("""
                To get your API key:
                1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
                2. Enable the Generative Language API in your [Google Cloud Console](https://console.developers.google.com/apis/api/generativelanguage.googleapis.com)
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

                        st.subheader(ui_config['section_titles']['therapist'])
                        st.markdown(response.content)

                    # Closure Messages
                    with st.spinner(ui_config['loading_messages']['closure']):
                        closure_prompt = agents_config['closure']['runtime_prompt'].format(
                            user_input=sanitized_input
                        )

                        response = closure_agent.run(
                            closure_prompt,
                            images=all_images
                        )

                        st.subheader(ui_config['section_titles']['closure'])
                        st.markdown(response.content)

                    # Recovery Plan
                    with st.spinner(ui_config['loading_messages']['routine_planner']):
                        routine_prompt = agents_config['routine_planner']['runtime_prompt'].format(
                            user_input=sanitized_input
                        )

                        response = routine_planner_agent.run(
                            routine_prompt,
                            images=all_images
                        )

                        st.subheader(ui_config['section_titles']['routine_planner'])
                        st.markdown(response.content)

                    # Honest Feedback
                    with st.spinner(ui_config['loading_messages']['brutal_honesty']):
                        honesty_prompt = agents_config['brutal_honesty']['runtime_prompt'].format(
                            user_input=sanitized_input
                        )

                        response = brutal_honesty_agent.run(
                            honesty_prompt,
                            images=all_images
                        )

                        st.subheader(ui_config['section_titles']['brutal_honesty'])
                        st.markdown(response.content)

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
