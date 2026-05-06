<!-- src/components/RightPanel.vue -->
<template>
  <section class="right-panel">
    <div class="ai-cards-container">
      
      <!-- Behavior Prediction Card -->
      <FlockStatusCard 
        title="Flock Behavior" 
        :label="currentBehaviorData.label" 
        :description="currentBehaviorData.description"
        :colorClass="currentBehaviorData.color"
        iconAsset="/assets/flockBehaviorIcon.png" 
      />

      <!-- Sound Analysis Card -->
      <FlockStatusCard 
        title="Flock Sounds" 
        :label="currentSoundData.label" 
        :description="currentSoundData.description"
        :colorClass="currentSoundData.color"
        iconAsset="/assets/flockSoundsIcon.png" 
      />

    </div>

    <div class="env-section">
      <div class="wireframe-box">Env 1</div>
      <div class="wireframe-box">Env 2</div>
      <div class="wireframe-box">Env 3</div>
      <div class="wireframe-box">Env 4</div>
    </div>
  </section>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import FlockStatusCard from './FlockStatusCard.vue';
import { getDatabase, ref as firebaseRef, onValue } from "firebase/database";

const rawBehaviorState = ref('LOADING'); 
const rawSoundState = ref('LOADING');

// MAPPING DICTIONARIES
const behaviorMap = {
  'HOT': { label: 'DISPERSED', description: 'Chicks are spread out or lethargic; possible heat stress.', color: 'text-red' },
  'NORMAL': { label: 'EVENLY DISTRIBUTED', description: 'Chicks are active and evenly distributed; possible optimal condition.', color: 'text-green' },
  'COLD': { label: 'HUDDLING', description: 'Chicks are grouped closely together; possible cold stress.', color: 'text-blue' },
  'LOADING': { label: 'CONNECTING...', description: 'Waiting for camera feed...', color: 'text-gray' },
  '--': { label: 'UNKNOWN', description: 'No data available.', color: 'text-gray' }
};

const soundMap = {
  'HOT': { label: 'IRREGULAR', description: 'Reduced and inconsistent chirping; possible heat stress.', color: 'text-red' },
  'NORMAL': { label: 'MODERATE', description: 'Steady and calm chirping; possible optimal condition.', color: 'text-green' },
  'COLD': { label: 'HIGH-INTENSITY', description: 'Repetitive and high-pitched chirping; possible cold stress.', color: 'text-blue' },
  'REJECTION': { label: 'UNDETECTED', description: 'No clear chick vocalization detected.', color: 'text-gray' },
  'LOADING': { label: 'CONNECTING...', description: 'Waiting for microphone feed...', color: 'text-gray' },
  '--': { label: 'UNKNOWN', description: 'No data available.', color: 'text-gray' }
};

const currentBehaviorData = computed(() => behaviorMap[rawBehaviorState.value] || behaviorMap['--']);
const currentSoundData = computed(() => soundMap[rawSoundState.value] || soundMap['--']);

onMounted(() => {
  const db = getDatabase();
    const aiResultRef = firebaseRef(db, 'aiResult'); 

  onValue(aiResultRef, (snapshot) => {
    if (snapshot.exists()) {
      const data = snapshot.val();
      
      rawBehaviorState.value = data.cv ? data.cv.toString().toUpperCase() : '--';
      rawSoundState.value = data.bioacoustic ? data.bioacoustic.toString().toUpperCase() : '--';
      
      console.log("Firebase AI Update:", rawBehaviorState.value, rawSoundState.value);
    } else {
      rawBehaviorState.value = '--';
      rawSoundState.value = '--';
    }
  });
});
</script>

<style scoped>
.right-panel {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.ai-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.env-section {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.wireframe-box {
  background-color: #FFFFFF;
  border: 1px dashed #CCCCCC;
  border-radius: 12px;
  padding: 24px;
  text-align: center;
  color: #888888;
}
</style>