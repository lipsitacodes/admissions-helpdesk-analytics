// Firebase SDK Initialization
// These are public client-side keys (safe for frontend use).
import { initializeApp } from "firebase/app";
import { getAuth, GoogleAuthProvider } from "firebase/auth";

const firebaseConfig = {
  apiKey: "AIzaSyAa6l_4MKRpAZnVQVB3vo3FeUdI8IS45cs",
  authDomain: "admissions-helpdesk.firebaseapp.com",
  projectId: "admissions-helpdesk",
  storageBucket: "admissions-helpdesk.firebasestorage.app",
  messagingSenderId: "914272299162",
  appId: "1:914272299162:web:3752d9cd16afbd6a9c1723",
};

const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
export const googleProvider = new GoogleAuthProvider();
export default app;
