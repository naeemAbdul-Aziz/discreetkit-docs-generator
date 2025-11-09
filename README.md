# DiscreetKit Docs (scaffold)

This scaffold generates branded PDF documents for Access DiscreetKit Ltd using ReportLab.

Structure

- `assets/` — logo(s), watermark, brand colors JSON (`assets/brand_colors.json`), optional `assets/fonts/`.
- `templates/` — individual document template modules (each has `generate(output_path)`).
- `output/` — generated PDFs.

Usage

Run a template via the CLI. Example:

```
python main.py --template letterhead --output output/letterhead_sample.pdf
```

Replace `assets/logo.png` and `assets/watermark.png` with your real images. If you have multiple logo variants, place them under `assets/logos/` as well.

## Satoshi Font Setup

To use the Satoshi font for all document text:

1. Obtain Satoshi Regular and Bold (`Satoshi-Regular.ttf`, `Satoshi-Bold.ttf`).
2. Place them in either `assets/fonts/` (recommended) or put a single `Satoshi.ttf` in the project root.
3. The code will automatically register and use Satoshi if found; otherwise it falls back to Helvetica.

If you want to use a different font file or location, update the search paths in `templates/common.py` (`register_satoshi_font()`).

## Brand colors

The color palette lives in `assets/brand_colors.json`. It includes both the new brand keys and legacy keys used by the templates, mapped to the new palette, so templates render with the latest colors automatically.
