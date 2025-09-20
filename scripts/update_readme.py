#!/usr/bin/env python3
"""
GitHub Profile README Stats Updater
====================================

This script fetches stats from GitHub, LeetCode, and HackerRank
and updates the README.md file with the latest information.

Requirements:
- GITHUB_TOKEN: Personal access token with repo scope
- LEETCODE_USERNAME: Your LeetCode username
- HACKERRANK_USERNAME: Your HackerRank username
- GITHUB_USERNAME: Your GitHub username (auto-populated in workflow)
"""

import os
import re
import json
import time
import logging
import requests
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class GitHubStatsCollector:
    """Collects GitHub statistics using the GitHub API"""
    
    def __init__(self, token: str, username: str):
        self.token = token
        self.username = username
        self.headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def _make_request(self, url: str, params: Dict = None) -> Optional[Dict]:
        """Make a request to the GitHub API with error handling"""
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed for {url}: {e}")
            return None
    
    def get_user_info(self) -> Dict:
        """Get basic user information"""
        logger.info("Fetching user information...")
        url = f"https://api.github.com/users/{self.username}"
        return self._make_request(url) or {}
    
    def get_repositories(self) -> List[Dict]:
        """Get all repositories for the user"""
        logger.info("Fetching repositories...")
        repos = []
        page = 1
        
        while True:
            url = f"https://api.github.com/users/{self.username}/repos"
            params = {
                'page': page,
                'per_page': 100,
                'type': 'all',
                'sort': 'updated'
            }
            
            data = self._make_request(url, params)
            if not data:
                break
                
            repos.extend(data)
            
            if len(data) < 100:  # Last page
                break
                
            page += 1
            time.sleep(0.1)  # Rate limiting
        
        logger.info(f"Found {len(repos)} repositories")
        return repos
    
    def get_total_commits(self) -> int:
        """Get total commit count across all repositories"""
        logger.info("Calculating total commits...")
        repos = self.get_repositories()
        total_commits = 0
        
        for repo in repos:
            if repo['fork']:  # Skip forked repositories
                continue
                
            # Get commits for this repository
            url = f"https://api.github.com/repos/{self.username}/{repo['name']}/commits"
            params = {
                'author': self.username,
                'per_page': 1
            }
            
            try:
                response = self.session.get(url, params=params)
                if response.status_code == 200:
                    # Get total count from Link header
                    link_header = response.headers.get('Link', '')
                    if 'rel="last"' in link_header:
                        last_page = re.search(r'page=(\d+).*rel="last"', link_header)
                        if last_page:
                            total_commits += int(last_page.group(1))
                    else:
                        # If no pagination, count the commits directly
                        commits = response.json()
                        if commits:
                            total_commits += len(commits)
            except Exception as e:
                logger.warning(f"Could not get commits for {repo['name']}: {e}")
                continue
            
            time.sleep(0.1)  # Rate limiting
        
        logger.info(f"Total commits: {total_commits}")
        return total_commits
    
    def get_total_stars(self) -> int:
        """Get total stars across all repositories"""
        logger.info("Calculating total stars...")
        repos = self.get_repositories()
        total_stars = sum(repo['stargazers_count'] for repo in repos if not repo['fork'])
        logger.info(f"Total stars: {total_stars}")
        return total_stars
    
    def get_language_stats(self) -> Dict[str, int]:
        """Get programming language statistics"""
        logger.info("Analyzing language usage...")
        repos = self.get_repositories()
        language_stats = {}
        
        for repo in repos:
            if repo['fork'] or not repo['language']:
                continue
                
            # Get detailed language stats for this repo
            url = f"https://api.github.com/repos/{self.username}/{repo['name']}/languages"
            languages = self._make_request(url)
            
            if languages:
                for lang, bytes_count in languages.items():
                    language_stats[lang] = language_stats.get(lang, 0) + bytes_count
            
            time.sleep(0.1)  # Rate limiting
        
        # Sort by usage
        sorted_languages = dict(sorted(language_stats.items(), key=lambda x: x[1], reverse=True))
        logger.info(f"Found {len(sorted_languages)} languages")
        return sorted_languages
    
    def get_contribution_streak(self) -> int:
        """Get current contribution streak (simplified version)"""
        logger.info("Calculating contribution streak...")
        # Note: This would require scraping the contribution graph or using GitHub GraphQL API
        # For now, return a placeholder
        return 0


class LeetCodeStatsCollector:
    """Collects LeetCode statistics"""
    
    def __init__(self, username: str):
        self.username = username
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def get_stats(self) -> Dict:
        """Get LeetCode statistics"""
        logger.info(f"Fetching LeetCode stats for {self.username}...")
        
        try:
            # LeetCode GraphQL endpoint
            url = "https://leetcode.com/graphql"
            query = {
                "query": """
                query getUserProfile($username: String!) {
                    matchedUser(username: $username) {
                        username
                        submitStats: submitStatsGlobal {
                            acSubmissionNum {
                                difficulty
                                count
                                submissions
                            }
                        }
                        profile {
                            ranking
                            userAvatar
                            realName
                            aboutMe
                            school
                            websites
                            countryName
                            company
                            jobTitle
                            skillTags
                            postViewCount
                            postViewCountDiff
                            reputation
                            reputationDiff
                            solutionCount
                            solutionCountDiff
                            categoryDiscussCount
                            categoryDiscussCountDiff
                        }
                    }
                }
                """,
                "variables": {"username": self.username}
            }
            
            response = self.session.post(url, json=query)
            response.raise_for_status()
            data = response.json()
            
            if 'data' in data and data['data']['matchedUser']:
                user_data = data['data']['matchedUser']
                
                # Parse submission stats
                total_solved = 0
                easy_solved = 0
                medium_solved = 0
                hard_solved = 0
                
                for stat in user_data['submitStats']['acSubmissionNum']:
                    if stat['difficulty'] == 'All':
                        total_solved = stat['count']
                    elif stat['difficulty'] == 'Easy':
                        easy_solved = stat['count']
                    elif stat['difficulty'] == 'Medium':
                        medium_solved = stat['count']
                    elif stat['difficulty'] == 'Hard':
                        hard_solved = stat['count']
                
                stats = {
                    'total_solved': total_solved,
                    'easy_solved': easy_solved,
                    'medium_solved': medium_solved,
                    'hard_solved': hard_solved,
                    'ranking': user_data['profile']['ranking'] if user_data['profile'] else None
                }
                
                logger.info(f"LeetCode stats: {stats}")
                return stats
            else:
                logger.warning("No LeetCode data found for user")
                return {}
                
        except Exception as e:
            logger.error(f"Failed to fetch LeetCode stats: {e}")
            return {}


class HackerRankStatsCollector:
    """Collects HackerRank statistics"""
    
    def __init__(self, username: str):
        self.username = username
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def get_stats(self) -> Dict:
        """Get HackerRank statistics by scraping profile page"""
        logger.info(f"Fetching HackerRank stats for {self.username}...")
        
        try:
            url = f"https://www.hackerrank.com/profile/{self.username}"
            response = self.session.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            stats = {
                'badges': 0,
                'points': 0,
                'rank': None,
                'skills': []
            }
            
            # Try to extract badges count
            badge_elements = soup.find_all('div', class_='badge-item')
            stats['badges'] = len(badge_elements)
            
            # Try to extract rank and points from various selectors
            rank_element = soup.find('div', class_='profile-rank')
            if rank_element:
                rank_text = rank_element.get_text(strip=True)
                # Extract rank number if present
                rank_match = re.search(r'#(\d+)', rank_text)
                if rank_match:
                    stats['rank'] = int(rank_match.group(1))
            
            # Extract skills
            skill_elements = soup.find_all('div', class_='skill-item') or soup.find_all('span', class_='skill-name')
            stats['skills'] = [skill.get_text(strip=True) for skill in skill_elements[:5]]  # Top 5 skills
            
            logger.info(f"HackerRank stats: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"Failed to fetch HackerRank stats: {e}")
            return {}


class READMEUpdater:
    """Updates the README.md file with collected statistics"""
    
    def __init__(self, readme_path: str = "README.md"):
        self.readme_path = readme_path
    
    def update_readme(self, github_stats: Dict, leetcode_stats: Dict, hackerrank_stats: Dict):
        """Update README.md with new statistics"""
        logger.info("Updating README.md...")
        
        # Read current README
        try:
            with open(self.readme_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except FileNotFoundError:
            logger.info("README.md not found, creating new one...")
            content = self._get_template_content()
        
        # Update statistics
        updated_content = self._replace_stats(content, github_stats, leetcode_stats, hackerrank_stats)
        
        # Write updated content
        with open(self.readme_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        logger.info("README.md updated successfully!")
    
    def _get_template_content(self) -> str:
        """Get template README content"""
        username = os.getenv('GITHUB_USERNAME', 'your-username')
        
        return f"""# Hi there, I'm {username}! 👋

[![Typing SVG](https://readme-typing-svg.herokuapp.com?font=Fira+Code&pause=1000&color=36BCF7&width=435&lines=Full+Stack+Developer;Open+Source+Enthusiast;Problem+Solver;Always+Learning)](https://git.io/typing-svg)

## 📊 GitHub Statistics

<!-- GITHUB_STATS_START -->
- 🔥 **Total Commits:** 0
- ⭐ **Total Stars:** 0  
- 📚 **Top Languages:** Python, JavaScript, TypeScript
<!-- GITHUB_STATS_END -->

## 🧠 Coding Platforms

### LeetCode 
<!-- LEETCODE_STATS_START -->
- 📈 **Problems Solved:** 0
- 🟢 **Easy:** 0
- 🟡 **Medium:** 0  
- 🔴 **Hard:** 0
- 🏆 **Ranking:** N/A
<!-- LEETCODE_STATS_END -->

### HackerRank
<!-- HACKERRANK_STATS_START -->
- 🏅 **Badges:** 0
- 🎯 **Rank:** N/A
- 💎 **Skills:** Problem Solving, Algorithms
<!-- HACKERRANK_STATS_END -->

## 🛠️ Technologies & Tools

![Python](https://img.shields.io/badge/-Python-3776AB?style=flat&logo=python&logoColor=white)
![JavaScript](https://img.shields.io/badge/-JavaScript-F7DF1E?style=flat&logo=javascript&logoColor=black)
![TypeScript](https://img.shields.io/badge/-TypeScript-3178C6?style=flat&logo=typescript&logoColor=white)
![React](https://img.shields.io/badge/-React-61DAFB?style=flat&logo=react&logoColor=black)
![Node.js](https://img.shields.io/badge/-Node.js-339933?style=flat&logo=node.js&logoColor=white)

## 📈 Contribution Graph

![GitHub Activity Graph](https://github-readme-activity-graph.vercel.app/graph?username={username}&theme=react-dark)

---

*Last updated: {datetime.now().strftime('%B %d, %Y at %I:%M %p UTC')}*

---

<div align="center">

![Profile Views](https://komarev.com/ghpvc/?username={username}&color=blue&style=flat)

</div>
"""
    
    def _replace_stats(self, content: str, github_stats: Dict, leetcode_stats: Dict, hackerrank_stats: Dict) -> str:
        """Replace statistics in README content"""
        
        # Format GitHub stats
        top_languages = list(github_stats.get('languages', {}).keys())[:3]
        languages_str = ', '.join(top_languages) if top_languages else 'Python, JavaScript, TypeScript'
        
        github_section = f"""- 🔥 **Total Commits:** {github_stats.get('total_commits', 0):,}
- ⭐ **Total Stars:** {github_stats.get('total_stars', 0):,}  
- 📚 **Top Languages:** {languages_str}"""
        
        # Format LeetCode stats
        leetcode_section = f"""- 📈 **Problems Solved:** {leetcode_stats.get('total_solved', 0):,}
- 🟢 **Easy:** {leetcode_stats.get('easy_solved', 0):,}
- 🟡 **Medium:** {leetcode_stats.get('medium_solved', 0):,}  
- 🔴 **Hard:** {leetcode_stats.get('hard_solved', 0):,}
- 🏆 **Ranking:** {leetcode_stats.get('ranking', 'N/A')}"""
        
        # Format HackerRank stats
        skills_str = ', '.join(hackerrank_stats.get('skills', ['Problem Solving', 'Algorithms'])[:3])
        hackerrank_section = f"""- 🏅 **Badges:** {hackerrank_stats.get('badges', 0):,}
- 🎯 **Rank:** {hackerrank_stats.get('rank', 'N/A')}
- 💎 **Skills:** {skills_str}"""
        
        # Replace sections using regex
        content = re.sub(
            r'<!-- GITHUB_STATS_START -->.*?<!-- GITHUB_STATS_END -->',
            f'<!-- GITHUB_STATS_START -->\n{github_section}\n<!-- GITHUB_STATS_END -->',
            content,
            flags=re.DOTALL
        )
        
        content = re.sub(
            r'<!-- LEETCODE_STATS_START -->.*?<!-- LEETCODE_STATS_END -->',
            f'<!-- LEETCODE_STATS_START -->\n{leetcode_section}\n<!-- LEETCODE_STATS_END -->',
            content,
            flags=re.DOTALL
        )
        
        content = re.sub(
            r'<!-- HACKERRANK_STATS_START -->.*?<!-- HACKERRANK_STATS_END -->',
            f'<!-- HACKERRANK_STATS_START -->\n{hackerrank_section}\n<!-- HACKERRANK_STATS_END -->',
            content,
            flags=re.DOTALL
        )
        
        # Update timestamp
        content = re.sub(
            r'\*Last updated: .*?\*',
            f'*Last updated: {datetime.now().strftime("%B %d, %Y at %I:%M %p UTC")}*',
            content
        )
        
        return content


def main():
    """Main function to orchestrate the stats collection and README update"""
    logger.info("Starting README stats update...")
    
    # Get environment variables
    github_token = os.getenv('GITHUB_TOKEN')
    github_username = os.getenv('GITHUB_USERNAME')
    leetcode_username = os.getenv('LEETCODE_USERNAME')
    hackerrank_username = os.getenv('HACKERRANK_USERNAME')
    
    if not github_token or not github_username:
        logger.error("GITHUB_TOKEN and GITHUB_USERNAME are required!")
        return
    
    # Collect GitHub stats
    github_collector = GitHubStatsCollector(github_token, github_username)
    github_stats = {
        'total_commits': github_collector.get_total_commits(),
        'total_stars': github_collector.get_total_stars(),
        'languages': github_collector.get_language_stats()
    }
    
    # Collect LeetCode stats
    leetcode_stats = {}
    if leetcode_username:
        leetcode_collector = LeetCodeStatsCollector(leetcode_username)
        leetcode_stats = leetcode_collector.get_stats()
    else:
        logger.warning("LEETCODE_USERNAME not provided, skipping LeetCode stats")
    
    # Collect HackerRank stats  
    hackerrank_stats = {}
    if hackerrank_username:
        hackerrank_collector = HackerRankStatsCollector(hackerrank_username)
        hackerrank_stats = hackerrank_collector.get_stats()
    else:
        logger.warning("HACKERRANK_USERNAME not provided, skipping HackerRank stats")
    
    # Update README
    readme_updater = READMEUpdater()
    readme_updater.update_readme(github_stats, leetcode_stats, hackerrank_stats)
    
    logger.info("README stats update completed successfully!")


if __name__ == '__main__':
    main()