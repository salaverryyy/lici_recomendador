export type AiImage = { nombre: string; mime_type: string; data: string };
export const MAX_IMAGES = 10;
export const MAX_IMAGE_TOTAL = 2_400_000;

export async function prepareImage(
  file: File,
  maxBytes = 1_000_000,
): Promise<AiImage> {
  if (!["image/jpeg", "image/png", "image/webp"].includes(file.type))
    throw new Error("Adjunta imágenes JPG, PNG o WebP.");
  if (file.size > 20_000_000)
    throw new Error(
      "La imagen supera 20 MB. Recorta la página antes de adjuntarla.",
    );
  const bitmap = await createImageBitmap(file);
  try {
    if (bitmap.width < 16 || bitmap.height < 16)
      throw new Error("La imagen es demasiado pequeña para interpretar texto.");
    let scale = Math.min(1, 2200 / Math.max(bitmap.width, bitmap.height));
    const canvas = document.createElement("canvas");
    let data = "";
    for (let attempt = 0; attempt < 8; attempt++) {
      canvas.width = Math.round(bitmap.width * scale);
      canvas.height = Math.round(bitmap.height * scale);
      const context = canvas.getContext("2d");
      if (!context) throw new Error("No se pudo preparar la imagen.");
      context.fillStyle = "white";
      context.fillRect(0, 0, canvas.width, canvas.height);
      context.drawImage(bitmap, 0, 0, canvas.width, canvas.height);
      data = canvas
        .toDataURL("image/jpeg", attempt < 2 ? 0.88 : 0.78)
        .split(",")[1];
      if ((data.length * 3) / 4 <= maxBytes)
        return {
          nombre: file.name.slice(0, 150),
          mime_type: "image/jpeg",
          data,
        };
      scale *= 0.8;
    }
    throw new Error(
      "No se pudo ajustar el tamaño. Recorta la imagen y reintenta.",
    );
  } finally {
    bitmap.close();
  }
}

export async function prepareImages(
  files: File[],
  existing: AiImage[],
): Promise<AiImage[]> {
  const count = files.length + existing.length;
  if (count > MAX_IMAGES)
    throw new Error(
      `Puedes adjuntar hasta ${MAX_IMAGES} imágenes por mensaje.`,
    );
  const budget = Math.min(
    1_000_000,
    Math.floor(MAX_IMAGE_TOTAL / Math.max(count, 1)) - 100,
  );
  const result: AiImage[] = [];
  for (const img of existing) {
    if ((img.data.length * 3) / 4 <= budget) result.push(img);
    else {
      const bytes = Uint8Array.from(atob(img.data), (c) => c.charCodeAt(0));
      result.push(
        await prepareImage(
          new File([bytes], img.nombre, { type: img.mime_type }),
          budget,
        ),
      );
    }
  }
  for (const file of files) result.push(await prepareImage(file, budget));
  return result;
}
