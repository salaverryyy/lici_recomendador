---
name: licitex-equipment-images
description: Generate the square gallery image and horizontal catalog cover for GNSS receivers, controllers, drones, and other equipment in the Licitex visual style. Use when adding or refreshing equipment imagery for this repository; do not use for flyers, icons, or transparent cutouts.
---

# Licitex Equipment Images

Create a matched pair of realistic product images from the user's source photographs:

- `galeria-cuadrada.png`: 1:1, normally 1254 x 1254 px.
- `portada-horizontal.png`: 3:2, normally 1536 x 1024 px.

Use the built-in image generation tool. Read [references/prompts.md](references/prompts.md) for the prompt templates and validation criteria.

## Required visual identity

- Use a seamless white-to-very-light-gray studio background with a soft neutral floor shadow.
- Keep the product centered, fully visible, and surrounded by balanced empty space.
- Preserve the real equipment's silhouette, proportions, colors, controls, connectors, screens, labels, and brand/model markings as closely as the source permits.
- Keep both images consistent in viewpoint, lighting, materials, and product identity. The precise viewing angle may vary when the user allows it.
- Do not add accessories, stands, poles, slogans, badges, specifications, watermarks, or invented hardware.

## Workflow

1. Inspect every supplied product reference. Treat these as authoritative for the equipment.
2. Inspect an existing square and horizontal pair in `output/imagegen/` and use them only as references for background, lighting, framing, and finish. Prefer a product with a similar shape or the same brand.
3. Generate the square and horizontal assets as separate calls. Explicitly state each input image's role in each prompt.
4. Inspect both results. Reject outputs that crop the equipment, change its product class, invent major hardware, use the wrong background, or render a visibly wrong brand/model name.
5. Save the accepted files under `output/imagegen/<brand-model>/` using the required filenames. Do not overwrite an existing pair unless the user asked for replacement; otherwise use a version suffix.
6. Verify pixel dimensions and file readability. Report both saved paths and the prompts used.

Image creation alone does not authorize uploading assets, editing database records, committing, or pushing. Perform those actions only when the user's request includes them.
