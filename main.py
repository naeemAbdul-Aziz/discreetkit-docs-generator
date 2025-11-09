"""CLI entrypoint for generating discreetkit documents."""
import argparse
import os
import importlib


TEMPLATES = [
    "letterhead",
    "board_resolution",
    "watermark_template",
    "cover_page",
    "contract_employment",
    "nda",
    "privacy_policy",
    "investor_brief",
    "contract_template",
]


def generate_template(name: str, output_path: str):
    if name not in TEMPLATES:
        raise ValueError(f"Unknown template: {name}")

    module_name = f"templates.{name}"
    mod = importlib.import_module(module_name)
    # Each module exposes generate(output_path=None)
    return mod.generate(output_path)


def main():
    parser = argparse.ArgumentParser(description="DiscreetKit PDF generator")
    parser.add_argument("--template", required=True, help="Template name to generate")
    parser.add_argument("--output", required=True, help="Output PDF path")
    args = parser.parse_args()

    out_dir = os.path.dirname(os.path.abspath(args.output))
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    try:
        generate_template(args.template, args.output)
        print(f"Generated {args.output}")
    except Exception as e:
        print("Failed to generate template:", e)


if __name__ == "__main__":
    main()
