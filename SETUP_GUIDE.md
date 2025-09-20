# Automated GitHub Profile README Stats System

## Overview

This system automatically updates your GitHub profile README.md with real-time statistics from GitHub, LeetCode, and HackerRank. The system runs as a GitHub Action on a scheduled basis and commits the updated stats directly to your repository.

## Features

- 📊 **GitHub Statistics**: Total commits, stars, and top programming languages
- 🧠 **LeetCode Stats**: Problems solved by difficulty, ranking
- 🏆 **HackerRank Stats**: Badges, rank, and top skills
- ⚡ **Dynamic Typing Effect**: Animated text using readme-typing-svg
- 👀 **Profile View Counter**: Track profile visits
- 🔄 **Automated Updates**: Runs daily at 6:00 AM UTC
- 📝 **Smart Updates**: Only commits when there are actual changes

## Setup Instructions

### Step 1: Repository Setup

1. **Fork or Clone** this repository to your GitHub profile repository (must be named `{your-username}/{your-username}`)
2. **Enable GitHub Actions** in your repository settings if not already enabled

### Step 2: Required Secrets Configuration

Navigate to your repository → **Settings** → **Secrets and variables** → **Actions**, then add the following secrets:

#### Required Secrets:

1. **GITHUB_TOKEN** (Required)
   - Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
   - Generate a new token with the following scopes:
     - `repo` (Full control of private repositories)
     - `read:user` (Read user profile data)
   - Copy the token and add it as a secret named `GITHUB_TOKEN`

#### Optional Secrets:

2. **LEETCODE_USERNAME** (Optional)
   - Your LeetCode username (e.g., `your-leetcode-username`)
   - If not provided, LeetCode stats will be skipped

3. **HACKERRANK_USERNAME** (Optional)
   - Your HackerRank username (e.g., `your-hackerrank-username`)
   - If not provided, HackerRank stats will be skipped

### Step 3: File Structure

Ensure your repository has the following structure:

```
your-username/
├── .github/
│   └── workflows/
│       └── update-readme.yml
├── scripts/
│   └── update_readme.py
├── README.md
└── (other files...)
```

### Step 4: Customize Your README.md

1. **Update Personal Information**: Edit the README.md file to include your personal details
2. **Verify Placeholders**: Ensure the following comment blocks exist in your README.md:

```markdown
<!-- GITHUB_STATS_START -->
<!-- GITHUB_STATS_END -->

<!-- LEETCODE_STATS_START -->
<!-- LEETCODE_STATS_END -->

<!-- HACKERRANK_STATS_START -->
<!-- HACKERRANK_STATS_END -->
```

### Step 5: Test the Setup

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

### Customizing Stats Display

Edit `scripts/update_readme.py` to customize:

- **Language Count**: Change the number of top languages displayed
- **Stat Formatting**: Modify how numbers are formatted (commas, etc.)
- **Additional Metrics**: Add new GitHub API endpoints for more stats

## API Rate Limits and Considerations

### GitHub API
- **Rate Limit**: 5,000 requests per hour for authenticated requests
- **Best Practice**: The script includes rate limiting delays
- **Fallback**: Failed requests return default values

### LeetCode API
- **Rate Limit**: No official limit, but includes delays to be respectful
- **Method**: Uses GraphQL API for accurate data
- **Fallback**: Returns empty stats if user not found

### HackerRank API
- **Method**: Web scraping (no official API)
- **Rate Limit**: Includes delays to avoid being blocked
- **Fallback**: Returns empty stats if profile inaccessible

## Troubleshooting

### Common Issues

#### 1. "GITHUB_TOKEN not found" Error
- **Solution**: Ensure you've added the `GITHUB_TOKEN` secret with proper permissions
- **Check**: Token must have `repo` and `read:user` scopes

#### 2. "Permission denied" Error
- **Solution**: Check repository permissions and GitHub Actions settings
- **Verify**: Repository settings → Actions → General → Workflow permissions

#### 3. LeetCode/HackerRank Stats Not Updating
- **Solution**: Verify usernames are correct and profiles are public
- **Check**: Test usernames manually in browser

#### 4. README Not Committing
- **Solution**: Ensure the workflow has write permissions
- **Check**: The git config and push steps in the workflow

#### 5. Rate Limiting Issues
- **Solution**: The script includes built-in delays, but you can increase them
- **Modify**: Add longer `time.sleep()` values in the Python script

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
   pip install requests beautifulsoup4 matplotlib seaborn pillow

   # Set environment variables
   export GITHUB_TOKEN="your_token"
   export GITHUB_USERNAME="your_username"
   export LEETCODE_USERNAME="your_leetcode_username"
   export HACKERRANK_USERNAME="your_hackerrank_username"

   # Run script
   python scripts/update_readme.py
   ```

## Security Considerations

1. **Token Security**: Never expose your GitHub token in code or logs
2. **Minimal Permissions**: Use tokens with only necessary scopes
3. **Regular Rotation**: Consider rotating tokens periodically
4. **Secret Management**: Use GitHub Secrets, never commit tokens to repository

## Customization Examples

### Adding New GitHub Stats

```python
# In GitHubStatsCollector class
def get_total_followers(self) -> int:
    """Get total followers count"""
    user_info = self.get_user_info()
    return user_info.get('followers', 0)

# In main() function
github_stats['followers'] = github_collector.get_total_followers()
```

### Modifying README Template

```python
# In READMEUpdater._replace_stats()
github_section = f"""- 🔥 **Total Commits:** {github_stats.get('total_commits', 0):,}
- ⭐ **Total Stars:** {github_stats.get('total_stars', 0):,}
- 👥 **Followers:** {github_stats.get('followers', 0):,}
- 📚 **Top Languages:** {languages_str}"""
```

## Support and Contribution

### Getting Help
- Check the [GitHub Issues](../../issues) for known problems
- Create a new issue with detailed error logs
- Include your workflow run logs and error messages

### Contributing
- Fork the repository and create a feature branch
- Test your changes thoroughly
- Submit a pull request with detailed description

## License

This project is open source and available under the [MIT License](LICENSE).

---

**Note**: This system respects the terms of service of all platforms (GitHub, LeetCode, HackerRank) and includes appropriate rate limiting and error handling.