import google.generativeai as genai

genai.configure(api_key="")

models = genai.list_models()

for m in models:
    print(f"Model name: {m.name}")
    if "generateContent" in m.supported_generation_methods:
        print("✅ Supports generateContent")
