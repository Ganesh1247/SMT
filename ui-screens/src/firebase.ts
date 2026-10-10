import { initializeApp, getApps, getApp } from "firebase/app";
import {
  getAuth,
  GoogleAuthProvider,
  signInWithPopup,
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword,
  sendPasswordResetEmail,
  sendEmailVerification,
  signOut,
  onAuthStateChanged,
  User
} from "firebase/auth";
import {
  getFirestore,
  doc,
  getDoc,
  setDoc,
  updateDoc,
  collection,
  onSnapshot
} from "firebase/firestore";

// Web app's Firebase configuration provided by user
export const firebaseConfig = {
  apiKey: "AIzaSyDV4KG7lFDJFQamt4q0VhnO6ooUvK_xou4",
  authDomain: "smta-f918c.firebaseapp.com",
  projectId: "smta-f918c",
  storageBucket: "smta-f918c.firebasestorage.app",
  messagingSenderId: "835347685975",
  appId: "1:835347685975:web:6107cecec1322ce30fb912"
};

// Initialize Firebase safely
export const app = getApps().length > 0 ? getApp() : initializeApp(firebaseConfig);
export const auth = getAuth(app);
export const db = getFirestore(app);

const googleProvider = new GoogleAuthProvider();

// --- AUTHENTICATION HELPERS ---

export async function loginWithGoogle() {
  try {
    const result = await signInWithPopup(auth, googleProvider);
    const user = result.user;
    await syncUserRecord(user);
    return { success: true, user };
  } catch (error: any) {
    console.error("Google Sign-In Error:", error);
    return { success: false, error: error.message };
  }
}

export async function signUpWithEmail(email: string, pass: string, name: string) {
  try {
    const result = await createUserWithEmailAndPassword(auth, email, pass);
    const user = result.user;
    await syncUserRecord(user, name);
    // Mail Automation: Automatically dispatch email verification
    try {
      await sendEmailVerification(user);
    } catch (mailErr) {
      console.warn("Automated email verification dispatch error:", mailErr);
    }
    return { success: true, user };
  } catch (error: any) {
    console.error("Sign-Up Error:", error);
    return { success: false, error: error.message };
  }
}

export async function sendUserVerificationEmail(user?: User) {
  try {
    const targetUser = user || auth.currentUser;
    if (targetUser) {
      await sendEmailVerification(targetUser);
      return { success: true };
    }
    return { success: false, error: "No authenticated user found" };
  } catch (error: any) {
    console.error("Verification Email Error:", error);
    return { success: false, error: error.message };
  }
}

export async function loginWithEmail(email: string, pass: string) {
  try {
    const result = await signInWithEmailAndPassword(auth, email, pass);
    return { success: true, user: result.user };
  } catch (error: any) {
    console.error("Login Error:", error);
    return { success: false, error: error.message };
  }
}

export async function sendPasswordReset(email: string) {
  try {
    await sendPasswordResetEmail(auth, email);
    return { success: true };
  } catch (error: any) {
    console.error("Password Reset Error:", error);
    return { success: false, error: error.message };
  }
}

export async function logoutUser() {
  try {
    await signOut(auth);
    return { success: true };
  } catch (error: any) {
    return { success: false, error: error.message };
  }
}

export function subscribeToAuth(callback: (user: User | null) => void) {
  return onAuthStateChanged(auth, callback);
}

// --- FIRESTORE USER PROFILE & STATE SYNC ---

export async function syncUserRecord(user: User, customName?: string) {
  try {
    const userRef = doc(db, "users", user.uid);
    const snap = await getDoc(userRef);
    if (!snap.exists()) {
      await setDoc(userRef, {
        uid: user.uid,
        email: user.email,
        name: customName || user.displayName || user.email?.split("@")[0] || "Learner Fellow",
        role: "Workforce Fellow",
        avatarUrl: user.photoURL || "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=100&h=100&fit=crop&crop=faces",
        track: "Associate to Senior PM Track",
        cohort: "Cohort #14 • Week 6",
        currentMilestone: "Product Strategy & Discovery",
        milestoneProgress: 68,
        streakDays: 5,
        streakBest: 12,
        xpBonus: 150,
        q1Target: 84,
        createdAt: new Date().toISOString()
      });
    }
  } catch (err) {
    console.warn("Firestore syncUserRecord error:", err);
  }
}

export async function saveRsvpStatus(eventId: string, rsvpState: boolean, userId: string = "demo-user") {
  try {
    const rsvpRef = doc(db, "cohort_rsvps", `${eventId}_${userId}`);
    await setDoc(rsvpRef, {
      eventId,
      userId,
      isRsvped: rsvpState,
      timestamp: new Date().toISOString()
    }, { merge: true });
    return { success: true };
  } catch (err) {
    console.warn("Firestore saveRsvpStatus error:", err);
    return { success: false, error: err };
  }
}

export async function toggleCourseBookmark(courseId: string, isBookmarked: boolean, userId: string = "demo-user") {
  try {
    const bookmarkRef = doc(db, "bookmarks", `${courseId}_${userId}`);
    await setDoc(bookmarkRef, {
      courseId,
      userId,
      isBookmarked,
      updatedAt: new Date().toISOString()
    }, { merge: true });
    return { success: true };
  } catch (err) {
    console.warn("Firestore toggleCourseBookmark error:", err);
    return { success: false, error: err };
  }
}

export async function enrollInCourse(courseId: string, courseTitle: string, userId: string = "demo-user") {
  try {
    const enrollRef = doc(db, "enrollments", `${courseId}_${userId}`);
    await setDoc(enrollRef, {
      courseId,
      courseTitle,
      userId,
      status: "in_progress",
      progress: 0,
      enrolledAt: new Date().toISOString()
    }, { merge: true });
    return { success: true };
  } catch (err) {
    console.warn("Firestore enrollInCourse error:", err);
    return { success: false, error: err };
  }
}

export async function updateLessonProgress(lessonId: string, isCompleted: boolean, userId: string = "demo-user") {
  try {
    const lessonRef = doc(db, "lesson_progress", `${lessonId}_${userId}`);
    await setDoc(lessonRef, {
      lessonId,
      userId,
      isCompleted,
      updatedAt: new Date().toISOString()
    }, { merge: true });
    return { success: true };
  } catch (err) {
    console.warn("Firestore updateLessonProgress error:", err);
    return { success: false, error: err };
  }
}

export async function submitQuizScore(quizId: string, score: number, total: number, userId: string = "demo-user") {
  try {
    const quizRef = doc(db, "quiz_submissions", `${quizId}_${userId}`);
    await setDoc(quizRef, {
      quizId,
      userId,
      score,
      total,
      percentage: Math.round((score / total) * 100),
      submittedAt: new Date().toISOString()
    });
    return { success: true };
  } catch (err) {
    console.warn("Firestore submitQuizScore error:", err);
    return { success: false, error: err };
  }
}
