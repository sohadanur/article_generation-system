import json
import os
from dotenv import load_dotenv
from mistralai.client import MistralClient  # ✅ No need for 'ChatMessage'

# Load environment variables
load_dotenv()

# Load Mistral API credentials
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
MISTRAL_MODEL = os.getenv("MISTRAL_MODEL")

# Ensure API key and model are available
if not MISTRAL_API_KEY or not MISTRAL_MODEL:
    raise ValueError("MISTRAL_API_KEY or MISTRAL_MODEL is not set. Check your .env file.")

# Initialize Mistral client
mistral_client = MistralClient(api_key=MISTRAL_API_KEY)


def generate_outline(topic, subject):
    """
    Generates an outline for an article about the given topic and subject.
    """
    try:
        SYSTEM_MESSAGE = f"You are a well-trained ghostwriter for writing articles about {topic}. " \
                         "Your articles are informative, detailed, and well-organized, " \
                         "written in a way that is easy to understand by all ages."

        PROMPT = f"Write the article outline for an article about {subject}. " \
                 "Reply with a JSON object in the format:\n" \
                 """{
                    "title": "Example Title",
                    "sections": [
                        {
                            "header": "Header Example",
                            "sub-sections": [
                                {
                                    "header": "Example Header"
                                }
                            ]
                        }
                    ]
                }"""

        messages = [
            {"role": "system", "content": SYSTEM_MESSAGE},
            {"role": "user", "content": PROMPT}
        ]

        # Get response from Mistral AI
        chat_response = mistral_client.chat(model=MISTRAL_MODEL, messages=messages)

        # Debugging: Print API response to verify structure
        print("generate_outline API Response:", chat_response)

        # Parse JSON response safely
        try:
            # Correctly access the content attribute using dot notation
            json_response = json.loads(chat_response.choices[0].message.content)
        except (json.JSONDecodeError, KeyError):
            print("Error: API response is not valid JSON or missing content.")
            return {"error": "Invalid API response"}

        # Ensure "title" exists before returning
        if "title" not in json_response:
            print("Error: 'title' key is missing from API response.")
            return {"error": "Missing title"}

        return json_response

    except Exception as e:
        print(f"Error in generate_outline: {e}")
        return {"error": "API request failed"}


def write_section(topic, header, sub_sections, text):
    """
    Writes a section of the article based on the given input.
    """
    try:
        SYSTEM_MESSAGE = f"You are a well-trained ghostwriter for writing articles about {topic}. " \
                         "Your articles are informative, detailed, and well-organized, " \
                         "written in a way that is easy to understand by all ages."

        # Extract headers from sub-sections (which are dictionaries)
        sub_section_headers = [sub_section["header"] for sub_section in sub_sections]
        sub_section_text = "\n\n".join(sub_section_headers)  # Join headers into a single string

        # Initialize Mistral client
        messages = [
            {"role": "system", "content": SYSTEM_MESSAGE},
            {"role": "system", "content": f"Previous sections:\n{text}"},
            {"role": "user", "content": f"Write section {header} with sub-sections:\n{sub_section_text}.\n"
                                        f"Make sure to use proper markdown formatting."}
        ]

        # Get response from Mistral AI
        chat_response = mistral_client.chat(model=MISTRAL_MODEL, messages=messages)

        # Debugging: Print API response to verify structure
        print("write_section API Response:", chat_response)

        # Check if response contains expected structure
        if hasattr(chat_response, 'choices') and chat_response.choices:
            # Correctly access the content attribute using dot notation
            return chat_response.choices[0].message.content
        else:
            raise ValueError("Unexpected API response format from Mistral AI.")

    except Exception as e:
        print(f"Error in write_section: {e}")
        return ""