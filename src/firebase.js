import { initializeApp } from "firebase/app";
import { getDatabase } from "firebase/database";
import 'dotenv/config';

const firebaseConfig = {
  apiKey: process.env.API_KEY,
  authDomain: "chickmate-ef0a0.firebaseapp.com",
  databaseURL: "https://chickmate-ef0a0-default-rtdb.asia-southeast1.firebasedatabase.app",
  projectId: "chickmate-ef0a0",
  storageBucket: "chickmate-ef0a0.firebasestorage.app",
  messagingSenderId: "625455130422",
  appId: "1:625455130422:web:5c5ca912a717c553b4f597"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);

export const db = getDatabase(app);