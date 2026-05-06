<!-- src/components/LeftPanel.vue -->
<template>
  <section class="left-panel">
    
    <div class="video-section">
      <!-- Your VideoFeed component will go here! -->
      <VideoFeed />
    </div>
    
    <div style="margin-top: 8px;">
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
  gap: 24px;
}

.video-section {
  background-color: #000000;
  border-radius: 16px;
  min-height: 450px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: bold;
  overflow: hidden;
}
</style>