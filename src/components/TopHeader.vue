<template>
  <header class="top-nav">
    <div class="logo-area">
      <img src="../assets/appLogo.png" alt="Logo" class="logo-img" />
      <h1 class="brand-name">ChickMate</h1>
    </div>
    
    <div class="header-icons">
      <!-- <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12.55a11 11 0 0 1 14.08 0"></path><path d="M1.42 9a16 16 0 0 1 21.16 0"></path><path d="M8.53 16.11a6 6 0 0 1 6.95 0"></path><line x1="12" y1="20" x2="12.01" y2="20"></line></svg> -->

      <svg @click="isHistoryModalOpen = true" class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>

      <div class="notification-wrapper" @click="handleNotificationClick">
        <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path><path d="M13.73 21a2 2 0 0 1-3.46 0"></path></svg>
        <div v-if="unreadCount > 0" class="notification-badge">{{ unreadCount > 99 ? '99+' : unreadCount }}</div>
      </div>
    </div>

    <NotificationsModal :isOpen="isNotificationModalOpen" @close="isNotificationModalOpen = false" />
    <HistoryModal :isOpen="isHistoryModalOpen" @close="isHistoryModalOpen = false" />
    
  </header>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import NotificationsModal from './NotificationsModal.vue';
import HistoryModal from './HistoryModal.vue'; // <-- Import the new modal

// Modal States
const isNotificationModalOpen = ref(false);
const isHistoryModalOpen = ref(false); // <-- Add state for history modal

// Notification Logic
const unreadCount = ref(0);
let pollingTimer = null;
const API_BASE_URL = 'http://100.68.113.75:5000/api'; 

const fetchUnreadCount = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/notifications/unread-count`);
    if (response.ok) {
      const data = await response.json();
      unreadCount.value = data.unreadCount || 0;
    }
  } catch (error) {
    console.error("Failed to fetch unread notifications.");
  }
};

const handleNotificationClick = async () => {
  try {
    await fetch(`${API_BASE_URL}/notifications/mark-all-read`, { method: 'PUT' });
    unreadCount.value = 0; 
  } catch (error) {
    console.error("Failed to mark notifications as read:", error);
  }
  isNotificationModalOpen.value = true;
};

onMounted(() => {
  fetchUnreadCount();
  pollingTimer = setInterval(fetchUnreadCount, 5000);
});

onUnmounted(() => {
  if (pollingTimer) clearInterval(pollingTimer);
});
</script>

<style scoped>
.top-nav {
  height: 50px; 
  padding: 0 24px;
  display: flex; 
  justify-content: space-between; 
  align-items: center; 
  border-bottom: 1px solid #EAEAEA; 
  background-color: #FFFFFF;
  width: 100%; 
  box-sizing: border-box;
}

.logo-area { display: flex; align-items: center; gap: 8px; }

.logo-img { height: 28px; border-radius: 6px; }

.brand-name { margin: 0; font-size: 20px; font-weight: 900; color: #202020; letter-spacing: -0.5px; }

.header-icons { 
  display: flex; 
  flex-direction: row; 
  align-items: center; 
  gap: 16px; 
}

.nav-icon { width: 20px; height: 20px; color: #333333; cursor: pointer; }

.nav-icon:hover { color: #000000; }

.notification-wrapper { position: relative; display: flex; align-items: center; cursor: pointer; }

.notification-badge { position: absolute; top: -6px; right: -8px; background-color: #F44336; color: #FFFFFF; font-size: 9px; font-weight: 900; padding: 2px 4px; border-radius: 10px; min-width: 14px; text-align: center; }

</style>