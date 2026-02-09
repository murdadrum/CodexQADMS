"use client";

import { useEffect, useState } from "react";
import { getFirebaseAuth, googleProvider } from "../lib/firebase";
import { signInWithPopup, signOut, onAuthStateChanged, type User } from "firebase/auth";

export function AuthPanel() {
  const [user, setUser] = useState<User | null>(null);
  const [error, setError] = useState<string | null>(null);
  const auth = getFirebaseAuth();
  const enabled = Boolean(auth);

  useEffect(() => {
    if (!auth) return;
    const unsub = onAuthStateChanged(auth, (next) => setUser(next));
    return () => unsub();
  }, [auth]);

  const handleSignIn = async () => {
    if (!auth) return;
    setError(null);
    try {
      await signInWithPopup(auth, googleProvider);
    } catch (err: any) {
      setError(err?.message ?? "Sign-in failed");
    }
  };

  const handleSignOut = async () => {
    if (!auth) return;
    setError(null);
    try {
      await signOut(auth);
    } catch (err: any) {
      setError(err?.message ?? "Sign-out failed");
    }
  };

  if (!enabled) {
    return (
      <div className="rounded-2xl border border-line/70 bg-white/90 p-4 shadow-sm space-y-2">
        <p className="text-sm text-ink font-semibold">Auth</p>
        <p className="text-sm text-slate-700">
          Firebase env vars are not set. Add `.env.local` with NEXT_PUBLIC_FIREBASE_* keys to enable sign-in.
        </p>
      </div>
    );
  }

  return (
    <div className="rounded-2xl border border-line/70 bg-white/90 p-4 shadow-sm space-y-2">
      <div className="flex items-center justify-between gap-2">
        <div>
          <p className="text-sm text-ink font-semibold">Auth</p>
          <p className="text-xs text-slate-600">Firebase (Google)</p>
        </div>
        {user ? (
          <button
            onClick={handleSignOut}
            className="rounded-lg border border-line bg-white px-3 py-1.5 text-sm font-medium text-ink shadow-sm"
          >
            Sign out
          </button>
        ) : (
          <button
            onClick={handleSignIn}
            className="rounded-lg bg-brand px-3 py-1.5 text-sm font-medium text-white shadow-sm"
          >
            Sign in with Google
          </button>
        )}
      </div>
      {user ? (
        <div className="text-sm text-slate-800">
          <p className="font-semibold">{user.displayName || user.email}</p>
          {user.email && <p className="text-xs text-slate-600">{user.email}</p>}
        </div>
      ) : (
        <p className="text-sm text-slate-700">Not signed in.</p>
      )}
      {error && <p className="text-sm text-red-700">{error}</p>}
    </div>
  );
}
