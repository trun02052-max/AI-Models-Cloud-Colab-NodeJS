# smth-rando

A Node.js & Python application that bridges Google Colab with a Node.js client to run AI models remotely and retrieve results via WebSocket communication.

## 📋 Overview

This project enables seamless interaction between a Node.js application and Python-based AI models running in Google Colab. It uses MongoDB to store dynamic tunnel URLs and WebSocket communication for real-time message passing.

### Key Features

- **Dual AI Model Support**: Runs two language models (7B and 1.5B parameter models) in parallel
- **Google Colab Integration**: Leverages Colab's GPU runtime with persistent storage via Google Drive
- **WebSocket Communication**: Real-time bidirectional communication between Node.js and Python
- **MongoDB Integration**: Stores and retrieves dynamic Colab tunnel URLs
- **Ngrok Tunneling**: Exposes local Colab server with public URLs
- **Secure Credentials**: Uses Google Colab Secrets for credential management

## 🏗️ Architecture

### Components

**Backend (Python - `colab.py`)**
- Runs in Google Colab for GPU acceleration
- Hosts two LLM models using Unsloth framework:
  - **Analytical Model**: DeepSeek-R1-Distill-Qwen-7B (analysis tasks)
  - **Counselor Model**: DeepSeek-R1-Distill-Qwen-1.5B (CBT-based assistance)
- Exposes WebSocket server on port 8765
- Uses Ngrok for public tunnel access
- Stores connection URL in MongoDB

**Frontend (Node.js - `i.js`)**
- Client application running locally
- Connects to Colab via WebSocket using MongoDB-retrieved URL
- Sends requests with block type and input text
- Receives and logs AI model responses

## 🚀 Quick Start

### Prerequisites

- Node.js 14+
- Python 3.8+
- Google Colab account with GPU runtime
- MongoDB Atlas account (or local MongoDB instance)
- Ngrok account

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/trun02052-max/smth-rando.git
   cd smth-rando
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
   - Required libraries will be auto-installed by `colab.py`
   - Key dependencies:
     - `unsloth`
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

3. Set your Google Drive paths:
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
   - Initialize both AI models
   - Create an Ngrok tunnel
   - Store the WebSocket URL in MongoDB
   - Listen for incoming WebSocket connections

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

- **`analytical`**: Routes to the 7B analytical model (DeepSeek-R1-Distill-Qwen-7B)
- **`gethelp`**: Routes to the 1.5B counselor model (DeepSeek-R1-Distill-Qwen-1.5B)

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

- **Code Explanation**: Use the analytical model to explain programming concepts
- **Mental Health Support**: Use the counselor model for CBT-based assistance
- **Learning Assistant**: Get detailed explanations for various topics
- **Remote AI Processing**: Offload computationally expensive tasks to Colab's GPU

## 🔧 Advanced Configuration

### Model Parameters

Edit in `colab.py`:
```python
max_seq_length = 2048  # Maximum sequence length
load_in_4bit = True    # 4-bit quantization for memory efficiency
max_new_tokens = 700   # Analytical model output length
max_new_tokens = 512   # Counselor model output length
```

### Counselor System Prompt

Customize the counselor model's behavior:
```python
second_smaller_model = (
    "You are an objective AI counselor practicing Cognitive Behavioral Therapy. "
    "Do not flatter the user. Do not blindly take their side. Point out cognitive distortions "
    "and challenge unfair or toxic behaviors logically and gently."
)
```

## 📦 Project Structure

```
smth-rando/
├── colab.py          # Google Colab server script with AI models
├── i.js              # Node.js WebSocket client
├── LICENSE           # MIT License
└── README.md         # This file
```

## 🔐 Security Considerations

- **MongoDB Credentials**: Use Colab Secrets for sensitive data
- **Ngrok Tokens**: Store in environment variables, not in code
- **Google Credentials**: Keep service account keys out of version control
- **WebSocket Security**: Consider adding authentication tokens for production use

## 🛠️ Troubleshooting

### WebSocket Connection Failed
- Ensure Colab script is still running
- Check MongoDB has the latest URL entry
- Verify Ngrok tunnel is active

### MongoDB Connection Error
- Verify connection string is correct
- Check network access rules in MongoDB Atlas
- Ensure database and collection exist

### Model Loading Timeout
- Increase Colab GPU quotas if available
- Models may take 2-3 minutes to load on first run
- Check for sufficient disk space in Google Drive

### Out of Memory (OOM)
- The 4-bit quantization helps, but Colab T4 GPU is limited (~15GB)
- Consider using smaller models if OOM persists

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

**Note**: This project is best run with proper credentials configured and active Google Colab and MongoDB instances.
