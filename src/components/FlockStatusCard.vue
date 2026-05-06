<template>
  <div class="flock-card">
    
    <div class="image-box">
      <img v-if="iconAsset" :src="iconAsset" alt="AI Icon" />
      <span v-else class="fallback-icon">🐔</span>
    </div>

    <div class="text-content">
      <span class="card-title">{{ title }}</span>
      <!-- We now use the exact mapped label and color class -->
      <span class="card-status" :class="colorClass">{{ label }}</span>
      <span class="card-description" :title="description">{{ description }}</span>
    </div>

  </div>
</template>

<script setup>
defineProps({
  title: String,
  label: String,
  description: String,
  colorClass: String,
  iconAsset: String
});
</script>

<style scoped>
.flock-card {
  display: flex;
  align-items: center;
  background-color: #FFFFFF;
  border-radius: 8px;
  padding: 12px;
  gap: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06); /* Very soft shadow */
  margin-bottom: 12px;
}

/* --- Cream Icon Box --- */
.image-box {
  width: 72px;
  height: 72px;
  background-color: #FCF6E8; 
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  padding: 8px;
}

.image-box img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.fallback-icon {
  font-size: 32px;
}

/* --- Typography --- */
.text-content {
  display: flex;
  flex-direction: column;
  justify-content: center;
  overflow: hidden; /* Keeps long descriptions from breaking the card */
  flex-grow: 1;
}

.card-title {
  font-size: 13px;
  color: #333333;
  margin-bottom: 2px;
  font-weight: 500;
}

.card-status {
  font-size: 24px;
  font-weight: 900;
  letter-spacing: 0.5px;
  text-transform: uppercase;
  line-height: 1.1;
  margin-bottom: 2px;
}

.card-description {
  font-size: 12px;
  color: #999999;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis; /* Adds '...' if the text is too long */
}

/* --- Dynamic Status Colors --- */
.text-blue { color: #2B82D9; }  
.text-green { color: #20C955; } 
.text-red { color: #F44336; }
.text-gray { color: #AAAAAA; }
</style>