<!-- src/components/LeftPanel.vue -->
<template>
  <section class="left-panel">
    <div class="video-section">
      <!-- Your VideoFeed component will go here! -->
      <VideoFeed />
    </div>
    
    <div class="controls-section">
      <div class="wireframe-box">Control 1</div>
      <div class="wireframe-box">Control 2</div>
      <div class="wireframe-box">Control 3</div>
    </div>
  </section>
</template>

<script setup>
import VideoFeed from './VideoFeed.vue';
</script>

<style scoped>
.left-panel {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.video-section {
  background-color: #333333;
  border-radius: 16px;
  min-height: 450px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: bold;
}

.controls-section {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
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