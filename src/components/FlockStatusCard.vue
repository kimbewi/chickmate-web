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
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.4) 0%, rgba(255, 255, 255, 0.1) 100%);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid rgba(255, 255, 255, 0.5);
  box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.07);  border-radius: 8px;
  padding: 12px; 
  gap: 12px; 
  margin: 0;
  height: 100%; 
  box-sizing: border-box;
  min-width: 0; 
}

/* --- Cream Icon Box --- */
.image-box { 
  width: 40px; 
  height: 40px; 
  background: linear-gradient(135deg, rgba(252, 246, 232, 0.6) 0%, rgba(252, 246, 232, 0.15) 100%);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.6);
  box-shadow: inset 0 1px 4px rgba(255, 255, 255, 0.4), 0 2px 4px rgba(0, 0, 0, 0.02);  border-radius: 6px; 
  padding: 6px; 
  flex-shrink: 0; 
}

.image-box img { 
  width: 100%; 
  height: 100%; 
  object-fit: contain; 
}

.fallback-icon { 
  font-size: 20px; 
}

/* --- Typography --- */
.text-content { 
  display: flex; 
  flex-direction: column; 
  justify-content: center; 
  gap: 2px;
  min-width: 0; 
  flex-grow: 1; 
}

.card-title { 
  font-size: 12px; color: #86868B; margin-bottom: 2px; font-weight: 600; }

.card-status { font-size: 16px; font-weight: 900; letter-spacing: -0.2px; line-height: 1.1;  }

.card-description { 
  font-size: 8px; 
  color: #98989D; 
  white-space: normal; 
  line-height: 1.2;
  display: -webkit-box;
  -webkit-line-clamp: 2; 
  -webkit-box-orient: vertical;
  overflow: hidden;
  margin: 0;
}

/* --- Dynamic Status Colors --- */
.text-blue { color: #2B82D9; }  .text-green { color: #20C955; } .text-red { color: #F44336; } .text-gray { color: #AAAAAA; }

</style>