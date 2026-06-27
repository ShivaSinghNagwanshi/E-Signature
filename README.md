# E-Signature

![E-Signature](e-signature.png)

A highly customizable, responsive HTML email signature generator. This project takes configuration data and compiles it into an HTML email signature, along with an Apple Mail-inspired preview interface.

## Key Features

- **HTML Email Layout**: Uses `<table>` based structures with inline CSS to ensure consistent rendering across major email clients (Gmail, Outlook, Apple Mail, etc.).
- **Interactive Preview UI**: Generates a responsive, dark-mode Apple Mail mockup to preview the signature in a typical email client context.
- **Dynamic Asset Resolution**: Supports both static (PNG/JPG) and animated (GIF) social media icons, detecting and linking them based on configuration.
- **Config-Driven Architecture**: Manage names, titles, colors, and layout preferences entirely through `config.json`. The included `config.json` contains generic filler data so you can easily fork this repository and swap in your own details to make it your own!
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
*(The primary dependency is `Jinja2`)*

### 4. Configuration

All signature data is stored in `config.json`. Edit this file to customize your signature.

| Key Category    | Description                                             |
| --------------- | ------------------------------------------------------- |
| `personal`      | Name, job title, company, email, and pronouns           |
| `contact`       | Website URLs and display text                           |
| `social_links`  | Links to LinkedIn, GitHub, X (Twitter), Instagram, etc. |
| `design`        | CSS styling parameters (colors, border radii, shadows)  |
| `hosting`       | Base URLs for resolving deployed asset paths            |

### 5. Generate the Signature and Preview

Run the generation script in **local mode** to build the files with relative asset paths suitable for local viewing:

```bash
python e-signature.py --local --preview
```

This command will output:
1. `e-signature.html`: Your production-ready HTML email signature.
2. `index.html`: The Apple Mail mockup preview interface.

Open `index.html` in your web browser to preview the result.

## Architecture

### Directory Structure

```text
├── assets/                 # All images, avatars, and social icons
│   ├── animated/           # Lottie framework animated GIFs
│   ├── icons/              # Static PNG/SVG icons
│   ├── signature-profile.png
│   └── signature-logo.png
├── templates/              # Jinja2 template files
│   ├── preview.html.j2     # The Apple Mail preview layout
│   └── signature.html.j2   # The core email signature layout
├── config.json             # Configuration variables
├── e-signature.py          # The primary Python build engine
├── e-signature.html        # Generated signature (Output)
└── index.html              # Generated preview UI (Output)
```

### Build Lifecycle

1. The developer runs `python e-signature.py`.
2. The script loads `config.json`.
3. The script dynamically scans the `assets/` directory to resolve which social media icons exist and prefer animated variants if available.
4. The data is passed into the Jinja2 engine.
5. The engine compiles `templates/signature.html.j2` into standard `<table>` HTML.
6. The engine compiles `templates/preview.html.j2`, injecting the signature HTML inside of it.
7. The finalized static assets (`e-signature.html` and `index.html`) are written directly to the project root.

## Available Scripts

| Command                                   | Description                                                           |
| ----------------------------------------- | --------------------------------------------------------------------- |
| `python e-signature.py`                   | Generate files using absolute URLs (for production deployment).       |
| `python e-signature.py --local`           | Generate the signature using relative local paths.                    |
| `python e-signature.py --preview`         | Generate both the signature and the `index.html` preview UI.          |
| `python e-signature.py --png`             | Force the use of static PNG icons instead of animated GIFs.           |
| `python e-signature.py --config-path <p>` | Specify a custom path to a configuration JSON file.                   |
| `python e-signature.py --copy`            | Generate the signature and automatically copy the HTML to the clipboard. |

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
python e-signature.py --preview
```

---

### Option A: Cloudflare Workers (or Pages)

Cloudflare is recommended for high-performance static asset hosting.

1. Create a new Cloudflare Pages project pointing to your GitHub repository, or deploy via the CLI:
   ```bash
   npx wrangler pages deploy . --project-name e-signature
   ```
2. Configure your custom domain in the Cloudflare dashboard (e.g., `e-signature.your-domain.com`).
3. Once deployed, Cloudflare will serve `index.html` at the root, and the assets will be available at `/assets/...`.

---

### Option B: GitHub Pages

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
   python e-signature.py --preview
   ```
3. Commit all generated files (`index.html`, `e-signature.html`) and the `assets/` folder to your GitHub repository.
4. Navigate to your repository **Settings > Pages**.
5. Select **Deploy from a branch** and choose your `main` branch.
6. Your preview UI will be accessible at `https://your-username.github.io/e-signature/`, and the raw signature at `https://your-username.github.io/e-signature/e-signature.html`.

## Troubleshooting

### Python Module Errors
**Error:** `ModuleNotFoundError: No module named 'jinja2'`
**Solution:** Ensure you have activated your virtual environment and run `pip install -r requirements.txt`.

### Missing Assets in Preview
**Error:** The preview UI shows broken image links locally.
**Solution:** Ensure you generated the files using the `--local` flag (`python e-signature.py --local --preview`). If you omit the flag, the HTML expects the assets to be hosted on your production domain.
## License and Credits

This project is open-source and available under the [MIT License](LICENSE). Feel free to fork, customize, and use it for your own personal or commercial projects.

See `CREDITS.md` for full attribution, including the Apple Mail Figma mockup design by Austin Condiff (CC BY 4.0), and iconography from Icons8 and UseAnimations.
