"""
Quick test script to verify OpenAI integration
"""
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv('OPENAI_API_KEY')

if not api_key or api_key == "your-openai-api-key-here":
    print("❌ ERROR: OpenAI API key not configured!")
    print("\n📝 Steps to fix:")
    print("1. Get your API key from: https://platform.openai.com/api-keys")
    print("2. Open backend/.env file")
    print("3. Replace 'your-openai-api-key-here' with your actual key")
    print("4. Run this test again")
else:
    print("✅ OpenAI API key is configured!")
    print(f"   Key starts with: {api_key[:20]}...")
    
    # Test the API
    try:
        client = OpenAI(api_key=api_key)
        print("\n🧪 Testing OpenAI connection...")
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "user", "content": "Say 'Hello! OpenAI is working!' in a friendly way."}
            ],
            max_tokens=50
        )
        
        print("✅ OpenAI API is working!")
        print(f"   Response: {response.choices[0].message.content}")
        print("\n🎉 All systems ready! You can start the backend server.")
        
    except Exception as e:
        print(f"\n❌ ERROR testing OpenAI API: {str(e)}")
        print("\n📝 Possible issues:")
        print("- Invalid API key")
        print("- No credits/payment method on OpenAI account")
        print("- Network connection issues")
        print("- Check: https://platform.openai.com/account/billing")
