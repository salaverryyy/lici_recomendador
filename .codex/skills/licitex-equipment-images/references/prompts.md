# Prompt templates

Use these as concise scaffolds. Replace bracketed values with facts from the inspected references.

## Square gallery

```text
Use case: product-mockup
Asset type: square catalog gallery image for Licitex
Primary request: Create a polished square studio product image of [brand and model] shown in the authoritative product reference images.
Input images: Identify each authoritative product reference; identify one existing Licitex image as the style reference only.
Scene/backdrop: The same very light neutral gray-to-white seamless studio backdrop and subtle floor shadow as the style reference.
Subject: Preserve [distinctive geometry, colors, controls, connectors, screen, labels and markings] as faithfully as possible.
Style/medium: High-end realistic catalog product photography.
Composition/framing: Square 1:1 canvas, product centered and fully visible, balanced margin, useful three-quarter or front view.
Lighting/mood: Soft diffused studio lighting, clean and neutral.
Constraints: Preserve product identity and geometry; no accessories; no invented hardware; no added text, badges or watermarks; do not transform it into another product class.
```

## Horizontal cover

Use the same content, changing only:

```text
Asset type: horizontal catalog cover image for Licitex
Composition/framing: Landscape 3:2 canvas, product centered and fully visible, balanced negative space around it.
```

## Validation

Check the pair for:

- square and 3:2 dimensions;
- the same light studio background family used by existing Licitex images;
- full product visibility and a natural contact shadow;
- consistent product colors and geometry across both assets;
- legible brand/model text when it is prominent in the reference;
- absence of extra labels, props, duplicated controls, and invented connectors.

If only a minor defect appears, regenerate once with a single explicit correction while repeating all product-preservation constraints.
