# # config.py

# # --- Gemini API Configuration ---
# # The API key is now stored directly in this file.
# #
# # IMPORTANT: Replace "YOUR_API_KEY_HERE" with your actual Gemini API key.
# API_KEY = "AIzaSyCl7ghU"


# # --- LLM Model Configuration ---
# # You can easily switch to other models here in the future.
# MODEL_NAME = "gemini-1.5-flash"


# # We add a small check to ensure the key placeholder has been replaced.
# if API_KEY == "YOUR_API_KEY_HERE" or not API_KEY:
#     # This error message is more specific to guide you.
#     print("CONFIGURATION ERROR: Please open the 'config.py' file and replace 'YOUR_API_KEY_HERE' with your actual Gemini API key.")
#     exit()











# config.py

# --- OpenAI API Configuration ---
# The API key is now stored directly in this file.
#
# IMPORTANT: Replace "YOUR_API_KEY_HERE" with your actual OpenAI API key.

API_KEY="api-key"  # Replace with your actual OpenAI API key.



# --- LLM Model Configuration ---
# You can easily switch to other models here in the future.
MODEL_NAME = "gpt-4.1-mini-2025-04-14" # Changed to an OpenAI model. You can use "gpt-4o" for better results if available.


# We add a small check to ensure the key placeholder has been replaced.
if API_KEY == "YOUR_API_KEY_HERE" or not API_KEY:
    # This error message is more specific to guide you.
    print("CONFIGURATION ERROR: Please open the 'config.py' file and replace 'YOUR_API_KEY_HERE' with your actual OpenAI API key.")
    exit()