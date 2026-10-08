// Firebase SDK Initialization
// Config loaded from environment variables (VITE_FIREBASE_* in .env) with verified fallbacks
import { initializeApp, getApps } from "firebase/app";
import { getAuth, GoogleAuthProvider } from "firebase/auth";

const apiKey =
  import.meta.env.VITE_FIREBASE_API_KEY ||
  "AIzaSyAa6l_4MKRpAZnVQVB3vo3FeUdI8IS45cs";

let app = null;
let auth = null;
let googleProvider = null;

try {
  if (apiKey && apiKey.trim().length > 0 && apiKey !== "undefined") {
    const firebaseConfig = {
      apiKey: apiKey.trim(),
      authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN || "admissions-helpdesk.firebaseapp.com",
      projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID || "admissions-helpdesk",
      storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET || "admissions-helpdesk.firebasestorage.app",
      messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID || "914272299162",
      appId: import.meta.env.VITE_FIREBASE_APP_ID || "1:914272299162:web:3752d9cd16afbd6a9c1723",
    };

    app = getApps().length === 0 ? initializeApp(firebaseConfig) : getApps()[0];
    auth = getAuth(app);
    googleProvider = new GoogleAuthProvider();
    googleProvider.setCustomParameters({ prompt: "select_account" });
  } else {
    console.info("[Auth] Running in local guest/candidate mode (Firebase API key not set).");
  }
} catch (error) {
  console.warn("[Auth] Firebase initialization error (falling back to local mode):", error);
}

export { auth, googleProvider };
export default app;

