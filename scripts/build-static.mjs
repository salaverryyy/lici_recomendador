import { cp, mkdir } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
const destino = fileURLToPath(new URL('../public/', import.meta.url));
await mkdir(destino, { recursive: true });
await cp(fileURLToPath(new URL('../frontend/dist/', import.meta.url)), destino, { recursive: true });
console.log('Interfaz preparada en public/ para el CDN de Vercel.');
