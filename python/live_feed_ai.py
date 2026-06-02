import asyncio
import json
import logging
import pyaudio
import websockets
import time
import fractions
import numpy as np
import threading
import cv2 
import os 
#import the .env file
from dotenv import load_dotenv 
from av import VideoFrame, AudioFrame
from aiortc import (
    RTCPeerConnection,
    RTCSessionDescription,
    VideoStreamTrack,
    AudioStreamTrack,
    RTCConfiguration
)
from aiortc.sdp import candidate_from_sdp
from picamera2 import Picamera2

# ===== BIOACOUSTIC IMPORTS (ADDED) =====
import scipy.signal as signal 
from collections import Counter
from collections import deque
from statistics import mode
import queue

# --- FIREBASE IMPORTS ---
import firebase_admin
from firebase_admin import credentials, db

# Load environment variables from .env file
load_dotenv()

# Check for AI
try:
    import tflite_runtime.interpreter as tflite
    AI_AVAILABLE = True
except ImportError:
    try:
        import tensorflow.lite as tflite
        AI_AVAILABLE = True
    except ImportError:
        logging.warning("TFLite/TensorFlow not installed. AI features disabled.")
        AI_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==========================================
# 0. FIREBASE SETUP
# ==========================================
try:
    # Fetch credentials path and database URL securely from .env
    cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH")
    db_url = os.getenv("FIREBASE_DATABASE_URL")

    cred = credentials.Certificate(cred_path)
    
    firebase_admin.initialize_app(cred, {
        'databaseURL': db_url 
    })
    
    # SAVES TO: aiResult/cv
    firebase_ref = db.reference('aiResult/cv')
    logger.info("FIREBASE CONNECTED SUCCESSFULLY")
    
except Exception as e:
    logger.error(f"FIREBASE INIT FAILED: {e}")
    firebase_ref = None

# ==========================================
# 1. GLOBAL CAMERA SETUP
# ==========================================
try:
    global_picam = Picamera2()
    # Bait & Switch for Wide Angle
    config = global_picam.create_video_configuration(
        main={"size": (1640, 1232), "format": "RGB888"}
    )
    config["main"]["size"] = (640, 480) 
    config["main"]["framerate"] = 30
    
    global_picam.configure(config)
    global_picam.start()
    global_picam.set_controls({"FrameDurationLimits": (33333, 33333)})

    logger.info("GLOBAL CAMERA STARTED")
except Exception as e:
    logger.error(f"CAMERA FAILED TO START: {e}")

# ==========================================
# 2. GLOBAL INFERENCE (AI) - UPDATED
# ==========================================

def softmax(x):
    e_x = np.exp(x - np.max(x))
    return e_x / e_x.sum()

class GlobalInference:
    def __init__(self, model_path="/home/raprap/efficientnetb0/chickmate0426.tflite"):
        if not AI_AVAILABLE:
            self.latest_prediction = "AI Missing"
            return

        self.running = True
        self.latest_prediction = "Initializing..."
        self.last_uploaded_status = ""
        self.last_upload_time = 0
        
        self.labels = ['Cold', 'Hot', 'Normal']

        # --- NEW: SMOOTHING VARIABLES ---
        self.history = []        
        # 20 frames * 3 seconds = 60 seconds (1 minute of observation)
        self.history_limit = 20
        
        try:
            logger.info(f"Loading Model: {model_path}")
            self.interpreter = tflite.Interpreter(model_path=model_path)
            self.interpreter.allocate_tensors()
            self.input_details = self.interpreter.get_input_details()
            self.output_details = self.interpreter.get_output_details()
            
            self.thread = threading.Thread(target=self._inference_loop, daemon=True)
            self.thread.start()
        except Exception as e:
            logger.error(f"AI Load Error: {e}")
            self.latest_prediction = "AI Error"

    def _inference_loop(self):
        while self.running:
            try:
                frame = global_picam.capture_array()
                
                # 1. Resize to 224x224
                input_shape = self.input_details[0]['shape']
                resized = cv2.resize(frame, (input_shape[1], input_shape[2]))
                input_data = np.expand_dims(resized, axis=0)
                
                # 2. Use Raw Values
                if self.input_details[0]['dtype'] == np.float32:
                    input_data = np.float32(input_data)

                # 3. Run Inference
                self.interpreter.set_tensor(self.input_details[0]['index'], input_data)
                self.interpreter.invoke()
                
                # 4. Get Output & Softmax
                output_data = self.interpreter.get_tensor(self.output_details[0]['index'])[0]
                scores = softmax(output_data)
                pred_idx = np.argmax(scores)
                confidence = scores[pred_idx] * 100 
                
                # 5. Get Raw Label
                raw_status = "Unknown"
                if pred_idx < len(self.labels):
                    raw_status = self.labels[pred_idx]
                else:
                    raw_status = f"Class {pred_idx}"
# --- NEW: SMOOTHING & VOTING LOGIC ---
                # Add current result to history
                self.history.append(raw_status)
                
                # Keep history size limited
                if len(self.history) > self.history_limit:
                    self.history.pop(0)

                # Calculate the percentage of each status in our 1-minute history
                vote_counts = Counter(self.history)
                history_len = len(self.history)
                
                cold_percent = vote_counts.get("Cold", 0) / history_len
                hot_percent = vote_counts.get("Hot", 0) / history_len

                # THE FIX: Require 70% consistency to trigger an alarm state. 
                # This completely filters out temporary 10-15 second clumping.
                if cold_percent >= 0.70:
                    final_status = "Cold"
                elif hot_percent >= 0.70:
                    final_status = "Hot"
                else:
                    # If they are just temporarily clumping, it defaults to Normal
                    final_status = "Normal"

                # Update Global Variable with the WINNER
                self.latest_prediction = f"{final_status}"
                
                # 6. FIREBASE UPDATE (Only send the smoothed Final Status)
                current_time = time.time()
                # Check against final_status, not raw_status
                if firebase_ref and (final_status != self.last_uploaded_status or (current_time - self.last_upload_time > 10)):
                    try:
                        firebase_ref.set(final_status)
                        self.last_uploaded_status = final_status
                        self.last_upload_time = current_time
                        logger.info(f"Firebase Updated: {final_status}")
                    except Exception as e:
                        logger.error(f"Firebase Upload Error: {e}")

                # --- NEW: SAMPLING DELAY ---
                # Wait 3 seconds before processing the next frame.
                # This keeps the CPU cool and prevents "flickering" results.
                time.sleep(3.0)
                
            except Exception as e:
                logger.error(f"AI Loop Error: {e}")
                time.sleep(1)



# Initialize AI
global_ai = GlobalInference()


# ==========================================
# 3. GLOBAL AUDIO
# ==========================================
class GlobalMicrophone:
    def __init__(self):
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
            format=pyaudio.paInt16, channels=1, rate=48000, input=True,
            frames_per_buffer=960, input_device_index=0 
        )
        self.running = True
        self.active_queues = set() 
        self.thread = threading.Thread(target=self._record_loop, daemon=True)
        self.thread.start()

    def _record_loop(self):
        while self.running:
            try:
                data = self.stream.read(960, exception_on_overflow=False)
                for q in list(self.active_queues):
                    if q.full():
                        try: q.get_nowait()
                        except: pass
                    try: q.put_nowait(data)
                    except: pass
            except: pass

    def add_queue(self, q): self.active_queues.add(q)
    def remove_queue(self, q): self.active_queues.discard(q)

global_mic = GlobalMicrophone()

# ==========================================
# X. GLOBAL BIOACOUSTIC INFERENCE (ADDED)
# ==========================================

# ===== THE MAGMA LOOK-UP TABLE (Optimized for Pi 5) =====
def get_magma_lut():
    # A sampling of the magma colormap (Dark Purple -> Orange -> White)
    magma_data = np.array([
        [0, 0, 4], [21, 13, 52], [61, 14, 115], [97, 24, 126], 
        [132, 37, 117], [168, 51, 98], [202, 70, 75], [229, 97, 51], 
        [247, 132, 23], [253, 172, 16], [246, 213, 64], [252, 255, 164]
    ], dtype=np.uint8)
    # Interpolate to 256 colors
    x = np.linspace(0, 255, len(magma_data))
    lut = np.zeros((256, 3), dtype=np.uint8)
    for i in range(3):
        lut[:, i] = np.interp(np.arange(256), x, magma_data[:, i])
    return lut

_MAGMA_LUT = get_magma_lut()

class GlobalBioacoustic:
    def __init__(self, model_path="/home/raprap/bioacoustic/mobilenet_v3.tflite"):
        self.model_path = model_path
        # Updated to 4 classes
        self.labels_full = ["cold", "hot", "normal", "rejection"] 
        self.latest_prediction = "Initializing..."
        self.running = True
        self.prediction_buffer = deque(maxlen=20)
        
        # Audio Settings
        self.RATE = 22050  # MATCH TRAINING
        self.SLICE_SEC = 3
        self.CHUNK_SIZE = self.RATE * self.SLICE_SEC
        
        self.audio_queue = queue.Queue(maxsize=100)
        global_mic.add_queue(self.audio_queue)

        try:
            self.interpreter = tflite.Interpreter(model_path=self.model_path)
            self.interpreter.allocate_tensors()
            self.input_details = self.interpreter.get_input_details()
            self.output_details = self.interpreter.get_output_details()
            
            self.thread = threading.Thread(target=self._audio_loop, daemon=True)
            self.thread.start()
        except Exception as e:
            logger.error(f"BIOACOUSTIC INIT ERROR: {e}")

    def _apply_magma(self, norm_s):
        # norm_s is 0.0 to 1.0, convert to 0-255
        idx = (norm_s * 255).astype(np.uint8)
        return _MAGMA_LUT[idx]

    def _audio_loop(self):
        buffer = np.zeros(self.CHUNK_SIZE, dtype=np.float32)

        while self.running:
            try:
                filled = 0
                
                while filled < self.CHUNK_SIZE: 
                    try:
                        raw = self.audio_queue.get(timeout=2)
                        raw_np = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
                        num_samples = int(len(raw_np) * self.RATE / 48000)
                        audio_resampled = signal.resample(raw_np, num_samples)
                        
                        # Roll and update: This is where the magic happens
                        buffer = np.roll(buffer, -len(audio_resampled))
                        buffer[-len(audio_resampled):] = audio_resampled
                        filled += len(audio_resampled)
                    except:
                        break
                
                # 1. Threshold-Based Peak Normalization (Signal Gating)
                peak = np.max(np.abs(buffer))
                if peak < 0.005: 
                    raw_label = "rejection" # Force rejection immediately
                elif peak > 0.02:
                    processed_audio = (buffer / peak) * 0.891
                else:
                    processed_audio = buffer

                # 2. Fast STFT
                f, t, Zxx = signal.stft(processed_audio, fs=self.RATE, nperseg=1024, noverlap=768)
                S_mag = np.abs(Zxx)

                # 3. Frequency Filtering & Log Scaling
                freq_mask = (f >= 2000) & (f <= 10000)
                S_filt = S_mag[freq_mask, :]
                S_db = 20 * np.log10(np.maximum(S_filt, 1e-4))

                # 4. Static Normalization (0.0 to 1.0)
                S_norm = np.clip((S_db + 80) / 80, 0, 1)

                # 5. Spectrogram Generation
                rgb_spec = self._apply_magma(S_norm)
                img = cv2.resize(rgb_spec, (224, 224), interpolation=cv2.INTER_LINEAR)

                # 6. Inference
                input_tensor = np.expand_dims(img.astype(np.uint8), axis=0)
                self.interpreter.set_tensor(self.input_details[0]['index'], input_tensor)
                self.interpreter.invoke()

                # 7. Raw Classification
                output_data = self.interpreter.get_tensor(self.output_details[0]['index'])[0]
                pred_idx = np.argmax(output_data)
                raw_label = self.labels_full[pred_idx]

                # --- SMOOTHING & VOTING LOGIC ---
                self.prediction_buffer.append(raw_label)

                if len(self.prediction_buffer) < 10:
                    self.latest_prediction = "initializing..."
                    continue

                # Calculate percentages
                vote_counts = Counter(self.prediction_buffer)
                buffer_len = len(self.prediction_buffer)

                rejection_percent = vote_counts.get("rejection", 0) / buffer_len
                cold_percent = vote_counts.get("cold", 0) / buffer_len
                hot_percent = vote_counts.get("hot", 0) / buffer_len

                # THE DECISION HIERARCHY
                if rejection_percent >= 0.30:
                    final_status = "rejection"
                elif cold_percent >= 0.60:
                    final_status = "cold"
                elif hot_percent >= 0.60:
                    final_status = "hot"
                else:
                    final_status = "normal"

                self.latest_prediction = final_status

            except Exception as e:
                logger.error(f"AUDIO LOOP ERROR: {e}")
                time.sleep(0.1)

# Initialize global audio model
global_bio = GlobalBioacoustic()

def _bio_firebase_loop():
    last_sent = ""
    while True:
        if firebase_ref:
            try:
                # 1. Get the current prediction (Cold, Hot, Normal, or Rejection)
                result = global_bio.latest_prediction.lower()

                # 2. Filter out ONLY the system initialization state
                if result != last_sent and result != "initializing...":
                    # 3. Send the raw label. Your App handles the mapping logic.
                    db.reference("aiResult/bioacoustic").set(result)
                    last_sent = result
                    logger.info(f"Bioacoustic Firebase Updated: {result}")

            except Exception as e:
                logger.error(f"BIOACOUSTIC FIREBASE ERROR: {e}")
        
        # Sync rate: 2 seconds is perfect for Realtime Database
        time.sleep(2)

threading.Thread(target=_bio_firebase_loop, daemon=True).start()

# def _bio_firebase_loop():
#     last_sent = ""
#     while True:
#         if firebase_ref:
#             try:
#                 result = global_bio.latest_prediction

#                 # 1. Update the filter list to match your new "Initializing..." string
#                 # 2. Decide if "Rejection" should be sent (included below)
#                 if result and result != last_sent and result not in [
#                     "Initializing...",        # Matches your new __init__ string
#                     "Bioacoustic Model Error"
#                 ]:
#                     # Send to Firebase (will now include 'rejection')
#                     db.reference("aiResult/bioacoustic").set(result.lower())
#                     last_sent = result
#                     logger.info(f"Bioacoustic Firebase Updated: {result}")

#             except Exception as e:
#                 logger.error(f"BIOACOUSTIC FIREBASE ERROR: {e}")

#         time.sleep(2)

# ==========================================
# 4. TRACK CLASSES (Transparent & Dynamic Box)
# ==========================================
class MyCameraTrack(VideoStreamTrack):
    async def recv(self):
        pts, time_base = await self.next_timestamp()
        
        # 1. Get Frame
        frame = global_picam.capture_array()
        
        # 2. Convert to BGR for OpenCV Drawing
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        # === THE FIX: MANUAL CHANNEL SWAP ===
        # We are sending BGR data, but we label it as "rgb24".
        # This forces the Blue channel to be displayed as Red, fixing the color.
        video_frame = VideoFrame.from_ndarray(frame_bgr, format="rgb24")
        
        video_frame.pts = pts
        video_frame.time_base = time_base
        return video_frame

class MyMicrophoneTrack(AudioStreamTrack):
    def __init__(self):
        super().__init__()
        self.queue = asyncio.Queue(maxsize=10)
        self._timestamp = 0
        self.RATE = 48000
        global_mic.add_queue(self.queue)
        
        # 1. Use a lower order (4) for even better stability in real-time
        self.sos = signal.butter(4, 2000, 'hp', fs=self.RATE, output='sos')
        
        # 2. INITIALIZE FILTER MEMORY (The "zi" state)
        # This prevents the "clicking" static between audio chunks
        self.zi = signal.sosfilt_zi(self.sos)

    async def recv(self):
        data = await self.queue.get()
        
        # 3. Convert to float32 safely
        raw_audio = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32768.0
        
        # 4. APPLY FILTER WITH STATE (The Fix)
        # We pass self.zi in and get the new self.zi out
        filtered_float, self.zi = signal.sosfilt(self.sos, raw_audio, zi=self.zi)
        
        # 5. Safe clipping and conversion
        final_audio = np.clip(filtered_float * 32767.0, -32768, 32767).astype(np.int16)
        
        # 6. Build the frame
        audio_frame = AudioFrame(format="s16", layout="mono", samples=960)
        audio_frame.planes[0].update(final_audio.reshape(1, -1))
        
        self._timestamp += 960
        audio_frame.pts = self._timestamp
        audio_frame.sample_rate = self.RATE
        audio_frame.time_base = fractions.Fraction(1, self.RATE)
        
        return audio_frame

    def stop(self):
        super().stop()
        global_mic.remove_queue(self.queue)

# ==========================================
# 5. SIGNALING
# ==========================================
pcs = set()

async def run_signaling(websocket):
    await websocket.send(json.dumps({"type": "camera_join"}))
    try:
        async for message in websocket:
            data = json.loads(message)
            if data["type"] == "offer":
                pc = RTCPeerConnection(configuration=RTCConfiguration(iceServers=[]))
                pcs.add(pc)
                pc.addTrack(MyCameraTrack())
                pc.addTrack(MyMicrophoneTrack())

                @pc.on("connectionstatechange")
                async def on_connectionstatechange():
                    if pc.connectionState in ["failed", "closed"]:
                        await pc.close()
                        pcs.discard(pc)

                await pc.setRemoteDescription(RTCSessionDescription(sdp=data["sdp"], type=data["type"]))
                answer = await pc.createAnswer()
                await pc.setLocalDescription(answer)
                await asyncio.sleep(2) 
                await websocket.send(json.dumps({"type": "answer", "sdp": pc.localDescription.sdp}))

            elif data["type"] == "candidate":
                candidate_info = data["candidate"]
                if candidate_info and "candidate" in candidate_info:
                    candidate = candidate_from_sdp(candidate_info["candidate"])
                    candidate.sdpMid = candidate_info.get("sdpMid")
                    candidate.sdpMLineIndex = candidate_info.get("sdpMLineIndex")
                    for active_pc in pcs:
                        try: await active_pc.addIceCandidate(candidate)
                        except: pass 
    except: pass
    finally:
        for pc in pcs: await pc.close()
        pcs.clear()

async def main():
    # Replace with your Signaling Server IP
    uri = "ws://100.68.113.75:8765"
    logger.info(f"Connecting to {uri}")
    while True:
        try:
            async with websockets.connect(uri) as websocket:
                await run_signaling(websocket)
        except:
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())