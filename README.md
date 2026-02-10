
A Python-based WebSocket server that bridges the Xiaozhi ESP32 device with LM Studio.

Components
Server: 
xiaozhi_bridge/server.py
 (WebSocket server)
Protocol: 
xiaozhi_bridge/protocol.py
 (Handles Xiaozhi v3 protocol)
Audio: 
xiaozhi_bridge/audio_utils.py
 (Opus <-> PCM conversion)
ASR: Faster-Whisper (local)
TTS: Edge-TTS (online)
LLM: LM Studio (local OpenAI API)
Setup
Install Dependencies:

bash
./run.sh
(or manually: pip install -r requirements.txt)

Start LM Studio:

Load a model.
Start the Local Server on port 1234.
Run Bridge Server:

bash
./run.sh
Configure Device: To point your Xiaozhi ESP32 to this server, you need to modify the firmware source code before building/flashing.

Open xiaozhi-esp32/main/protocols/websocket_protocol.cc and modify the OpenAudioChannel method (around line 85):

cpp
bool WebsocketProtocol::OpenAudioChannel() {
    Settings settings("websocket", false);
    // Original: std::string url = settings.GetString("url");
    
    // Modify to point to your computer's IP:
    std::string url = "ws://192.168.1.100:8000"; 
    
    std::string token = settings.GetString("token");
    // ...
}
Replace 192.168.1.100 with your actual LAN IP address.

Then rebuild and flash the firmware:

bash
idf.py build flash monitor
Verification
Run python test_client.py to verify the server is reachable and protocol is working.
Verification Results
I have verified the server implementation by running 
test_client.py
. Server Log:

New connection from ('127.0.0.1', 50976)
Received JSON: {'type': 'hello', ...}
Sent Hello response
Client Log:

Connected!
Sent Hello
Received: {"type": "hello", ...}
Handshake successful!
