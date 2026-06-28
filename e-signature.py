"""
Email Signature Generator
=========================
Reads config.json, auto-detects .gif/.png assets, renders the Jinja2 template,
and outputs the final email signature HTML.

Usage:
    python e-signature.py                  # Generate with hosted URLs
    python e-signature.py --local          # Generate with local file paths (for preview)
    python e-signature.py --copy           # Generate and copy HTML to clipboard
    python e-signature.py --local --copy   # Local preview + clipboard
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
PROJECT_ROOT = Path(__file__).resolve().parent
CONFIG_PATH = PROJECT_ROOT / "config.json"
TEMPLATES_DIR = PROJECT_ROOT / "templates"
ASSETS_DIR = PROJECT_ROOT / "assets"
ICONS_DIR = ASSETS_DIR / "icons"
OUTPUT_DIR = PROJECT_ROOT / "output"
SOCIAL_ICON_ORDER_DEFAULT = ["website", "instagram", "linkedin", "github", "x"]

def load_config(config_path: Path = CONFIG_PATH) -> dict:
    """Load and validate config.json."""
    if not config_path.exists():
        print(f"❌ Config not found: {config_path}")
        sys.exit(1)

    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    return config

def resolve_asset_path(name: str, fallback_subdir: str = "", force_png: bool = False) -> str:
    """
    Looks for .gif in assets/animated/ or root first (unless force_png is True).
    Falls back to .png in assets/{fallback_subdir}/.
    Returns path relative to ASSETS_DIR.
    """
    animated_dir = ASSETS_DIR / "animated"
    fallback_dir = ASSETS_DIR / fallback_subdir if fallback_subdir else ASSETS_DIR
    
    if not force_png:
        if (animated_dir / f"{name}.gif").exists():
            return f"animated/{name}.gif"
        if (fallback_dir / f"{name}.gif").exists():
            return f"{fallback_subdir}/{name}.gif" if fallback_subdir else f"{name}.gif"
        
    if (fallback_dir / f"{name}.png").exists():
        return f"{fallback_subdir}/{name}.png" if fallback_subdir else f"{name}.png"
    # Fallback to PNG name even if missing so templates don't break entirely
    return f"{fallback_subdir}/{name}.png" if fallback_subdir else f"{name}.png"

def build_template_context(config: dict, use_local: bool = False, force_png: bool = False) -> dict:
    """
    Build the full context dictionary for the Jinja2 template.
    Handles asset resolution, URL building, and conditional features.
    """
    if use_local:
        asset_base_url = "assets"
    else:
        hosting = config.get("hosting", {})
        base_url = hosting.get("base_url", "")
        asset_base_url = f"{base_url}/assets" if base_url else "./assets"
    profile_name = config.get("assets", {}).get("profile_photo", "signature-profile")
    profile_filename = resolve_asset_path(profile_name, force_png=force_png)
    profile_png_filename = resolve_asset_path(profile_name, force_png=True)
    profile_is_gif = profile_filename.endswith(".gif")
    logo_name = config.get("assets", {}).get("logo", "signature-logo")
    logo_filename = resolve_asset_path(logo_name, force_png=force_png)
    social_order = config.get("social_order", SOCIAL_ICON_ORDER_DEFAULT)
    icon_paths = {}
    for icon_name in social_order:
        icon_paths[icon_name] = resolve_asset_path(icon_name, fallback_subdir="icons", force_png=force_png)
    verified_exists = (ICONS_DIR / "verified.png").exists() or (ASSETS_DIR / "animated" / "verified.gif").exists()
    if verified_exists:
        icon_paths["verified"] = resolve_asset_path("verified", fallback_subdir="icons")
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
        "hosting": config.get("hosting", {}),
        "asset_base_url": asset_base_url,
        "profile_filename": profile_filename,
        "profile_png_filename": profile_png_filename,
        "profile_is_gif": profile_is_gif,
        "logo_filename": logo_filename,
        "icon_paths": icon_paths,
        "verified_icon_exists": verified_exists,
        "background_filename": background_filename,
    }

def generate_signature(config: dict, use_local: bool = False, force_png: bool = False) -> str:
    """Generate the email signature HTML from config and template."""
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=False,  # We're generating HTML, not escaping it
        trim_blocks=True,
        lstrip_blocks=True,
    )

    template = env.get_template("signature.html.j2")
    context = build_template_context(config, use_local=use_local, force_png=force_png)
    html = template.render(**context)

    return html

def generate_preview(config: dict, signature_html: str, use_local: bool = False, force_png: bool = False) -> str:
    """Generate the preview index.html containing the signature."""
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=False,
    )
    template_path = TEMPLATES_DIR / "index.html.j2"
    if not template_path.exists():
        return ""
        
    template = env.get_template("index.html.j2")
    context = build_template_context(config, use_local=use_local, force_png=force_png)
    context["signature_html"] = signature_html
    return template.render(**context)

def generate_png_screenshot(html_path: Path, output_png: Path, meta_png: Path):
    """Generate a high-res PNG screenshot and a compressed meta PNG (e.g. for WhatsApp)."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("  ⚠️  Playwright not installed. Skipping PNG generation. (pip install playwright)")
        return
        
    print("  📸 Generating PNG screenshots...")
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            uri = f"file:///{html_path.absolute().as_posix()}"
            
            context_high = browser.new_context(device_scale_factor=3)
            page_high = context_high.new_page()
            page_high.set_viewport_size({"width": 800, "height": 600})
            page_high.goto(uri)
            page_high.wait_for_load_state("networkidle")
            page_high.wait_for_timeout(5000)
            page_high.locator("table").first.screenshot(path=output_png, omit_background=True)
            print(f"  ✅ Generated high-res PNG (3x): {output_png.name} ({output_png.stat().st_size / 1024:.1f} KB)")
            context_high.close()

            for scale in [2, 1]:
                context_meta = browser.new_context(device_scale_factor=scale)
                page_meta = context_meta.new_page()
                page_meta.set_viewport_size({"width": 800, "height": 418})
                page_meta.goto(uri)
                page_meta.wait_for_load_state("networkidle")
                page_meta.wait_for_timeout(5000)
                
                page_meta.evaluate("document.body.style.display = 'flex'; document.body.style.justifyContent = 'center'; document.body.style.alignItems = 'center'; document.body.style.height = '100vh';")
                page_meta.screenshot(path=meta_png, omit_background=True)
                context_meta.close()
                
                size_kb = meta_png.stat().st_size / 1024
                if size_kb <= 290 or scale == 1:
                    print(f"  ✅ Generated meta PNG ({scale}x): {meta_png.name} ({size_kb:.1f} KB)")
                    break
                else:
                    print(f"  🔄 Meta {scale}x was {size_kb:.1f} KB (too large). Trying lower scale...")
                    
            browser.close()
    except Exception as e:
        print(f"  ❌ Error generating PNG: {e}")

def main():
    parser = argparse.ArgumentParser(description="Generate email signature HTML")
    parser.add_argument("--local", action="store_true",
                        help="Use local file paths instead of hosted URLs")
    parser.add_argument("--copy", action="store_true",
                        help="Copy generated HTML to clipboard")
    parser.add_argument("--preview", action="store_true",
                        help="Generate the index.html preview page")
    parser.add_argument("--png", action="store_true",
                        help="Force using static PNG icons instead of animated GIFs")
    parser.add_argument("--output", type=str, default=None,
                        help="Custom output file path")
    parser.add_argument("--config-path", type=str, default=None,
                        help="Path to a custom config.json file")
    args = parser.parse_args()

    print("=" * 60)
    print("  Email Signature Generator")
    print("=" * 60)
    custom_config_path = Path(args.config_path) if args.config_path else CONFIG_PATH
    config = load_config(custom_config_path)
    name = config.get("personal", {}).get("full_name") or config.get("full_name", "Unknown")
    print(f"  Name: {name}")
    print(f"  Mode: {'Local preview' if args.local else 'Hosted URLs'}")
    print()
    profile_name = config.get("assets", {}).get("profile_photo", "signature-profile")
    profile_path = resolve_asset_path(profile_name, force_png=args.png)
    logo_name = config.get("assets", {}).get("logo", "signature-logo")
    logo_path = resolve_asset_path(logo_name, force_png=args.png)
    print(f"  Profile: {profile_path}")
    print(f"  Logo:    {logo_path}")
    print("  Icons:")
    social_order = config.get("social_order", SOCIAL_ICON_ORDER_DEFAULT)
    for icon in social_order:
        path = resolve_asset_path(icon, fallback_subdir="icons", force_png=args.png)
        exists = (ASSETS_DIR / path).exists()
        status = "✅" if exists else "⚠️ "
        print(f"    {status} {path}")
    print()
    html = generate_signature(config, use_local=args.local, force_png=args.png)
    output_path = Path(args.output) if args.output else PROJECT_ROOT / "e-signature.html"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    file_size = output_path.stat().st_size
    print(f"  ✅ Generated: {output_path}")
    print(f"  📦 Size: {file_size} bytes ({file_size / 1024:.1f} KB)")
    preview_html = generate_preview(config, html, use_local=args.local, force_png=args.png)
    if preview_html:
        preview_path = PROJECT_ROOT / "index.html"
        with open(preview_path, "w", encoding="utf-8") as f:
            f.write(preview_html)
        print(f"  ✅ Generated Preview: {preview_path}")
    else:
        print("  ⚠  Could not generate preview: templates/index.html.j2 missing.")

    if args.preview:
        png_path = PROJECT_ROOT / "e-signature.png"
        meta_path = PROJECT_ROOT / "e-signature-meta.png"
        generate_png_screenshot(output_path, png_path, meta_path)
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
