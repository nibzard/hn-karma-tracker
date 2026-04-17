# Hacker News Karma Tracker

This repository automatically tracks the karma points for a Hacker News user and generates a visualization of the karma history.

## Latest Karma Plot
![Karma History](images/karma_plot.png)

## Features
- Daily automatic karma tracking
- Historical data storage in JSON format
- Visual representation with trend analysis
- Automated updates via GitHub Actions

## Setup
1. Fork this repository
2. Set up the `HN_USER_ID` secret in your repository settings
3. Enable GitHub Actions

## Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run karma tracker
python src/karma_tracker.py

# Generate plot
python src/plot_generator.py
```

## Data
- Karma history is stored in `data/karma_history.json`
- Plots are saved in `images/karma_plot.png`

## Maintenance

### Cleaning Git History

Since the workflow commits data files daily, the git history can grow large with hundreds of commits. The repository includes a script to clean this up:

```bash
./clean_history.sh
```

**Prerequisite:** the script uses [`git filter-repo`](https://github.com/newren/git-filter-repo). Install it with `brew install git-filter-repo` or `pip install git-filter-repo`.

**What it does:**

1. Saves the current versions of `karma_history.json` and `karma_plot.png`
2. Uses `git filter-repo` to remove these files from all historical commits
3. Cleans up git references and runs garbage collection to reclaim space
4. Restores the current versions and creates a fresh commit

Note: The script rewrites git history. It may break things. Make sure you have a backup before running it (e.g. the upstream GitHub repository serves as your backup).

**After running the script:**

Once you have cleaned the history, you will need to force push the changes to the remote repository to update it. Note that unless you have another backup this step is irreversible, so make sure you have a complete karma history JSON file before proceeding.

```bash
# Force push to update the remote repository
git push origin --force --all
git push origin --force --tags
```


## License
Apache 2.0
