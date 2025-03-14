import gradio as gr
import logging
import json
import os
from datetime import datetime
from typing import Dict, Any, Tuple, List, Optional, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("ui.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("UISettings")

# Ensure feedback directory exists
FEEDBACK_DIR = "feedback"
os.makedirs(FEEDBACK_DIR, exist_ok=True)


class UISettings:
    """
    Utility class for managing UI settings and user interactions.

    This class provides static methods for toggling UI components, handling user feedback,
    and managing UI state and appearance.
    
    Attributes:
        THEME_LIGHT (Dict): CSS styling for light theme
        THEME_DARK (Dict): CSS styling for dark theme
    
    Methods:
        toggle_sidebar: Toggle the visibility of a UI component
        feedback: Process and store user feedback on generated responses
        toggle_theme: Switch between light and dark themes
        clear_chat: Clear the chat history
        save_chat_history: Save the current chat history to a file
        load_chat_history: Load a saved chat history from a file
    """
    
    # Theme definitions
    THEME_LIGHT = {
        "bg_color": "#FFFFFF",
        "text_color": "#333333",
        "accent_color": "#4CAF50",
        "secondary_color": "#E0E0E0"
    }
    
    THEME_DARK = {
        "bg_color": "#1E1E1E",
        "text_color": "#F0F0F0",
        "accent_color": "#6FCF7C",
        "secondary_color": "#3A3A3A"
    }
    
    @staticmethod
    def toggle_sidebar(state: bool) -> Tuple[Dict[str, bool], bool]:
        """
        Toggle the visibility state of a UI component.

        Parameters:
            state (bool): The current state of the UI component.

        Returns:
            Tuple[Dict[str, bool], bool]: A tuple containing the updated UI component state and the new state.
        """
        try:
            state = not state
            logger.debug(f"Sidebar visibility toggled to: {state}")
            return gr.update(visible=state), state
        except Exception as e:
            logger.error(f"Error toggling sidebar: {str(e)}", exc_info=True)
            # Return original state if there's an error
            return gr.update(visible=not state), not state

    @staticmethod
    def feedback(data: gr.LikeData) -> None:
        """
        Process and store user feedback on the generated response.

        This method logs user feedback and saves it to a JSON file for later analysis.

        Parameters:
            data (gr.LikeData): Gradio LikeData object containing user feedback.
        """
        try:
            feedback_type = "upvote" if data.liked else "downvote"
            logger.info(f"User {feedback_type}d response: {data.value[:100]}...")
            
            # Create feedback data structure
            feedback_data = {
                "timestamp": datetime.now().isoformat(),
                "feedback_type": feedback_type,
                "response": data.value
            }
            
            # Save feedback to file
            filename = f"{FEEDBACK_DIR}/feedback_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w') as f:
                json.dump(feedback_data, f, indent=2)
                
            logger.info(f"Feedback saved to {filename}")
        except Exception as e:
            logger.error(f"Error processing feedback: {str(e)}", exc_info=True)

    @staticmethod
    def toggle_theme(current_theme: str) -> Tuple[Dict[str, Any], str]:
        """
        Toggle between light and dark themes.

        Parameters:
            current_theme (str): The current theme ("light" or "dark").

        Returns:
            Tuple[Dict[str, Any], str]: A tuple containing the CSS update and the new theme name.
        """
        try:
            if current_theme == "light":
                new_theme = "dark"
                theme_css = UISettings.THEME_DARK
            else:
                new_theme = "light"
                theme_css = UISettings.THEME_LIGHT
                
            logger.debug(f"Theme changed from {current_theme} to {new_theme}")
            
            # Create CSS update for Gradio
            css_update = gr.update(
                value=f"""
                :root {{
                    --bg-color: {theme_css['bg_color']};
                    --text-color: {theme_css['text_color']};
                    --accent-color: {theme_css['accent_color']};
                    --secondary-color: {theme_css['secondary_color']};
                }}
                """
            )
            
            return css_update, new_theme
        except Exception as e:
            logger.error(f"Error toggling theme: {str(e)}", exc_info=True)
            # Return original theme if there's an error
            return gr.update(), current_theme

    @staticmethod
    def clear_chat() -> Tuple[List, None]:
        """
        Clear the chat history.

        Returns:
            Tuple[List, None]: A tuple containing an empty list for the chat history and None for the references.
        """
        try:
            logger.info("Chat history cleared")
            return [], None
        except Exception as e:
            logger.error(f"Error clearing chat: {str(e)}", exc_info=True)
            return [], None

    @staticmethod
    def save_chat_history(chatbot: List, filename: Optional[str] = None) -> str:
        """
        Save the current chat history to a JSON file.

        Parameters:
            chatbot (List): The current chat history.
            filename (Optional[str]): Custom filename to save the history to.

        Returns:
            str: Path to the saved file.
        """
        try:
            if not filename:
                filename = f"chat_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            # Ensure the chat history directory exists
            os.makedirs("chat_history", exist_ok=True)
            filepath = os.path.join("chat_history", filename)
            
            with open(filepath, 'w') as f:
                json.dump(chatbot, f, indent=2)
                
            logger.info(f"Chat history saved to {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Error saving chat history: {str(e)}", exc_info=True)
            return "Error: Could not save chat history"

    @staticmethod
    def load_chat_history(filepath: str) -> List:
        """
        Load a saved chat history from a JSON file.

        Parameters:
            filepath (str): Path to the chat history file.

        Returns:
            List: The loaded chat history.
        """
        try:
            if not os.path.exists(filepath):
                logger.warning(f"Chat history file not found: {filepath}")
                return []
                
            with open(filepath, 'r') as f:
                chatbot = json.load(f)
                
            logger.info(f"Chat history loaded from {filepath}")
            return chatbot
        except Exception as e:
            logger.error(f"Error loading chat history: {str(e)}", exc_info=True)
            return []