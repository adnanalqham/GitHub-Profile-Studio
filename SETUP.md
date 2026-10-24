# Setup — adnanalqham animated GitHub profile

The profile repository `adnanalqham/adnanalqham` was not found, and the connected GitHub integration does not expose a repository-creation action. Create a **public** repository named exactly `adnanalqham`, then upload these files to its `main` branch.

## First run
1. Create the public repository `adnanalqham/adnanalqham`.
2. Upload all files while preserving their paths.
3. Open **Actions** and enable workflows if GitHub prompts you.
4. Run **Refresh profile contribution art** manually.
5. Check the logs and confirm that `assets/contrib-heatmap.svg` and `data/contributions.json` were generated.

## Accuracy
The fetch script fails instead of publishing fabricated data if GitHub changes its HTML markup. If that happens, update the CSS selector in `scripts/fetch_contributions.py`. Compare the parsed totals with your public profile.

## Personalization
Edit `PROFILE` in `scripts/render_info_card.py` to adjust the title, location, focus, technologies, and project names. The initial values reflect previously discussed work and should be reviewed for accuracy.
