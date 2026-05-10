<template>
  <section class="left-panel">
    
    <div class="video-section">
      <VideoFeed />
    </div>
    
    <div class="actuator-wrapper">
      <ActuatorControls />
    </div>

  </section>
</template>

<script setup>
import VideoFeed from './VideoFeed.vue';
import ActuatorControls from './ActuatorControls.vue';
</script>

<style scoped>
.left-panel {
  display: flex;
  flex-direction: column;
  gap: 12px;
  height: 100%; 
  min-height: 0; 
}

.video-section {
  background-color: #000000;
  border-radius: 16px;
  flex: 1; 
  min-height: 250px; 
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: bold;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0,0,0,0.1);
}

.actuator-wrapper {
  display: flex;
  flex-direction: column;
}
</style>