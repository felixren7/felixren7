# Install this GitHub profile

This package is prepared for the GitHub account **felixren7**. Keep the directory structure exactly as shown. It has not been published to GitHub yet.

## 1. Create the profile repository

At https://github.com/new, create a **Public** repository named exactly `felixren7` under the `felixren7` account. Initialize it empty. A repository whose name matches your username supplies the profile README.

## 2. Add the files

Unzip this package. In a terminal in the unzipped `felixren7-profile` directory:

```bash
git init -b main
git add README.md SETUP.md .github/workflows/metrics.yml .github/workflows/snake.yml .github/workflows/daily-card.yml scripts/daily_card.py assets/daily-card.svg
git commit -m "Create engineering profile"
git remote add origin https://github.com/felixren7/felixren7.git
git push -u origin main
```

If you initialized the repository with a README on GitHub, clone it first and copy the package's files into that clone, replacing only its placeholder README. Then commit and push.

## 3. Set up the metrics token

Metrics needs a personal token for user-level API data. In GitHub Settings → Developer settings → Personal access tokens, create a token for public profile data with the minimum required access. The project's official instructions describe a scope-less classic token as a starting point; if you add private/organization data later, review their extra scopes carefully. Store the token at repository Settings → Secrets and variables → Actions → New repository secret, with the exact name `METRICS_TOKEN`. Never put the token in a file, commit, or chat. See https://github.com/lowlighter/metrics/blob/master/.github/readme/partials/documentation/setup/action.md

In Settings → Actions → General → Workflow permissions, allow GitHub Actions to write repository contents, so generated SVGs can be committed. The workflow also declares `contents: write`.

## 4. Run and inspect

Run all three workflows once from the repository Actions tab using **Run workflow**:

1. **Profile metrics** generates `metrics.svg`, `achievements.svg`, `languages.svg` on `main`.
2. **Contribution snake** creates the `output` branch and two animated SVGs.
3. **Singapore weather and daily thought** replaces the placeholder card in `assets/daily-card.svg`.

Reload https://github.com/felixren7 after they succeed. Scheduled runs are daily. GitHub can delay scheduled jobs at busy times. A missing image immediately after the initial push is expected until its workflow has run successfully.

## 5. Make the project section accurate

The three featured projects are written as descriptions only. When the correct public repositories are ready, link their headings to those exact URLs. Never link a company's private implementation or upload source code without permission. Edit your stack and measured performance claims if they differ from your actual work.

## Appearance and maintenance

- Visitor badge: external counter at `komarev.com`; it measures image requests, not unique people.
- Achievements: Metrics `plugin_achievements` instead of the hosted trophy image service, whose endpoint has had availability reports.
- Snake: generated with `Platane/snk` and published on a dedicated `output` branch, with light and dark variants.
- Weather: Open-Meteo current conditions for Singapore, refreshed daily; the card keeps the previous reading on temporary API failures.
- Thought: one of ten original short engineering thoughts picked on each successful update.
- Language analysis: authored commit patches can take time. `freeCodeCamp` and `CISE_Repos` are skipped because they are large or likely to distort personal language figures. Remove entries from `plugin_languages_skipped` if you want them counted.
- The Metrics action is pinned to `v3.34` so scheduled runs stay reproducible; bump it deliberately and skim the release notes first. `Platane/snk` still tracks the moving `v3` tag — pin it to `v3.5.0` if you want the same guarantee there.

Sources: https://github.com/lowlighter/metrics · https://github.com/Platane/snk · https://open-meteo.com/en/docs · https://github.com/antonkomarev/github-profile-views-counter
