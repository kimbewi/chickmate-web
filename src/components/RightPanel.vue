<template>
  <section class="right-panel">
    
    <h2 class="section-header">AI Predictions</h2>
    <div class="ai-cards-container">
      <FlockStatusCard 
        title="Flock Behavior" 
        :label="currentBehaviorData.label" 
        :description="currentBehaviorData.description"
        :colorClass="currentBehaviorData.color"
        iconAsset="/assets/flockBehaviorIcon.png" 
      />
      <FlockStatusCard 
        title="Flock Sounds" 
        :label="currentSoundData.label" 
        :description="currentSoundData.description"
        :colorClass="currentSoundData.color"
        iconAsset="/assets/flockSoundsIcon.png" 
      />
    </div>

    <h2 class="section-header env-header">Environmental Status</h2>
    <div class="env-section">
      <StatusCard title="Ammonia Level" :data="ammoniaLevel" unit="ppm" iconColor="#4CAF50" :selectedWeek="selectedWeek" />
      <StatusCard title="Temperature" :data="temperature" unit="°C" iconColor="#F44336" :selectedWeek="selectedWeek" />
      <StatusCard title="Humidity" :data="humidity" unit="%" iconColor="#2196F3" :selectedWeek="selectedWeek" />
      <StatusCard title="Light Level" :data="lightLevel" unit="lux" iconColor="#FFEB3B" :selectedWeek="selectedWeek" />
    </div>
    
  </section>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { getDatabase, ref as firebaseRef, onValue } from "firebase/database";
import FlockStatusCard from './FlockStatusCard.vue';
import StatusCard from './StatusCard.vue';

const rawBehaviorState = ref('LOADING'); 
const rawSoundState = ref('LOADING');

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

// ENVIRONMENTAL STATUS LOGIC
const ammoniaLevel = ref('--');
const temperature = ref('--');
const humidity = ref('--');
const lightLevel = ref('--');
const selectedWeek = ref(1);

onMounted(() => {
  const db = getDatabase();
  const aiResultRef = firebaseRef(db, 'aiResult'); 

  onValue(aiResultRef, (snapshot) => {
    if (snapshot.exists()) {
      const data = snapshot.val();
      rawBehaviorState.value = data.cv ? data.cv.toString().toUpperCase() : '--';
      rawSoundState.value = data.bioacoustic ? data.bioacoustic.toString().toUpperCase() : '--';
    } else {
      rawBehaviorState.value = '--';
      rawSoundState.value = '--';
    }
  });

  const sensorRef = firebaseRef(db, 'sensorData');
  onValue(sensorRef, (snapshot) => {
    if (snapshot.exists()) {
      const data = snapshot.val();
      ammoniaLevel.value = data.ammonia !== undefined ? Number(data.ammonia).toFixed(3) : '--';
      lightLevel.value = data.lightLevel !== undefined ? Number(data.lightLevel).toFixed(3) : '--';
      temperature.value = data.temperature !== undefined ? data.temperature.toString() : '--';
      humidity.value = data.humidity !== undefined ? data.humidity.toString() : '--';
    }
  });

  const chickRef = firebaseRef(db, 'chickInfo');
  onValue(chickRef, (snapshot) => {
    if (snapshot.exists() && snapshot.val().ageWeeks) {
      selectedWeek.value = snapshot.val().ageWeeks;
    }
  });
});
</script>

<style scoped>
.right-panel {
  display: flex;
  flex-direction: column;
  gap: 4px; 
  height: 100%;
  min-height: 0;
  overflow: hidden;
}

.section-header {
  font-size: 12px;
  font-weight: 700;
  color: #888888;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin: 0;
}

.env-header {
  margin-top: 10px; 
}

.ai-cards-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px; 
  flex: 0.25;
  min-height: 0;
}

.env-section {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px; 
  flex: 0.75; 
  min-height: 0;
}
</style>