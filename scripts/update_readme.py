#!/usr/bin/env python3
"""
GitHub Profile Stats Logger
====================================

This script fetches stats from LeetCode and HackerRank
and logs them for monitoring purposes.
It also updates the timestamp in the README.md file.

Note: Stats are displayed via embedded cards in README.
This script is for logging and timestamp updates.

Requirements:
- LEETCODE_USERNAME: Your LeetCode username (optional)
- HACKERRANK_USERNAME: Your HackerRank username (optional)
"""

import os
import re
import time
import logging
import requests
from datetime import datetime
from typing import Dict, List, Optional
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

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
                        }
                    }
                }
                """,
                "variables": {"username": self.username}
            }
            
            response = self.session.post(url, json=query, timeout=30)
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
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            stats = {
                'badges': 0,
                'points': 0,
                'rank': None,
                'skills': []
            }
            
            # Try multiple selectors for badges
            badge_selectors = [
                'div.badge-item',
                'div[class*="badge"]',
                '.badge',
                'div[data-test="badge"]',
                '.certificate-item',
                'div[class*="certificate"]'
            ]
            
            for selector in badge_selectors:
                badge_elements = soup.select(selector)
                if badge_elements:
                    stats['badges'] = len(badge_elements)
                    logger.info(f"Found {stats['badges']} badges using selector: {selector}")
                    break
            
            # Try multiple selectors for rank
            rank_selectors = [
                'div.profile-rank',
                'span[class*="rank"]',
                '.rank',
                'div[data-test="rank"]',
                'span[class*="position"]',
                '.position'
            ]
            
            for selector in rank_selectors:
                rank_element = soup.select_one(selector)
                if rank_element:
                    rank_text = rank_element.get_text(strip=True)
                    # Extract rank number if present
                    rank_match = re.search(r'#?(\d+)', rank_text)
                    if rank_match:
                        stats['rank'] = int(rank_match.group(1))
                        logger.info(f"Found rank: {stats['rank']} using selector: {selector}")
                        break
            
            # Try multiple selectors for points
            points_selectors = [
                'div[class*="point"]',
                '.points',
                'span[class*="point"]',
                'div[data-test="points"]',
                '.score'
            ]
            
            for selector in points_selectors:
                points_element = soup.select_one(selector)
                if points_element:
                    points_text = points_element.get_text(strip=True)
                    points_match = re.search(r'(\d+)', points_text)
                    if points_match:
                        stats['points'] = int(points_match.group(1))
                        logger.info(f"Found points: {stats['points']} using selector: {selector}")
                        break
            
            # Try multiple selectors for skills
            skill_selectors = [
                'div.skill-item',
                'span.skill-name',
                'div[class*="skill"]',
                'span[class*="skill"]',
                'div[data-test="skill"]',
                '.skill-tag',
                'div[class*="certificate"]'
            ]
            
            for selector in skill_selectors:
                skill_elements = soup.select(selector)
                if skill_elements:
                    skills = [skill.get_text(strip=True) for skill in skill_elements[:5]]
                    # Filter out empty skills and common non-skill text
                    skills = [skill for skill in skills if skill and len(skill) > 2 and skill not in ['Badges', 'Certificates', 'Skills']]
                    if skills:
                        stats['skills'] = skills
                        logger.info(f"Found skills: {stats['skills']} using selector: {selector}")
                        break
            
            # If no skills found, try to extract from any text that might contain skill names
            if not stats['skills']:
                # Look for common programming languages/technologies
                page_text = soup.get_text().lower()
                common_skills = ['python', 'java', 'javascript', 'c++', 'sql', 'algorithms', 'data structures', 'problem solving']
                found_skills = [skill.title() for skill in common_skills if skill in page_text]
                if found_skills:
                    stats['skills'] = found_skills[:3]
                    logger.info(f"Found skills from page text: {stats['skills']}")
            
            logger.info(f"HackerRank stats: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"Failed to fetch HackerRank stats: {e}")
            return {}


class READMEUpdater:
    """Updates the README.md file with timestamp"""
    
    def __init__(self, readme_path: str = "README.md"):
        self.readme_path = readme_path
    
    def update_readme(self, leetcode_stats: Dict, hackerrank_stats: Dict):
        """Update README.md timestamp"""
        logger.info("Updating README timestamp...")
        
        # Read current README
        try:
            with open(self.readme_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except FileNotFoundError:
            logger.error(f"README.md not found at {self.readme_path}")
            return
        
        # Update timestamp
        current_time = datetime.utcnow().strftime('%B %d, %Y at %I:%M %p UTC')
        updated_content = re.sub(
            r'\*Last updated: .*?\*',
            f'*Last updated: {current_time}*',
            content
        )
        
        # Write updated content if there were changes
        if updated_content != content:
            with open(self.readme_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            logger.info(f"README.md timestamp updated to: {current_time}")
        else:
            logger.info("No timestamp found to update in README.md")
        
        logger.info("LeetCode and HackerRank stats are displayed via embedded cards")
    

def main():
    """Main function to orchestrate the stats collection and README update"""
    logger.info("Starting README stats update...")
    
    # Get environment variables
    leetcode_username = os.getenv('LEETCODE_USERNAME')
    hackerrank_username = os.getenv('HACKERRANK_USERNAME')
    
    # Collect LeetCode stats
    leetcode_stats = {}
    if leetcode_username:
        logger.info(f"Collecting LeetCode stats for user: {leetcode_username}")
        try:
            leetcode_collector = LeetCodeStatsCollector(leetcode_username)
            leetcode_stats = leetcode_collector.get_stats()
            logger.info(f"LeetCode stats collected successfully: {leetcode_stats}")
        except Exception as e:
            logger.error(f"Failed to collect LeetCode stats: {e}")
            leetcode_stats = {}
    else:
        logger.warning("LEETCODE_USERNAME not provided, skipping LeetCode stats")
    
    # Collect HackerRank stats  
    hackerrank_stats = {}
    if hackerrank_username:
        logger.info(f"Collecting HackerRank stats for user: {hackerrank_username}")
        try:
            hackerrank_collector = HackerRankStatsCollector(hackerrank_username)
            hackerrank_stats = hackerrank_collector.get_stats()
            logger.info(f"HackerRank stats collected successfully: {hackerrank_stats}")
        except Exception as e:
            logger.error(f"Failed to collect HackerRank stats: {e}")
            hackerrank_stats = {}
    else:
        logger.warning("HACKERRANK_USERNAME not provided, skipping HackerRank stats")
    
    # Update README
    logger.info("Updating README.md with collected stats...")
    readme_updater = READMEUpdater()
    readme_updater.update_readme(leetcode_stats, hackerrank_stats)
    
    # Summary
    logger.info("=" * 50)
    logger.info("STATS COLLECTION SUMMARY:")
    logger.info(f"LeetCode - Problems: {leetcode_stats.get('total_solved', 0)}")
    logger.info(f"HackerRank - Badges: {hackerrank_stats.get('badges', 0)}")
    logger.info("=" * 50)
    logger.info("README stats update completed successfully!")


if __name__ == '__main__':
    main()