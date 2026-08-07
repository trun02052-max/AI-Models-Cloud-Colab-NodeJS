const { google } = require('googleapis');
const WebSocket = require('ws');
const path = require('path');
//const express = require("express")
const mongoose = require('mongoose');

// 1. Connection URI (Replace with your database name/credentials)



//const app = express();

const PORT = 3000;

// 1. Configure Auth using your downloaded Service Account key
/*const auth = new google.auth.GoogleAuth({
    keyFile: path.join(__dirname, 'credentials.json'),
    scopes: ['https://googleapis.com'],
});
const drive = google.drive({ version: 'v3', auth });
*/
// 2. Helper to fetch the dynamic link from Google Drive
mongoose.connect(mongoURI, {
    dbName: "links"
});
    console.log('Successfully connected to MongoDB.');

const userSchema = new mongoose.Schema(
  {
    url: String
  },
  {
    collection: "links"
  }
);

const User = mongoose.models.User || mongoose.model("User", userSchema);
async function getLiveColabUrl() {
    /*console.log("Checking Google Drive for live Colab tunnel link...");
    
    // Search for the file by name inside your shared drive
    const response = await drive.files.list({
        q: "name='live_colab_url.txt'",
        fields: 'files(id, name)',
        spaces: 'drive'
    });

    const files = response.data.files;
    if (!files || files.length === 0) {
        throw new Error("No live link file found! Make sure your Colab script is currently running.");
    }

    // Download the contents of the text file
    const fileId = files[0].id;
    const fileContent = await drive.files.get({
        fileId: fileId,
        alt: 'media'
    });

    return fileContent.data.trim();*/
    await mongoose.connect(mongoURI, {
        dbName: "links"
    });
    console.log('Successfully connected to MongoDB.');

    // 3. Define Schema and Model

    // 4. Retrieve the latest document
    // Sorting by -1 on 'createdAt' or '_id' gets the newest entry
    const latestUser = await User.findOne().sort({ _id: -1 });

    if (latestUser) {
      console.log('Latest User Found:', latestUser);
      return latestUser.url
    } else {
      console.log('No documents found in the collection.');
    }
}

// 3. Execution Pipeline
async function run() {
    try {
        // Automatically discover the fresh link (changes every time Colab restarts)
        const targetUrl = await getLiveColabUrl();
        console.log(`Successfully connected to endpoint: ${targetUrl}`);

        const ws = new WebSocket(targetUrl);

        ws.on('open', () => {
            console.log('Handshake complete with hardware runtime.');

            // Call whichever specific block ID you want right here
            const requestPayload = {
                block: "analytical", 
                text: "Explain the working of for loops in programming"
            };

            ws.send(JSON.stringify(requestPayload));
        });

        ws.on('message', (rawData) => {
            const response = JSON.parse(rawData);
            console.log('\n--- TARGET CELL RESULT ---');
            console.log(response.result);
            console.log('--------------------------\n');
            ws.close();
        });

        ws.on('error', (err) => {
            console.error('WebSocket connection dropped:', err.message);
        });

    } catch (error) {
        console.error("Automation error:", error.message);
    }
}

// Fire the program
run();



/*app.listen(PORT, () => {
    console.log(`Express server is running on http://localhost:${PORT}`);
});
*/
