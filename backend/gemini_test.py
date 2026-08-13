import os

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI


# Load the .env file used by Member 1's code
load_dotenv("app/.env")


# Get API key
api_key = os.getenv("GEMINI_API_KEY")

print("=" * 60)
print("GEMINI API CONNECTION TEST")
print("=" * 60)

print("\nAPI key loaded:", bool(api_key))

if not api_key:
    raise RuntimeError(
        "GEMINI_API_KEY was not found in backend/app/.env"
    )


print("Creating Gemini model...")

llm = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash",
    google_api_key=api_key,
    timeout=60,
)

print("Gemini model created successfully!")

print("\nSending test request...")

response = llm.invoke(
    "Reply with exactly: Gemini API is working."
)

print("\nGemini response:")
print(response.content)

print("\n" + "=" * 60)
print("TEST SUCCESSFUL")
print("=" * 60)