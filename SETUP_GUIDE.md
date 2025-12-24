# GitHub Profile Stats Logger

## Overview

This system logs statistics from LeetCode and HackerRank for monitoring purposes. The actual stats are displayed in your README via embedded cards that update automatically.

## Features

- 🧠 **LeetCode Stats Card**: Real-time stats displayed via leetcard.jacoblin.cool
- 🏆 **HackerRank Profile Badge**: Direct link to your HackerRank profile
- ⚡ **Dynamic Typing Effect**: Animated text using readme-typing-svg
- 👀 **Profile View Counter**: Track profile visits
- 📊 **Stats Logging**: Optional scheduled logging for monitoring

## Setup Instructions

### Step 1: Repository Setup

1. **Fork or Clone** this repository to your GitHub profile repository (must be named `{your-username}/{your-username}`)
2. **Enable GitHub Actions** in your repository settings if not already enabled

### Step 2: Secrets Configuration

Navigate to your repository → **Settings** → **Secrets and variables** → **Actions**, then add the following secrets:

#### Optional Secrets:

1. **LEETCODE_USERNAME** (Optional)
   - Your LeetCode username (e.g., `your-leetcode-username`)
   - If not provided, LeetCode stats will be skipped

2. **HACKERRANK_USERNAME** (Optional)
   - Your HackerRank username (e.g., `your-hackerrank-username`)
   - If not provided, HackerRank stats will be skipped

### Step 3: Customize Your README.md

1. **Update Personal Information**: Edit the README.md file to include your personal details
2. **Update Usernames**: Replace the LeetCode and HackerRank usernames in the README with your own

### Step 4: Test the Setup

1. **Manual Trigger**: Go to Actions tab → "Update README with Latest Stats" → "Run workflow"
2. **Check Logs**: Monitor the workflow execution for any errors
3. **Verify Output**: Check if README.md was updated with your stats

## Configuration Options

### Scheduling

The default schedule runs daily at 6:00 AM UTC. To change this:

1. Edit `.github/workflows/update-readme.yml`
2. Modify the cron expression in the `schedule` section:

```yaml
schedule:
  - cron: '0 6 * * *'  # 6:00 AM UTC daily
  # - cron: '0 */12 * * *'  # Every 12 hours
  # - cron: '0 0 * * 0'     # Weekly on Sundays
```

## Troubleshooting

### Common Issues

#### 1. LeetCode/HackerRank Stats Not Updating
- **Solution**: Verify usernames are correct and profiles are public
- **Check**: Test usernames manually in browser

#### 2. README Not Committing
- **Solution**: Ensure the workflow has write permissions
- **Check**: The git config and push steps in the workflow

### Debug Steps

1. **Check Workflow Logs**:
   - Go to Actions tab → Latest workflow run → Click on job
   - Review each step for error messages

2. **Validate Secrets**:
   - Ensure all required secrets are properly set
   - Check secret names match exactly (case-sensitive)

3. **Test Locally** (Optional):
   ```bash
   # Install dependencies
   pip install requests beautifulsoup4

   # Set environment variables
   export LEETCODE_USERNAME="your_leetcode_username"
   export HACKERRANK_USERNAME="your_hackerrank_username"

   # Run script
   python scripts/update_readme.py
   ```

## Security Considerations

1. **Secret Management**: Use GitHub Secrets, never commit sensitive data to repository

---

**Note**: This system respects the terms of service of all platforms (LeetCode, HackerRank) and includes appropriate rate limiting and error handling.