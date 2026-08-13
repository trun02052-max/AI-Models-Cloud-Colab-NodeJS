import os
from google.colab import drive
import asyncio, websockets, json, nest_asyncio, os
from pyngrok import ngrok
import pymongo
from google.colab import userdata

# Retrieve the password securely from Colab Secrets
#db_password = userdata.get('MONGO_PASSWORD')

# Define connection string
#add uri

# Establish connection
client = pymongo.MongoClient(uri)

# Test connection
try:
    client.admin.command('ping')
    print("Successfully connected to MongoDB Atlas!")
except Exception as e:
    print(f"Connection failed: {e}")



# 1. Mount your Google Drive
drive.mount('/content/drive')

# 2. Setup your target permanent storage directory
gdrive_cache_dir = '/content/drive/MyDrive/AI_Models'
os.makedirs(gdrive_cache_dir, exist_ok=True)

# 3. Direct Hugging Face to write straight to this folder
os.environ["HF_HOME"] = gdrive_cache_dir
print(f"Success! Models will download directly to Google Drive: {gdrive_cache_dir}")

#Folder for ngrok stuff
FOLDER_PATH = "/content/drive/MyDrive/ColabAutomation"
os.makedirs(FOLDER_PATH, exist_ok=True)

nest_asyncio.apply()

# Install unsloth library silently
!pip install -q unsloth

from unsloth import FastLanguageModel
import torch

# Configuration details
max_seq_length = 2048
dtype = None # Auto-detects Colab's T4 GPU
load_in_4bit = True # CRITICAL: Keeps storage size low

print("Downloading/Loading Model 1: 7B Analytical Model...")
analytical_model, analytical_tokenizer = FastLanguageModel.from_pretrained(
    model_name = "unsloth/DeepSeek-R1-Distill-Qwen-7B-bnb-4bit",
    max_seq_length = max_seq_length,
    dtype = dtype,
    load_in_4bit = load_in_4bit,
)
FastLanguageModel.for_inference(analytical_model)

print("\nDownloading/Loading Model 2: 1.5B Therapy Model...")
second_smaller_model, second_tokenizer = FastLanguageModel.from_pretrained(
    model_name = "unsloth/DeepSeek-R1-Distill-Qwen-1.5B-bnb-4bit",
    max_seq_length = max_seq_length,
    dtype = dtype,
    load_in_4bit = load_in_4bit,
)
FastLanguageModel.for_inference(second_smaller_model)

print("\n Both models are successfully saved into your Google Drive!")

def analytical(ain):


#analysis_user_input = "If I have two lists in Python, each having elements corresponding to the other (at the same index). How do I sort one list and ensure that the other gets sorted in the same way?"

  inputs = analytical_tokenizer(
      [f"<｜begin of sentence｜>User: {ain}\n\nAssistant:"],
      return_tensors = "pt"
  ).to("cuda")

# Generate response via the larger 7B Model
  outputs = analytical_model.generate(**inputs, max_new_tokens = 700)
  return analytical_tokenizer.decode(outputs[0], skip_special_tokens=True)

second_smaller_model = (
    "You are an objective AI counselor practicing Cognitive Behavioral Therapy. "
    "Do not flatter the user. Do not blindly take their side. Point out cognitive distortions "
    "and challenge unfair or toxic behaviors logically and gently."
) #example preprompt

def second(the):



  # Compile context format
  input = second_tokenizer(
      [f"<｜begin of sentence｜>{second_smaller_model}\n\nUser: {the}\n\nAssistant:"],
      return_tensors = "pt"
  ).to("cuda")

# Generate response via the 1.5B Model
  output = second_smaller_model.generate(**input, max_new_tokens = 512)
  return (second_tokenizer.decode(output[0], skip_special_tokens=True))

# --- BLOCK 4: Automated Link Discovery & Auto-Shutdown ---

# Create a synchronization event to control server lifecycle
stop_event = asyncio.Event()
#removed path argument in the function
async def router_with_shutdown(websocket):
    try:
        async for message in websocket:
            payload = json.loads(message)
            target_block = payload.get("block")
            user_text = payload.get("text")

            if target_block == "analytical":
                o = analytical(user_text)
            elif target_block == "gethelp":
                o = second(user_text)
            else:
                o = "Error: Block not found"

            # Send result back to Node.js
            await websocket.send(json.dumps({"status": "done", "result": o}))

            # Message sent! Trigger the shutdown event
            print("Processing complete. Triggering graceful shutdown...")
            stop_event.set()
            break  # Exit the message loop
    except Exception as e:
        print(f"Error occurred: {e}")
        stop_event.set()

# Authenticate and connect Ngrok
#set up ngrok 
#tunnel = ngrok.connect(8765, "tcp")
#clean_url = tunnel.public_url.replace("tcp://", "ws://")

tunnel = ngrok.connect(8765, "http")
clean_url = tunnel.public_url.replace("https://", "wss://")

#mongo
db = client["links"]
collection = db["links"]

# 3. Insert a single document
single_document = {
    "url": str(clean_url),
}

insert_one_result = collection.insert_one(single_document)
print(f"Inserted single document with url")
#mongo

async def main_server_lifecycle():
    # Start the server using our updated handler
    async with websockets.serve(router_with_shutdown, "localhost", 8765):
        # Wait right here until stop_event.set() is called by the handler
        await stop_event.wait()

    # Clean up the ngrok tunnel so it doesn't leak connections
    print("Closing ngrok tunnel...")
    ngrok.disconnect(tunnel.public_url)

# Execute the lifecycle
asyncio.get_event_loop().run_until_complete(main_server_lifecycle())
print("🏁 Colab cell finished execution completely.")
