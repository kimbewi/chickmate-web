<template>
  <div class="video-wrapper">

    <video 
      ref="videoPlayer" 
      autoplay 
      playsinline 
      :muted="isMuted" 
      class="rpi-stream"
      @dblclick="toggleFullScreen"
    ></video>
    
    <div class="status-overlay" v-if="status !== 'Connected'">
      {{ status }}
    </div>

    <!-- Video Controls Container -->
    <div class="video-controls" v-if="status === 'Connected'">
      
      <!-- Hover-based Volume Container -->
      <div class="volume-container">
        
        <!-- Vertical Slider -->
        <div class="slider-popup">
          <input 
            type="range" 
            class="vertical-slider" 
            min="0" max="1" step="0.01" 
            v-model="volume" 
            @input="handleVolumeDrag"
          />
        </div>

        <!-- Mute/Unmute Icon -->
        <button class="icon-btn volume-btn" @click="toggleMute" :title="isMuted ? 'Unmute' : 'Mute'">
          <svg v-if="isMuted || volume === 0" viewBox="0 0 24 24" width="20" height="20" stroke="currentColor" stroke-width="2" fill="none">
            <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon>
            <line x1="23" y1="9" x2="17" y2="15"></line>
            <line x1="17" y1="9" x2="23" y2="15"></line>
          </svg>
          <svg v-else viewBox="0 0 24 24" width="20" height="20" stroke="currentColor" stroke-width="2" fill="none">
            <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon>
            <path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07"></path>
          </svg>
        </button>
      </div>

      <!-- Fullscreen Button -->
      <button class="icon-btn fullscreen-btn" @click="toggleFullScreen" title="Fullscreen">
        <svg viewBox="0 0 24 24" width="20" height="20" stroke="currentColor" stroke-width="2" fill="none">
          <path d="M8 3H5a2 2 0 0 0-2 2v3m18 0V5a2 2 0 0 0-2-2h-3m0 18h3a2 2 0 0 0 2-2v-3M3 16v3a2 2 0 0 0 2 2h3"></path>
        </svg>
      </button>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';

const videoPlayer = ref(null); 
const status = ref('Connecting...');

// --- AUDIO STATE ---
const isMuted = ref(true); 
const volume = ref(0);    
const previousVolume = ref(0.5);  
let pc = null;
let ws = null;

// --- FIXED AUDIO SYNC LOGIC ---
const toggleMute = () => {
  isMuted.value = !isMuted.value;
  
  if (isMuted.value) {
    if (volume.value > 0) previousVolume.value = volume.value;
    volume.value = 0;
    if (videoPlayer.value) videoPlayer.value.volume = 0;
  } else {
    volume.value = previousVolume.value;
    if (videoPlayer.value) videoPlayer.value.volume = volume.value;
  }
};

const handleVolumeDrag = (e) => {
  const newVol = parseFloat(e.target.value);
  if (videoPlayer.value) videoPlayer.value.volume = newVol;
  
  if (newVol === 0) {
    isMuted.value = true;
  } else {
    isMuted.value = false;
    previousVolume.value = newVol; 
  }
};

// --- FULLSCREEN LOGIC ---
const toggleFullScreen = () => {
  if (!document.fullscreenElement) {
    if (videoPlayer.value.requestFullscreen) videoPlayer.value.requestFullscreen();
    else if (videoPlayer.value.webkitRequestFullscreen) videoPlayer.value.webkitRequestFullscreen();
  } else {
    if (document.exitFullscreen) document.exitFullscreen();
    else if (document.webkitExitFullscreen) document.webkitExitFullscreen();
  }
};

// --- WEBRTC CONNECTION LOGIC ---
const connectWebRTC = async () => {
  pc = new RTCPeerConnection({ iceServers: [{ urls: 'stun:stun.l.google.com:19302' }] });
  pc.addTransceiver('video', { direction: 'recvonly' });
  pc.addTransceiver('audio', { direction: 'recvonly' });

  pc.ontrack = (event) => {
    if (event.streams && event.streams[0]) {
      videoPlayer.value.srcObject = event.streams[0];
      videoPlayer.value.volume = volume.value; 
      status.value = 'Connected';
    }
  };

  pc.onicecandidate = (event) => {
    if (event.candidate && ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ type: 'candidate', candidate: event.candidate }));
    }
  };

  const tailscaleIp = 'ws://100.68.113.75:8765';
  const localIp = 'ws://192.168.8.95:8765';

  try { ws = await connectWebSocket(tailscaleIp); } 
  catch (e) {
    try { ws = await connectWebSocket(localIp); } 
    catch (err) { status.value = 'Offline. Check Raspberry Pi.'; return; }
  }

  ws.onmessage = async (message) => {
    const data = JSON.parse(message.data);
    if (data.type === 'answer') await pc.setRemoteDescription(new RTCSessionDescription(data));
    else if (data.type === 'candidate') await pc.addIceCandidate(new RTCIceCandidate(data.candidate));
  };

  const offer = await pc.createOffer();
  let sdp = offer.sdp;
  if (sdp.includes('useinbandfec=1')) {
      sdp = sdp.replace('useinbandfec=1', 'useinbandfec=1; stereo=1; maxaveragebitrate=128000; sprop-stereo=1');
  }
  await pc.setLocalDescription({ type: offer.type, sdp: sdp });
  ws.send(JSON.stringify(pc.localDescription));
};

const connectWebSocket = (url) => {
  return new Promise((resolve, reject) => {
    const socket = new WebSocket(url);
    const timer = setTimeout(() => { socket.close(); reject(new Error("Timeout")); }, 3000); 
    socket.onopen = () => { clearTimeout(timer); resolve(socket); };
    socket.onerror = (err) => { clearTimeout(timer); reject(err); };
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
  background-color: #1e1e1e;
}

.rpi-stream {
  width: 100%;
  height: 100%;
  object-fit: cover; 
  cursor: pointer;
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

/* --- Controls Layout --- */
.video-controls {
  position: absolute;
  bottom: 16px;
  right: 16px;
  display: flex;
  gap: 12px;
  align-items: center;
}

.fullscreen-btn {
  background-color: rgba(0, 0, 0, 0.5);
  padding: 8px;
  border-radius: 50%;
  backdrop-filter: blur(4px);
}

.icon-btn {
  color: white;
  border: none;
  background: transparent;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: transform 0.2s ease, opacity 0.2s ease;
  opacity: 0.8;
}

.icon-btn:hover {
  transform: scale(1.1);
  opacity: 1;
}

.volume-container {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.volume-btn {
  background: transparent; 
  padding: 8px;
  border-radius: 50%;
  z-index: 2; 
}

.slider-popup {
  position: absolute;
  bottom: 100%; 
  left: 50%;
  transform: translateX(-50%);
  margin-bottom: 4px; 
  background-color: rgba(0, 0, 0, 0.5);
  border-radius: 20px;
  backdrop-filter: blur(4px);
  height: 100px; 
  width: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  
  opacity: 0;
  visibility: hidden;
  transition: opacity 0.2s ease, visibility 0.2s ease, transform 0.2s ease;
  transform-origin: bottom center;
}

.volume-container:hover .slider-popup {
  opacity: 1;
  visibility: visible;
}

.vertical-slider {
  -webkit-appearance: none;
  appearance: none;
  width: 80px; 
  height: 4px; 
  background: rgba(255, 255, 255, 0.3);
  border-radius: 2px;
  outline: none;
  cursor: pointer;
  transform: rotate(-90deg); 
}

.vertical-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: white;
  cursor: pointer;
  transition: transform 0.1s ease;
}

.vertical-slider::-webkit-slider-thumb:hover {
  transform: scale(1.3);
}

.vertical-slider::-moz-range-thumb {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: white;
  cursor: pointer;
  border: none;
}
</style>