import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def upload_to_gemini(path, mime_type=None):
  """Uploads the given file to Gemini.

  See https://ai.google.dev/gemini-api/docs/prompting_with_media
  """
  file = genai.upload_file(path, mime_type=mime_type)
  print(f"Uploaded file '{file.display_name}' as: {file.uri}")
  return file

def get_answer(img_name):
    # Create the model
    generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
    }

    model = genai.GenerativeModel(
    model_name="gemini-2.0-flash-exp",
    generation_config=generation_config,
    )

    files = [
    upload_to_gemini(img_name, mime_type="image/jpeg"),
    ]

    chat_session = model.start_chat(
    history=[
        {
        "role": "user",
        "parts": [
            files[0],
            "here is an image.",
        ],
        },
    ]
    )

    response = chat_session.send_message("what is written in the image? reply only with the contents of the image using latin characters and numbers")

    return response.text