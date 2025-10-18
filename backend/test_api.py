import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
print(f"API Key (first 20 chars): {api_key[:20] if api_key else 'NOT FOUND'}")

if api_key:
    try:
        client = OpenAI(api_key=api_key)
        
        # Test with gpt-4o
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": "Say hello"}],
            max_tokens=50
        )
        print(f"\n✅ SUCCESS with gpt-4o!")
        print(f"Response: {response.choices[0].message.content}")
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        
        # Try gpt-3.5-turbo as fallback
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Say hello"}],
                max_tokens=50
            )
            print(f"\n✅ SUCCESS with gpt-3.5-turbo!")
            print(f"Response: {response.choices[0].message.content}")
        except Exception as e2:
            print(f"\n❌ ERROR with gpt-3.5-turbo too: {str(e2)}")
else:
    print("❌ OPENAI_API_KEY not found in .env file!")