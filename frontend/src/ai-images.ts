export type AiImage = { nombre: string; mime_type: string; data: string };

export async function prepareImage(file: File): Promise<AiImage> {
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
    for (let attempt = 0; attempt < 5; attempt++) {
      canvas.width = Math.round(bitmap.width * scale);
      canvas.height = Math.round(bitmap.height * scale);
      const context = canvas.getContext("2d");
      if (!context) throw new Error("No se pudo preparar la imagen.");
      context.fillStyle = "white";
      context.fillRect(0, 0, canvas.width, canvas.height);
      context.drawImage(bitmap, 0, 0, canvas.width, canvas.height);
      data = canvas.toDataURL("image/jpeg", 0.88).split(",")[1];
      if ((data.length * 3) / 4 <= 1_000_000)
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
