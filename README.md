# AI-Models-Cloud-Colab-NodeJS

A Node.js & Python application that bridges Google Colab with a Node.js client to run AI models remotely and retrieve results via WebSocket communication.

## 📋 Overview

This project enables interaction between a local Node.js application and Python-based AI models running in Google Colab. It leverages Colab's cloud GPU runtime and can persist model files in Google Drive so you don't have to re-download them every time.

Note: Colab provides remote compute resources — the heavy model inference runs on Google's servers, not on your local machine. The Node.js client only sends requests and receives responses over WebSocket.

### Key Features

- **Runs AI models in Google Colab**: Uses Colab's GPU runtime for model inference (free tiers available but with usage limits).
- **Persistent model storage in Google Drive**: Optionally installs and caches model files in your Google Drive folder to reduce repeated downloads between sessions.
- **Hugging Face-compatible**: Models from Hugging Face can be used, so you're not limited to any specific model family.
- **WebSocket Communication**: Real-time bidirectional communication between Node.js and the Colab server.
- **MongoDB Integration**: Stores and retrieves dynamic Colab tunnel URLs for the client to connect.
- **Ngrok Tunneling**: Exposes the Colab server with a public URL when needed.
- **Secure Credentials**: Uses Colab Secrets / environment variables for credentials management.

## 🚀 Quick Start

### Prerequisites

- Node.js 14+
- Python 3.8+
- Google account with access to Google Colab
- MongoDB Atlas account (or local MongoDB instance)
- Ngrok account (optional, for public tunnels)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/trun02052-max/AI-Models-Cloud-Colab-NodeJS.git
   cd AI-Models-Cloud-Colab-NodeJS
   ```

2. **Install Node.js dependencies**
   ```bash
   npm install
   ```
   Required packages:
   - `googleapis`
   - `ws` (WebSocket)
   - `mongoose`

3. **Python Setup (in Google Colab)**
   - Required libraries will be auto-installed by `colab.py` when you run the notebook/script
   - Key dependencies:
     - `unsloth` (project-specific LLM runner)
     - `pymongo`
     - `pyngrok`
     - `websockets`

## ⚙️ Configuration

### Colab Setup (`colab.py`)

1. Set your MongoDB connection URI:
   ```python
   uri = "your_mongodb_connection_string"
   ```

2. (Optional) Set Ngrok auth token:
   ```python
   ngrok.set_auth_token("your_ngrok_token")
   ```

3. Set your Google Drive paths (optional — used to cache models):
   ```python
   gdrive_cache_dir = '/content/drive/MyDrive/AI_Models'
   FOLDER_PATH = "/content/drive/MyDrive/ColabAutomation"
   ```

### Node.js Setup (`i.js`)

1. Set your MongoDB connection URI:
   ```javascript
   const mongoURI = "your_mongodb_connection_string";
   ```

2. (Optional) Set Google Drive credentials if using Drive-based link retrieval:
   ```javascript
   const auth = new google.auth.GoogleAuth({
       keyFile: path.join(__dirname, 'credentials.json'),
       scopes: ['https://www.googleapis.com/auth/drive'],
   });
   ```

## 📝 Usage

### Starting the Colab Server

1. Open `colab.py` in Google Colab
2. Run all cells sequentially
3. The server will:
   - Initialize configured AI models
   - Create an Ngrok tunnel (if enabled)
   - Store the WebSocket URL in MongoDB
   - Listen for incoming WebSocket connections

Important operational notes (rephrased and checked):
- Google Colab provides free GPU access on some tiers, but it has usage limits, session timeouts, and resource restrictions. It is not a guaranteed continuous GPU server.
- Model inference and loading run on Colab (Google's cloud). Your local machine does not need an NVIDIA GPU or large VRAM to run the models — the Node.js client only communicates over the network.
- Loading large models can take several minutes (often anywhere from a couple to several minutes depending on model size and network/storage speed). Each new Colab session typically needs to load model weights into the Colab runtime's memory/GPU before inference can start.
- Storing model files in Google Drive can reduce repeated downloads between sessions, but Drive access is slower than local disk. Even when model files are cached in Drive, they still must be loaded into the Colab runtime memory/GPU each session.
- Colab sessions can disconnect or be limited in length (and sometimes in idle time). For production or low-latency needs, consider paid compute or a persistent server.
- Because models are loaded on-demand in the cloud, cold starts cause longer latency — the workflow is best for intermittent or batch workloads rather than low-latency streaming APIs.

### Running the Node.js Client

```bash
node i.js
```

The client will:
1. Connect to MongoDB and retrieve the latest Colab tunnel URL
2. Establish a WebSocket connection to the Colab server
3. Send a sample request:
   ```json
   {
     "block": "analytical",
     "text": "Explain the working of for loops in programming"
   }
   ```
4. Receive and log the AI model's response
5. Close the connection

### Available Blocks

- `analytical`: Routes to the larger analytical model (configurable)
- `gethelp`: Routes to the smaller counselor model (configurable)

### Request Format

```json
{
  "block": "analytical|gethelp",
  "text": "Your input text here"
}
```

### Response Format

```json
{
  "status": "done",
  "result": "AI model response here"
}
```

## 💡 Use Cases

- Code explanation and learning assistance
- Mental health / conversational assistance (if configured responsibly)
- Offloading model inference to Colab's GPU for development and experimentation

## 🔧 Advanced Configuration

### Model Parameters

Edit in `colab.py`:
```python
max_seq_length = 2048  # Maximum sequence length
load_in_4bit = True    # 4-bit quantization for memory efficiency (if supported)
max_new_tokens = 700   # Analytical model output length
# adjust smaller-model tokens separately
```

### Hugging Face and Custom Models

This project is compatible with models hosted on Hugging Face, so you can swap in other compatible model checkpoints or families. You're not limited to any single provider or a fixed set of two models — the code can be adapted to run other models supported by the runtime and framework.

### Counselor System Prompt

Customize the counselor model's behavior in `colab.py` (example):
```python
second_smaller_model = (
    "You are an objective AI counselor practicing Cognitive Behavioral Therapy. "
    "Do not flatter the user. Do not blindly take their side. Point out cognitive distortions "
    "and challenge unfair or toxic behaviors logically and gently."
)
```

## 📦 Project Structure

```
AI-Models-Cloud-Colab-NodeJS/
├── colab.py          # Google Colab server script with AI models
├── i.js              # Node.js WebSocket client
├── LICENSE           # MIT License
└── README.md         # This file
```

## 🔐 Security Considerations

- **MongoDB Credentials**: Use Colab Secrets or environment variables for sensitive data
- **Ngrok Tokens**: Store in environment variables, not in code
- **Google Credentials**: Keep service account keys out of version control
- **WebSocket Security**: Add authentication for production use

## 🛠️ Troubleshooting

### WebSocket Connection Failed
- Ensure Colab script is still running
- Check MongoDB has the latest URL entry
- Verify Ngrok tunnel is active

### MongoDB Connection Error
- Verify connection string is correct
- Check network access rules in MongoDB Atlas
- Ensure database and collection exist

### Model Loading / Cold Start
- Models can take several minutes to load on first run, especially large models. Caching model files in Google Drive helps but does not remove the need to load weights into GPU memory each session.

### Out of Memory (OOM)
- 4-bit quantization reduces memory usage but Colab GPUs (free tier) have limited VRAM. Consider smaller models if OOM persists.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs and issues
- Suggest new features
- Submit pull requests
- Improve documentation

## 📧 Contact

For questions or support, please open an issue in the GitHub repository.

---

**Note**: This project relies on Google Colab and MongoDB. Colab's free resources are subject to change and usage limits. For stable, production-grade deployments consider using paid cloud GPU instances or managed services.
