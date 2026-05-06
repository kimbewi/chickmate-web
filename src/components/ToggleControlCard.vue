<!-- src/components/ToggleControlCard.vue -->
<template>
  <div class="control-card" :class="{ 'is-on': isOn }">
    <div class="card-header">
      <div class="icon-box" :class="isOn ? 'icon-on' : 'icon-off'">
        <slot name="icon"></slot>
      </div>
      <label class="switch">
        <input type="checkbox" :checked="isOn" @change="$emit('toggle', $event.target.checked)">
        <span class="slider round"></span>
      </label>
    </div>
    <div class="card-text">
      <h3 :class="{ 'text-white': isOn }">{{ title }}</h3>
      <span :class="isOn ? 'status-text-on' : 'status-text-off'">
        {{ isOn ? 'On' : 'Off' }}
      </span>
    </div>
  </div>
</template>

<script setup>
defineProps({ title: String, isOn: Boolean });
defineEmits(['toggle']);
</script>

<style scoped>
.control-card {
  background-color: #FFFFFF;
  border-radius: 16px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
  transition: background-color 0.3s ease;
  height: 120px;
}
.control-card.is-on { background-color: #F9A825; }
.card-header { display: flex; justify-content: space-between; align-items: flex-start; }
.icon-box { padding: 8px; border-radius: 8px; display: flex; align-items: center; justify-content: center; }
.icon-off { background-color: rgba(249, 168, 37, 0.15); color: #F9A825; }
.icon-on { background-color: rgba(255, 255, 255, 0.2); color: #FFFFFF; }
.card-text h3 { font-size: 16px; font-weight: 700; color: #1e1e1e; margin: 0 0 4px 0; transition: color 0.3s ease; }
.card-text h3.text-white { color: #FFFFFF; }
.status-text-off { color: #888888; font-size: 14px; font-weight: 500; }
.status-text-on { color: rgba(255, 255, 255, 0.7); font-size: 14px; font-weight: 500; }
.switch { position: relative; display: inline-block; width: 40px; height: 24px; }
.switch input { opacity: 0; width: 0; height: 0; }
.slider { position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0; background-color: #ccc; transition: .4s; border-radius: 34px; }
.slider:before { position: absolute; content: ""; height: 16px; width: 16px; left: 4px; bottom: 4px; background-color: white; transition: .4s; border-radius: 50%; }
input:checked + .slider { background-color: rgba(255, 255, 255, 0.5); }
input:checked + .slider:before { transform: translateX(16px); }
</style>