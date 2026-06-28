# E-Signature

![E-Signature](e-signature.png)

A highly customizable, responsive, and animated HTML email signature generator. This project takes configuration data and compiles it into a suite of premium email signatures across multiple designs, complete with an Apple Mail-inspired preview interface.

## Key Features

- **Multi-Design Architecture**: Choose between `classic`, `portrait`, `split`, and `compact` designs. Generate all of them at once to compare.
- **HTML Email Design**: Uses `<table>` based structures with inline CSS to ensure consistent rendering across major email clients (Gmail, Outlook, Apple Mail, etc.).
- **Interactive Preview UI**: Generates a responsive, dark-mode Apple Mail mockup to preview the signature in a typical email client context.
- **Dynamic Asset Resolution**: Supports both static (PNG/JPG) and animated social media icons. *(Note: Only `.gif` format is supported for animated icons).*
- **Rich Hyperlinks**: Natively supports full redirection for social media links, personal website URLs, and `mailto:` links for quick email composition.
- **Config-Driven Architecture**: Manage names, titles, colors, and design preferences entirely through `config.json`. The included `config.json` contains generic filler data so you can easily fork this repository and swap in your own details to make it your own!
- **GitHub Pages Ready**: Includes a pre-configured `.github/workflows/static.yml` action to seamlessly deploy your signature preview and assets to GitHub Pages.
## Tech Stack

- **Language**: Python 3.12+
- **Templating Engine**: Jinja2
- **Styling**: Tailwind CSS (via CDN for the preview UI) & Vanilla CSS (inline for the email signature)
- **Frontend Logic**: Vanilla JavaScript (for dynamic skeleton loaders in the preview)

## Prerequisites

- Python 3.10 or higher
- `pip` (Python package installer)

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/user/e-signature.git
cd e-signature
```

### 2. Set Up a Virtual Environment (Optional but Recommended)

```bash
python -m venv venv

# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configuration

All signature data is stored in `config.json`. Edit this file to customize your signature.

| Key Category    | Description                                             |
| --------------- | ------------------------------------------------------- |
| `personal`      | Name, job title, company, email, and pronouns           |
| `contact`       | Website URLs and display text                           |
| `social_links`  | Links to LinkedIn, GitHub, X (Twitter), Instagram, etc. |
| `active_design` | Specifies which design template to generate by default  |
| `cta`           | Call-To-Action button text, link URL, and custom colors |
| `design`        | CSS styling parameters (colors, border radii, shadows)  |
| `hosting`       | Base URLs for resolving deployed asset paths            |


### 5. Animated GIF & Icon Guidelines

If you plan to use animated GIFs for your `signature-profile` or `signature-logo`, you must follow these design guidelines:

*   **Aspect Ratio & Dimensions**: The profile picture MUST be exactly **1:1 (Square)**. Recommended resolution is **240x240 pixels**.
*   **Light-Theme Fallbacks**: If you have a dark logo or icons and want them inverted for dark-mode templates (`portrait`, `split`, `compact`), you can place a `-light.png` or `-light.gif` (e.g. `signature-logo-light.png`) in the assets folder. The compiler will intelligently pick it up and use it!

### 6. Generate the Signature and Preview

Run the generation script in **local mode** to build the files with relative asset paths suitable for local viewing:

```bash
python e-signature.py --all --local
```

This command will output the active design (specified in config) into the root folder, and the alternative designs into a `designs/` folder:
- `designs/<design_name>/e-signature-<design_name>.html`: Your production-ready HTML email signature.
- `designs/<design_name>/index.html`: The Apple Mail mockup preview interface for that design.

Open `index.html` in your web browser to preview the result.

### 7. How to Install in Email Clients

1. Open the generated `index.html` (or your deployed URL) in your web browser.
2. Click the **"Copy Signature Card"** button in the top right of the preview toolbar, OR manually highlight the visual signature card with your mouse and press `Ctrl+C` (`Cmd+C` on Mac).
3. Paste the visual signature directly into your email client's signature box:
   *   **Gmail**: Settings > See all settings > General > Signature > Paste.
   *   **Outlook Web**: Settings > Mail > Compose and reply > Email signature > Paste.
   *   **Apple Mail**: Settings > Signatures > select a signature > Paste.

## Architecture

### Directory Structure

```
├── assets/                 # All images, avatars, and social icons
│   ├── animated/           # Lottie framework animated GIFs
│   ├── icons/              # Static PNG/SVG icons
│   └── signature-profile.png
├── designs/                # Auto-generated outputs for alternate designs
│   ├── portrait/
│   ├── split/
│   └── compact/
├── templates/              # Jinja2 template files
│   ├── index.html.j2               # The interactive preview design
│   ├── signature-classic.html.j2   # The classic email signature design
│   ├── signature-split.html.j2
│   ├── signature-compact.html.j2
│   └── signature-portrait.html.j2
├── config.json             # Configuration variables
├── e-signature.py          # The primary Python build engine
├── e-signature.html        # Generated active signature (Output)
└── index.html              # Generated active preview UI (Output)
```

### Request Lifecycle

1. The developer runs `python e-signature.py` (with flags like `--all`).
2. The script loads configuration from `config.json`.
3. The script dynamically scans the `assets/` directory to resolve which social media icons exist and prefer animated variants if available. It dynamically links `-light` variations if found.
4. The data is passed into the Jinja2 engine via the context builder.
5. The engine iterates through the designs and compiles the HTML.
6. The engine compiles `templates/index.html.j2`, injecting the signature HTML inside of it for a beautiful preview.
7. The finalized static assets are written directly to the project root and `designs/` directory.

### Key Components

**Dynamic Asset Resolution**
- The script uses `Path.rglob` to recursively scan `assets/` for matching filenames (e.g. `github.gif` or `github.png`).
- It applies a specific preference order: `animated/{name}.gif` > `icons/{name}.png`.
- A fallback logic detects `-light.png` or `-light.gif` variants and supplies them to the Jinja templates.

**Responsive Email Templating**
- Because email clients strip out modern CSS (like flexbox/grid), the templates rely exclusively on standard HTML `<table>` elements with `mso-` attributes for Outlook compatibility.
- Media queries are provided for clients that do support them, like Apple Mail and iOS Gmail, to resize avatars or shift the design dynamically.

## Environment Variables

This project does not rely on environment variables. All configuration is stored purely in `config.json` to simplify deployment as a static site.

## Available Scripts

| Command                                   | Description                                                           |
| ----------------------------------------- | --------------------------------------------------------------------- |
| `python e-signature.py`                   | Generate the default design using absolute hosted URLs. |
| `python e-signature.py --all`             | Generate all available designs simultaneously into `designs/`. |
| `python e-signature.py --local`           | Generate output files using relative local paths.                    |
| `python e-signature.py --design <name>`   | Override the default design and generate a specific design. |
| `python e-signature.py --preview`         | Generate screenshots (requires Playwright). |
| `python e-signature.py --png`             | Force the use of static PNG icons instead of animated GIFs.           |
| `python e-signature.py --config-path <p>` | Specify a custom path to a configuration JSON file.                   |
| `python e-signature.py --copy`            | Generate the signature and automatically copy the HTML to the clipboard. |

## Testing

There is currently no automated test suite configured for this project.

## Deployment

This project is architected to be deployed as a static site. You can host it on your own platform, or use one of the two primary recommended platforms: GitHub Pages or Cloudflare Workers/Pages.

### General Setup

Regardless of the platform, ensure your `config.json` reflects your target deployment domain:

```json
"hosting": {
    "repo_name": "E-Signature",
    "base_url": "https://your-domain.com"
}
```

Before deploying, run the generator *without* the `--local` flag to ensure all asset paths in the signature are compiled as absolute URLs pointing to your production domain:

```bash
python e-signature.py --all
```

### GitHub Pages

GitHub Pages is a quick way to host the signature directly from the repository.

1. In your `config.json`, set the `base_url` to your GitHub Pages URL:
   ```json
   "hosting": {
       "repo_name": "E-Signature",
       "base_url": "https://your-username.github.io/e-signature"
   }
   ```
2. Generate the production files:
   ```bash
   python e-signature.py --all
   ```
3. Commit all generated files and the `assets/` folder to your GitHub repository.
4. Navigate to your repository **Settings > Pages**.
5. Select **Deploy from a branch** and choose your `main` branch.
6. Your preview UI will be accessible at `https://your-username.github.io/e-signature/`.

### Cloudflare Workers (or Pages)

Cloudflare is recommended for high-performance static asset hosting.

1. Create a new Cloudflare Pages project pointing to your GitHub repository, or deploy via the CLI:
   ```bash
   npx wrangler pages deploy . --project-name e-signature
   ```
2. Configure your custom domain in the Cloudflare dashboard.
3. Once deployed, Cloudflare will serve `index.html` at the root, and the assets will be available at `/assets/...`.

## Troubleshooting

### Python Module Errors

**Error:** `ModuleNotFoundError: No module named 'jinja2'`
**Solution:** Ensure you have activated your virtual environment and run `pip install -r requirements.txt`.

### Missing Assets in Preview

**Error:** The preview UI shows broken image links locally.
**Solution:** Ensure you generated the files using the `--local` flag (`python e-signature.py --local`). If you omit the flag, the HTML expects the assets to be hosted on your production domain.

