# Vectora Website: Documentação Open-Source com Hugo + Hextra

Vectora Website é a documentação oficial em HTML estática gerada com Hugo + Hextra theme. Contém guides de setup (local, Docker, VPS), API reference (auto-generated from OpenAPI), architecture deep-dive, integration guides para cada SDK, contributing guidelines, e blog. Suporta múltiplos idiomas (English e Português Brasileiro) via Hugo i18n. Deploy automático para GitHub Pages, Netlify, ou Fly.io via GitHub Actions.

## Stack

Hugo é o gerador de sites estáticos (não precisa banco de dados, serve HTML puro). Hextra é o theme moderno open-source com search built-in. Markdown é a linguagem de escrita. Hugo i18n gerencia múltiplos idiomas sem duplicação. GitHub Pages/Netlify faz deploy automático. Zero complexidade, máxima velocidade.

- Static Site Generator: Hugo 0.120+
- Theme: Hextra (modern, responsive, open-source)
- Content: Markdown (Hugo processes to HTML)
- Internationalization: Hugo i18n (en, pt-br)
- Deployment: GitHub Pages OR Netlify OR Fly.io
- CI/CD: GitHub Actions (build on push, deploy)
- Search: Built-in Hextra search (no external service)

## Mapa Mental

Website é purado HTML estático servido via CDN. Usuário navega docs em Markdown format. Hugo processa em build time para HTML. Hextra theme fornece navegação, responsiveness, search. i18n permite same content em múltiplos idiomas. Deployment é trivial (push to GitHub, auto-build).

```
Developer edits Markdown
    |
    V
Git push
    |
    V
GitHub Actions trigger
    |
    +-- Hugo build (en, pt-br)
    |
    +-- Hextra theme processing
    |
    +-- Generate HTML static files
    |
    V
Deploy to CDN (GitHub Pages/Netlify/Fly)
    |
    V
User visits vectora.ai
    |
    +-- CDN serves static HTML
    |
    +-- Built-in search works
    |
    V
Read docs instantly (no backend needed)
```

## Estrutura

Root /docs contém hugo.toml config, themes/hextra submodule, content/(en e pt-br) com markdown, static/ para assets. Cada section de documentação é um folder separado em content/(lang)/docs/.

```
vectora-website/
├── config.toml                          (Hugo config)
│   ├── baseURL = "https://vectora.ai"
│   ├── defaultContentLanguage = "en"
│   ├── defaultContentLanguageInSubdir = true
│   └── theme = "hextra"
│
├── content/                             (Markdown files)
│   ├── en/                              (English)
│   │   ├── _index.md                    (Home page)
│   │   ├── docs/
│   │   │   ├── _index.md                (Docs overview)
│   │   │   ├── getting-started/
│   │   │   │   ├── _index.md
│   │   │   │   ├── local.md             (Setup local)
│   │   │   │   ├── docker.md            (Setup Docker)
│   │   │   │   └── vps.md               (Setup VPS)
│   │   │   ├── architecture/
│   │   │   │   ├── _index.md
│   │   │   │   ├── overview.md
│   │   │   │   ├── tier-based.md
│   │   │   │   └── data-flow.md
│   │   │   ├── api-reference/
│   │   │   │   ├── _index.md
│   │   │   │   ├── chat.md
│   │   │   │   ├── memory.md
│   │   │   │   ├── datasets.md
│   │   │   │   ├── auth.md
│   │   │   │   └── settings.md
│   │   │   ├── integrations/
│   │   │   │   ├── _index.md
│   │   │   │   ├── claude-code.md
│   │   │   │   ├── gemini-cli.md
│   │   │   │   ├── paperclip.md
│   │   │   │   └── custom.md
│   │   │   ├── contributing/
│   │   │   │   ├── _index.md
│   │   │   │   ├── dev-setup.md
│   │   │   │   ├── code-style.md
│   │   │   │   └── pull-requests.md
│   │   │   └── faq/
│   │   │       ├── _index.md
│   │   │       └── troubleshooting.md
│   │   ├── blog/
│   │   │   ├── _index.md
│   │   │   ├── 2026-05-01-launch.md
│   │   │   └── 2026-06-01-phase2.md
│   │   └── about/
│   │       └── _index.md
│   │
│   └── pt-br/                           (Portuguese Brazil)
│       ├── _index.md
│       ├── docs/
│       │   ├── _index.md
│       │   ├── getting-started/
│       │   │   ├── _index.md
│       │   │   ├── local.md
│       │   │   ├── docker.md
│       │   │   └── vps.md
│       │   ├── architecture/
│       │   │   ├── _index.md
│       │   │   └── ... (same as en/)
│       │   ├── api-reference/
│       │   ├── integrations/
│       │   ├── contributing/
│       │   └── faq/
│       ├── blog/
│       └── about/
│
├── static/                              (Assets)
│   ├── images/
│   │   ├── logo.png
│   │   ├── architecture-diagram.png
│   │   └── ...
│   ├── diagrams/
│   └── downloads/
│       ├── vectora-cli-linux-x64
│       ├── vectora-cli-macos-x64
│       └── vectora-cli-windows-x64.exe
│
├── themes/
│   └── hextra/                          (Submodule: github.com/imfing/hextra)
│       ├── layouts/
│       ├── static/
│       ├── assets/
│       └── config.toml
│
├── .github/
│   └── workflows/
│       ├── build-deploy.yml             (Hugo build + deploy)
│       └── link-check.yml               (Check for broken links)
│
├── hugo.toml                            (Hugo 0.87+ config format)
├── .gitignore
├── .gitmodules                          (Hextra as submodule)
├── README.md
└── LICENSE
```

---

## Development Setup

```bash
git clone https://github.com/vectora/vectora-website.git
cd vectora-website

# Initialize submodules (Hextra theme)
git submodule update --init --recursive

# Install Hugo (if not already)
# macOS: brew install hugo
# Linux: apt install hugo
# Windows: choco install hugo-extended

# Run local dev server
hugo server

# Website live at http://localhost:1313
```

## Deployment

GitHub Actions automatically builds and deploys on push to main:

```yaml
# .github/workflows/build-deploy.yml
- name: Build with Hugo
  run: hugo --gc --minify

- name: Deploy to GitHub Pages
  uses: peaceiris/actions-gh-pages@v3
  with:
    github_token: ${{ secrets.GITHUB_TOKEN }}
    publish_dir: ./public
```

## Internationalization

Content is duplicated in en/ and pt-br/ folders. Hugo i18n system handles language selection. URL structure: /en/docs/... and /pt-br/docs/...

## License

Apache 2.0
