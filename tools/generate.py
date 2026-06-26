"""
Email Signature Generator
=========================
Reads config.json, auto-detects .gif/.png assets, renders the Jinja2 template,
and outputs the final email signature HTML.

Usage:
    python tools/generate.py                  # Generate with hosted URLs
    python tools/generate.py --local          # Generate with local file paths (for preview)
    python tools/generate.py --copy           # Generate and copy HTML to clipboard
    python tools/generate.py --local --copy   # Local preview + clipboard
"""

import json
import os
import sys
import argparse
from pathlib import Path
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from jinja2 import Environment, FileSystemLoader
PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = PROJECT_ROOT / "config.json"
TEMPLATES_DIR = PROJECT_ROOT / "templates"
ASSETS_DIR = PROJECT_ROOT / "assets"
ICONS_DIR = ASSETS_DIR / "icons"
OUTPUT_DIR = PROJECT_ROOT / "output"
SOCIAL_ICON_ORDER_DEFAULT = ["website", "instagram", "linkedin", "github", "x"]

def load_config() -> dict:
    """Load and validate config.json."""
    if not CONFIG_PATH.exists():
        print(f"❌ Config not found: {CONFIG_PATH}")
        sys.exit(1)

    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = json.load(f)

    return config

def resolve_asset_extension(base_dir: Path, name: str) -> str:
    """
    Auto-detect .gif vs .png for an asset.
    Returns the extension (without dot) — 'gif' or 'png'.
    Prefers .gif if it exists.
    """
    gif_path = base_dir / f"{name}.gif"
    png_path = base_dir / f"{name}.png"

    if gif_path.exists():
        return "gif"
    elif png_path.exists():
        return "png"
    else:
        return "png"  # Default fallback

def build_template_context(config: dict, use_local: bool = False) -> dict:
    """
    Build the full context dictionary for the Jinja2 template.
    Handles asset resolution, URL building, and conditional features.
    """
    if use_local:
        asset_base_url = "../assets"
    else:
        hosting = config.get("hosting", {})
        base_url = hosting.get("base_url", "")
        asset_base_url = f"{base_url}/assets" if base_url else "./assets"
    profile_name = config.get("assets", {}).get("profile_photo", "signature-profile")
    profile_ext = resolve_asset_extension(ASSETS_DIR, profile_name)
    profile_filename = f"{profile_name}.{profile_ext}"
    logo_name = config.get("assets", {}).get("logo", "signature-logo")
    logo_ext = resolve_asset_extension(ASSETS_DIR, logo_name)
    logo_filename = f"{logo_name}.{logo_ext}"
    social_order = config.get("social_order", SOCIAL_ICON_ORDER_DEFAULT)
    icon_extensions = {}
    for icon_name in social_order:
        icon_extensions[icon_name] = resolve_asset_extension(ICONS_DIR, icon_name)
    verified_exists = (ICONS_DIR / "verified.png").exists() or (ICONS_DIR / "verified.gif").exists()
    if verified_exists:
        icon_extensions["verified"] = resolve_asset_extension(ICONS_DIR, "verified")
    background_filename = None
    for ext in ["jpg", "jpeg", "png", "gif", "webp"]:
        if (ASSETS_DIR / f"background.{ext}").exists():
            background_filename = f"background.{ext}"
            break
    social_links = {k: v for k, v in config.get("social_links", {}).items() if v}
    design_defaults = {
        "accent_color": "#6366f1",
        "text_primary": "#1a1a2e",
        "text_secondary": "#64748b",
        "text_muted": "#94a3b8",
        "border_color": "#e5e7eb",
        "card_border_radius": "12px",
        "font_family": "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif",
        "profile_shape": "rounded-square",
        "profile_size": 120,
        "icon_size": 22,
        "icon_color": "#64748b",
    }
    active_theme = config.get("active_theme", "glassmorphism")
    theme_config = config.get("themes", {}).get(active_theme, {})
    design = {**design_defaults, **config.get("design", {}), **theme_config}
    design["style"] = active_theme
    personal = config.get("personal", {})
    if not personal:
        personal = {
            "full_name": config.get("full_name", ""),
            "job_title": config.get("job_title", ""),
            "company": config.get("company", ""),
            "email": config.get("email", ""),
        }
    contact = config.get("contact", {})
    if not contact:
        contact = {
            "website": config.get("website", ""),
            "website_display": config.get("website", ""),
        }
    if "website_display" not in contact and "website" in contact:
        display = contact["website"].replace("https://", "").replace("http://", "").rstrip("/")
        contact["website_display"] = display
    cta_defaults = {"enabled": False, "text": "", "url": "", "style": "pill"}
    cta = {**cta_defaults, **config.get("cta", {})}
    assets = config.get("assets", {})

    return {
        "personal": personal,
        "contact": contact,
        "social_links": social_links,
        "social_order": social_order,
        "design": design,
        "cta": cta,
        "assets": assets,
        "asset_base_url": asset_base_url,
        "profile_filename": profile_filename,
        "logo_filename": logo_filename,
        "icon_extensions": icon_extensions,
        "verified_icon_exists": verified_exists,
        "background_filename": background_filename,
    }

def generate_signature(config: dict, use_local: bool = False) -> str:
    """Generate the email signature HTML from config and template."""
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=False,  # We're generating HTML, not escaping it
        trim_blocks=True,
        lstrip_blocks=True,
    )

    template = env.get_template("signature.html.j2")
    context = build_template_context(config, use_local=use_local)
    html = template.render(**context)

    return html

def main():
    parser = argparse.ArgumentParser(description="Generate email signature HTML")
    parser.add_argument("--local", action="store_true",
                        help="Use local file paths instead of hosted URLs")
    parser.add_argument("--copy", action="store_true",
                        help="Copy generated HTML to clipboard")
    parser.add_argument("--output", type=str, default=None,
                        help="Custom output file path")
    args = parser.parse_args()

    print("=" * 60)
    print("  Email Signature Generator")
    print("=" * 60)
    config = load_config()
    name = config.get("personal", {}).get("full_name") or config.get("full_name", "Unknown")
    print(f"  Name: {name}")
    print(f"  Mode: {'Local preview' if args.local else 'Hosted URLs'}")
    print()
    profile_name = config.get("assets", {}).get("profile_photo", "signature-profile")
    profile_ext = resolve_asset_extension(ASSETS_DIR, profile_name)
    logo_name = config.get("assets", {}).get("logo", "signature-logo")
    logo_ext = resolve_asset_extension(ASSETS_DIR, logo_name)
    print(f"  Profile: {profile_name}.{profile_ext}")
    print(f"  Logo:    {logo_name}.{logo_ext}")
    print("  Icons:")
    social_order = config.get("social_order", SOCIAL_ICON_ORDER_DEFAULT)
    for icon in social_order:
        ext = resolve_asset_extension(ICONS_DIR, icon)
        exists = (ICONS_DIR / f"{icon}.{ext}").exists()
        status = "✅" if exists else "⚠️ "
        print(f"    {status} {icon}.{ext}")
    print()
    html = generate_signature(config, use_local=args.local)
    OUTPUT_DIR.mkdir(exist_ok=True)
    output_path = Path(args.output) if args.output else OUTPUT_DIR / "signature.html"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    file_size = output_path.stat().st_size
    print(f"  ✅ Generated: {output_path}")
    print(f"  📦 Size: {file_size} bytes ({file_size / 1024:.1f} KB)")
    if args.copy:
        try:
            import pyperclip
            pyperclip.copy(html)
            print("  📋 Copied to clipboard!")
        except Exception as e:
            print(f"  ⚠  Could not copy to clipboard: {e}")

    print()
    print("=" * 60)
    print("  Done! ✨")
    print("=" * 60)

if __name__ == "__main__":
    main()
