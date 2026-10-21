import { useEffect, useState } from "react";

export function readStored<T>(key: string, fallback: T): T {
  try {
    const raw = localStorage.getItem(key);
    return raw === null ? fallback : JSON.parse(raw);
  } catch {
    return fallback;
  }
}
export function writeStored(key: string, value: unknown) {
  try {
    localStorage.setItem(key, JSON.stringify(value));
    return true;
  } catch {
    /* Navegación disponible aunque el navegador bloquee el almacenamiento. */
    return false;
  }
}
export function usePersistentState<T>(key: string, initial: T) {
  const [value, setValue] = useState<T>(() => readStored(key, initial));
  const [storageError, setStorageError] = useState(false);
  useEffect(() => {
    setStorageError(!writeStored(key, value));
  }, [key, value]);
  return [value, setValue, storageError] as const;
}
