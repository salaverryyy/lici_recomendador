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
  } catch {
    /* Navegación disponible aunque el navegador bloquee el almacenamiento. */
  }
}
export function usePersistentState<T>(key: string, initial: T) {
  const [value, setValue] = useState<T>(() => readStored(key, initial));
  useEffect(() => writeStored(key, value), [key, value]);
  return [value, setValue] as const;
}
