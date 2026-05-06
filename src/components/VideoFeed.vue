<template>
  <div class="video-wrapper">
    <!-- The native HTML5 video element -->
    <video 
      ref="videoPlayer" 
      autoplay 
      playsinline 
      muted
      class="rpi-stream"
    ></video>
    
    <!-- Connection Status Overlay -->
    <div class="status-overlay" v-if="status !== 'Connected'">
      {{ status }}
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';

const videoPlayer = ref(null); 
const status = ref('Initializing...');

let pc = null;
let ws = null;

const connectWebRTC = async () => {
  // 1. Setup Peer Connection (Same STUN server from your Flutter code)
  pc = new RTCPeerConnection({
    iceServers: [{ urls: 'stun:stun.l.google.com:19302' }]
  });

  // 2. Bind the incoming video stream to our HTML video tag
  pc.ontrack = (event) => {
    if (event.streams && event.streams[0]) {
      videoPlayer.value.srcObject = event.streams[0];
      status.value = 'Connected';
    }
  };

  // 3. Your Raspberry Pi IPs
  const tailscaleIp = 'ws://100.68.113.75:8765';
  const localIp = 'ws://192.168.8.95:8765';

  try {
    status.value = 'Connecting via Tailscale...';
    ws = await connectWebSocket(tailscaleIp);
  } catch (e) {
    status.value = 'Connecting via Local Wi-Fi...';
    try {
      ws = await connectWebSocket(localIp);
    } catch (err) {
      status.value = 'Offline. Check Raspberry Pi.';
      return;
    }
  }

  // 4. Handle the WebRTC Handshake
  ws.onmessage = async (message) => {
    const data = JSON.parse(message.data);
    if (data.type === 'answer') {
      await pc.setRemoteDescription(new RTCSessionDescription(data.sdp));
    }
  };

  // 5. Send Offer
  const offer = await pc.createOffer();
  await pc.setLocalDescription(offer);
  ws.send(JSON.stringify({ type: 'offer', sdp: offer.sdp }));
};

// Helper function to handle WebSocket timeouts
const connectWebSocket = (url) => {
  return new Promise((resolve, reject) => {
    const socket = new WebSocket(url);
    const timer = setTimeout(() => {
      socket.close();
      reject(new Error("Timeout"));
    }, 3000); // 3 second timeout just like your Dart code

    socket.onopen = () => {
      clearTimeout(timer);
      resolve(socket);
    };
    socket.onerror = (err) => {
      clearTimeout(timer);
      reject(err);
    };
  });
};

onMounted(() => connectWebRTC());

onUnmounted(() => {
  if (ws) ws.close();
  if (pc) pc.close();
});
</script>

<style scoped>
.video-wrapper {
  position: relative;
  width: 100%;
  height: 100%;
  border-radius: 16px;
  overflow: hidden;
  background-color: #1e1e1e; /* Fallback dark background */
}

.rpi-stream {
  width: 100%;
  height: 100%;
  object-fit: cover; /* Ensures the video fills the box perfectly */
}

.status-overlay {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: #FFFFFF;
  font-size: 14px;
  font-weight: 600;
  background-color: rgba(0, 0, 0, 0.6);
  padding: 8px 16px;
  border-radius: 20px;
}
</style>