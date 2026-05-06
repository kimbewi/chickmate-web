<!-- src/components/RightPanel.vue -->
<template>
  <section class="right-panel">
    <div class="ai-section">
      <div class="wireframe-box">Flock Behavior</div>
      <div class="wireframe-box">Flock Sounds</div>
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
// We will import your FlockStatusCard and StatusCard here later!
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