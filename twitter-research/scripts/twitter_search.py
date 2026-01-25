#!/usr/bin/env python3
"""
Twitter Search CLI using RapidAPI Twitter241

A clean CLI interface for Twitter search that abstracts away query syntax.
Requires RAPIDAPI_KEY_241 environment variable.

Examples:
    # Search for keywords
    python twitter_search.py search "artificial intelligence"
    
    # Search with filters
    python twitter_search.py search "AI" --from elonmusk --min-likes 100 --no-retweets
    
    # Get user profile
    python twitter_search.py user naval
    
    # Get user's tweets
    python twitter_search.py tweets karpathy --limit 50 --no-replies
    
    # Find popular tweets on a topic
    python twitter_search.py search "startup funding" --min-likes 500 --has-links --lang en
"""

import argparse
import csv
import io
import json
import os
import sys
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from typing import Optional
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

# Load environment variables from .env file if it exists
try:
    from pathlib import Path
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ.setdefault(key.strip(), value.strip())
except Exception:
    pass


RAPIDAPI_HOST = "twitter241.p.rapidapi.com"
RAPIDAPI_URL = f"https://{RAPIDAPI_HOST}"


@dataclass
class TwitterUser:
    id: str
    username: str
    display_name: str
    followers_count: int
    description: str = ""
    profile_image_url: str = ""

    @property
    def url(self) -> str:
        return f"https://twitter.com/{self.username}"


@dataclass
class TwitterTweet:
    id: str
    text: str
    created_at: str
    username: str
    display_name: str
    like_count: int
    retweet_count: int
    reply_count: int
    view_count: Optional[int] = None
    is_retweet: bool = False
    is_reply: bool = False
    is_quote: bool = False
    media_urls: list = None

    def __post_init__(self):
        if self.media_urls is None:
            self.media_urls = []

    @property
    def url(self) -> str:
        return f"https://twitter.com/{self.username}/status/{self.id}"


class QueryBuilder:
    """Builds Twitter search queries from CLI parameters"""

    def __init__(self):
        self.parts = []

    def add_keywords(self, keywords: str):
        if keywords:
            self.parts.append(keywords)
        return self

    def add_from_user(self, username: str):
        if username:
            self.parts.append(f"from:{username}")
        return self

    def add_to_user(self, username: str):
        if username:
            self.parts.append(f"to:{username}")
        return self

    def add_mention(self, username: str):
        if username:
            self.parts.append(f"@{username}")
        return self

    def add_hashtag(self, tag: str):
        if tag:
            # Remove # if user included it
            tag = tag.lstrip("#")
            self.parts.append(f"#{tag}")
        return self

    def add_min_likes(self, count: int):
        if count and count > 0:
            self.parts.append(f"min_faves:{count}")
        return self

    def add_min_retweets(self, count: int):
        if count and count > 0:
            self.parts.append(f"min_retweets:{count}")
        return self

    def add_min_replies(self, count: int):
        if count and count > 0:
            self.parts.append(f"min_replies:{count}")
        return self

    def add_since(self, date: str):
        if date:
            self.parts.append(f"since:{date}")
        return self

    def add_until(self, date: str):
        if date:
            self.parts.append(f"until:{date}")
        return self

    def add_language(self, lang: str):
        if lang:
            self.parts.append(f"lang:{lang}")
        return self

    def exclude_retweets(self):
        self.parts.append("-filter:retweets")
        return self

    def exclude_replies(self):
        self.parts.append("-filter:replies")
        return self

    def only_replies(self):
        self.parts.append("filter:replies")
        return self

    def has_media(self):
        self.parts.append("filter:media")
        return self

    def has_images(self):
        self.parts.append("filter:images")
        return self

    def has_videos(self):
        self.parts.append("filter:videos")
        return self

    def has_links(self):
        self.parts.append("filter:links")
        return self

    def add_url_domain(self, domain: str):
        if domain:
            self.parts.append(f"url:{domain}")
        return self

    def add_exclude_word(self, word: str):
        if word:
            self.parts.append(f"-{word}")
        return self

    def build(self) -> str:
        return " ".join(self.parts)


class Twitter241Client:
    """Python client for twitter241.p.rapidapi.com"""

    def __init__(self, api_key: Optional[str] = None, verbose: bool = False):
        self.api_key = api_key or os.environ.get("RAPIDAPI_KEY_241")
        if not self.api_key:
            raise ValueError("RAPIDAPI_KEY_241 environment variable required")
        self.verbose = verbose

    def _log(self, msg: str):
        if self.verbose:
            print(f"[twitter] {msg}", file=sys.stderr)

    def _fetch(self, endpoint: str, params: dict = None) -> dict:
        """Make API request with retry logic"""
        url = f"{RAPIDAPI_URL}{endpoint}"
        if params:
            url = f"{url}?{urlencode(params)}"

        headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": RAPIDAPI_HOST,
        }

        max_retries = 5
        last_error = None

        for attempt in range(max_retries + 1):
            if attempt > 0:
                delay = min(1 * (2 ** (attempt - 1)), 16)
                self._log(f"Rate limited, waiting {delay}s (retry {attempt}/{max_retries})")
                time.sleep(delay)

            try:
                self._log(f"Fetching: {endpoint}")
                req = Request(url, headers=headers)
                with urlopen(req, timeout=30) as response:
                    return json.loads(response.read().decode())
            except HTTPError as e:
                if e.code == 429:
                    last_error = e
                    continue
                raise RuntimeError(f"API error: {e.code} {e.reason}")
            except URLError as e:
                raise RuntimeError(f"Network error: {e.reason}")

        raise RuntimeError(f"Max retries exceeded: {last_error}")

    def get_user(self, username: str) -> TwitterUser:
        """Get user profile by username"""
        data = self._fetch("/user", {"username": username})

        try:
            user = data["result"]["data"]["user"]["result"]
            return TwitterUser(
                id=user["rest_id"],
                username=user["core"]["screen_name"],
                display_name=user["core"]["name"],
                profile_image_url=user.get("avatar", {}).get("image_url", ""),
                followers_count=user["legacy"]["followers_count"],
                description=user["legacy"].get("description", ""),
            )
        except (KeyError, TypeError) as e:
            raise RuntimeError(f"User not found: @{username}") from e

    def _search_page(self, query: str, cursor: str = None) -> tuple[list[TwitterTweet], Optional[str]]:
        """Execute single search page, returns (tweets, next_cursor)"""
        params = {"query": query, "type": "Latest"}
        if cursor:
            params["cursor"] = cursor

        data = self._fetch("/search", params)
        tweets = []
        next_cursor = None

        # Check top-level cursor
        if "cursor" in data and data["cursor"].get("bottom"):
            next_cursor = data["cursor"]["bottom"]

        # Parse timeline instructions
        try:
            instructions = data["result"]["timeline"]["instructions"]
        except (KeyError, TypeError):
            return tweets, None

        for instruction in instructions:
            if instruction.get("type") != "TimelineAddEntries":
                continue

            for entry in instruction.get("entries", []):
                entry_id = entry.get("entryId", "")

                if entry_id.startswith("cursor-bottom"):
                    next_cursor = entry.get("content", {}).get("value")
                    continue

                tweet = self._extract_tweet(entry.get("content"))
                if tweet:
                    tweets.append(tweet)

        return tweets, next_cursor

    def search(self, query: str, limit: int = 20) -> list[TwitterTweet]:
        """
        Search tweets with automatic pagination.
        
        Args:
            query: Built query string with operators
            limit: Maximum tweets to return (handles pagination internally)
        
        Returns:
            List of tweets up to limit
        """
        all_tweets = []
        cursor = None
        page = 0

        while len(all_tweets) < limit:
            page += 1
            self._log(f"Fetching page {page}...")
            
            tweets, next_cursor = self._search_page(query, cursor)

            if not tweets:
                self._log("No more tweets found")
                break

            all_tweets.extend(tweets)
            self._log(f"Got {len(tweets)} tweets (total: {len(all_tweets)})")

            if not next_cursor:
                self._log("No more pages")
                break

            cursor = next_cursor
            
            # Rate limiting between pages
            if len(all_tweets) < limit:
                time.sleep(1)

        return all_tweets[:limit]

    def _extract_tweet(self, content: dict) -> Optional[TwitterTweet]:
        """Extract tweet from timeline entry content"""
        try:
            if content.get("__typename") != "TimelineTimelineItem":
                return None

            item_content = content.get("itemContent", {})
            tweet_result = item_content.get("tweet_results", {}).get("result")

            if not tweet_result:
                return None

            legacy = tweet_result["legacy"]
            user_result = tweet_result["core"]["user_results"]["result"]
            user_core = user_result.get("core", {})
            user_legacy = user_result.get("legacy", {})

            view_count = None
            views = tweet_result.get("views", {})
            if views.get("count"):
                try:
                    view_count = int(views["count"])
                except ValueError:
                    pass

            media_urls = []
            entities = legacy.get("extended_entities") or legacy.get("entities", {})
            for media in entities.get("media", []):
                if media.get("type") == "photo" and media.get("media_url_https"):
                    url = media["media_url_https"]
                    if "?" not in url:
                        ext_match = url.rsplit(".", 1)
                        if len(ext_match) == 2:
                            url = f"{ext_match[0]}?format={ext_match[1]}&name=large"
                    media_urls.append(url)

            return TwitterTweet(
                id=legacy["id_str"],
                text=legacy["full_text"],
                created_at=legacy["created_at"],
                username=user_core.get("screen_name", "unknown"),
                display_name=user_core.get("name", user_legacy.get("name", "Unknown")),
                like_count=legacy.get("favorite_count", 0),
                retweet_count=legacy.get("retweet_count", 0),
                reply_count=legacy.get("reply_count", 0),
                view_count=view_count,
                is_retweet=legacy["full_text"].startswith("RT @"),
                is_reply=bool(legacy.get("in_reply_to_status_id_str")),
                is_quote=legacy.get("is_quote_status", False),
                media_urls=media_urls,
            )
        except (KeyError, TypeError):
            return None


# ============================================================================
# Output Formatting
# ============================================================================

def format_tweet_xml(tweet: TwitterTweet, index: int) -> str:
    """Format tweet as XML for structured output"""
    flags = []
    if tweet.is_reply:
        flags.append("reply")
    if tweet.is_retweet:
        flags.append("retweet")
    if tweet.is_quote:
        flags.append("quote")
    
    # Escape XML special chars in text
    text = tweet.text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    
    lines = [
        f'<tweet index="{index}" id="{tweet.id}">',
        f'  <author username="{tweet.username}">{tweet.display_name}</author>',
        f'  <date>{tweet.created_at}</date>',
        f'  <content>{text}</content>',
        f'  <metrics likes="{tweet.like_count}" retweets="{tweet.retweet_count}" replies="{tweet.reply_count}"' +
        (f' views="{tweet.view_count}"' if tweet.view_count else '') + ' />',
    ]
    
    if flags:
        lines.append(f'  <type>{", ".join(flags)}</type>')
    
    if tweet.media_urls:
        lines.append(f'  <media count="{len(tweet.media_urls)}" />')
    
    lines.append(f'  <url>{tweet.url}</url>')
    lines.append('</tweet>')
    
    return "\n".join(lines)


def format_user_xml(user: TwitterUser) -> str:
    """Format user as XML for structured output"""
    desc = (user.description or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    
    return "\n".join([
        f'<user id="{user.id}" username="{user.username}">',
        f'  <display_name>{user.display_name}</display_name>',
        f'  <followers>{user.followers_count}</followers>',
        f'  <bio>{desc}</bio>',
        f'  <url>{user.url}</url>',
        '</user>',
    ])


def compute_summary(tweets: list[TwitterTweet]) -> dict:
    """Compute summary statistics for tweets"""
    if not tweets:
        return {}
    
    total_likes = sum(t.like_count for t in tweets)
    total_retweets = sum(t.retweet_count for t in tweets)
    total_replies = sum(t.reply_count for t in tweets)
    
    # Unique authors
    authors = {}
    for t in tweets:
        if t.username not in authors:
            authors[t.username] = {"count": 0, "likes": 0}
        authors[t.username]["count"] += 1
        authors[t.username]["likes"] += t.like_count
    
    # Top authors by tweet count
    top_authors = sorted(authors.items(), key=lambda x: x[1]["likes"], reverse=True)[:5]
    
    # Count types
    original_count = sum(1 for t in tweets if not t.is_retweet and not t.is_reply and not t.is_quote)
    reply_count = sum(1 for t in tweets if t.is_reply)
    retweet_count = sum(1 for t in tweets if t.is_retweet)
    quote_count = sum(1 for t in tweets if t.is_quote)
    with_media = sum(1 for t in tweets if t.media_urls)
    
    return {
        "total": len(tweets),
        "total_likes": total_likes,
        "total_retweets": total_retweets,
        "total_replies": total_replies,
        "avg_likes": total_likes / len(tweets),
        "unique_authors": len(authors),
        "top_authors": top_authors,
        "original_tweets": original_count,
        "replies": reply_count,
        "retweets": retweet_count,
        "quotes": quote_count,
        "with_media": with_media,
    }


def format_summary_xml(summary: dict, query: str = "") -> str:
    """Format summary statistics as XML"""
    lines = [
        '<summary>',
        f'  <query>{query}</query>' if query else '',
        f'  <total_tweets>{summary["total"]}</total_tweets>',
        f'  <unique_authors>{summary["unique_authors"]}</unique_authors>',
        f'  <engagement likes="{summary["total_likes"]}" retweets="{summary["total_retweets"]}" replies="{summary["total_replies"]}" />',
        f'  <avg_likes>{summary["avg_likes"]:.1f}</avg_likes>',
        f'  <breakdown original="{summary["original_tweets"]}" replies="{summary["replies"]}" retweets="{summary["retweets"]}" quotes="{summary["quotes"]}" with_media="{summary["with_media"]}" />',
        '  <top_authors>',
    ]
    
    for username, stats in summary["top_authors"]:
        lines.append(f'    <author username="{username}" tweets="{stats["count"]}" total_likes="{stats["likes"]}" />')
    
    lines.extend([
        '  </top_authors>',
        '</summary>',
    ])
    
    return "\n".join(line for line in lines if line)


def output_tweets(tweets: list[TwitterTweet], fmt: str, query: str = ""):
    """Output tweets in specified format"""
    if not tweets:
        print("<results><summary><total_tweets>0</total_tweets></summary></results>")
        return

    if fmt == "json":
        summary = compute_summary(tweets)
        data = {
            "summary": {
                "query": query,
                "total": summary["total"],
                "unique_authors": summary["unique_authors"],
                "total_likes": summary["total_likes"],
                "total_retweets": summary["total_retweets"],
                "avg_likes": round(summary["avg_likes"], 1),
                "breakdown": {
                    "original": summary["original_tweets"],
                    "replies": summary["replies"],
                    "retweets": summary["retweets"],
                    "quotes": summary["quotes"],
                    "with_media": summary["with_media"],
                },
                "top_authors": [
                    {"username": u, "tweets": s["count"], "total_likes": s["likes"]}
                    for u, s in summary["top_authors"]
                ],
            },
            "tweets": [],
        }
        for t in tweets:
            d = asdict(t)
            d["url"] = t.url
            data["tweets"].append(d)
        print(json.dumps(data, indent=2))

    elif fmt == "csv":
        output = io.StringIO()
        fieldnames = [
            "id", "username", "display_name", "text", "created_at",
            "like_count", "retweet_count", "reply_count", "view_count",
            "is_retweet", "is_reply", "is_quote", "url"
        ]
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        for tweet in tweets:
            row = asdict(tweet)
            row["url"] = tweet.url
            del row["media_urls"]
            writer.writerow(row)
        print(output.getvalue())

    else:  # text (XML format for Claude)
        summary = compute_summary(tweets)
        
        print("<results>")
        print(format_summary_xml(summary, query))
        print("<tweets>")
        for i, tweet in enumerate(tweets, 1):
            print(format_tweet_xml(tweet, i))
        print("</tweets>")
        print("</results>")


def output_user(user: TwitterUser, fmt: str):
    """Output user in specified format"""
    if fmt == "json":
        d = asdict(user)
        d["url"] = user.url
        print(json.dumps(d, indent=2))
    else:
        print(format_user_xml(user))


# ============================================================================
# CLI Commands
# ============================================================================

def cmd_search(args, client: Twitter241Client):
    """Execute search command"""
    builder = QueryBuilder()
    
    # Keywords (required positional arg)
    builder.add_keywords(args.keywords)
    
    # User filters
    if args.from_user:
        builder.add_from_user(args.from_user)
    if args.to_user:
        builder.add_to_user(args.to_user)
    if args.mention:
        builder.add_mention(args.mention)
    
    # Content filters
    if args.hashtag:
        for tag in args.hashtag:
            builder.add_hashtag(tag)
    if args.exclude:
        for word in args.exclude:
            builder.add_exclude_word(word)
    
    # Engagement filters
    if args.min_likes:
        builder.add_min_likes(args.min_likes)
    if args.min_retweets:
        builder.add_min_retweets(args.min_retweets)
    if args.min_replies:
        builder.add_min_replies(args.min_replies)
    
    # Date filters
    if args.since:
        builder.add_since(args.since)
    if args.until:
        builder.add_until(args.until)
    if args.days:
        since_date = (datetime.now() - timedelta(days=args.days)).strftime("%Y-%m-%d")
        builder.add_since(since_date)
    
    # Type filters
    if args.no_retweets:
        builder.exclude_retweets()
    if args.no_replies:
        builder.exclude_replies()
    if args.only_replies:
        builder.only_replies()
    
    # Media filters
    if args.has_media:
        builder.has_media()
    if args.has_images:
        builder.has_images()
    if args.has_videos:
        builder.has_videos()
    if args.has_links:
        builder.has_links()
    if args.url:
        builder.add_url_domain(args.url)
    
    # Language
    if args.lang:
        builder.add_language(args.lang)
    
    query = builder.build()
    
    if args.verbose:
        print(f"[query] {query}", file=sys.stderr)
    
    tweets = client.search(query, limit=args.limit)
    output_tweets(tweets, args.format, query=query)


def cmd_user(args, client: Twitter241Client):
    """Execute user lookup command"""
    user = client.get_user(args.username)
    output_user(user, args.format)


def cmd_tweets(args, client: Twitter241Client):
    """Execute user tweets command"""
    builder = QueryBuilder()
    builder.add_from_user(args.username)
    
    if args.no_retweets:
        builder.exclude_retweets()
    if args.no_replies:
        builder.exclude_replies()
    if args.only_replies:
        builder.only_replies()
    if args.since:
        builder.add_since(args.since)
    if args.until:
        builder.add_until(args.until)
    if args.days:
        since_date = (datetime.now() - timedelta(days=args.days)).strftime("%Y-%m-%d")
        builder.add_since(since_date)
    
    query = builder.build()
    
    if args.verbose:
        print(f"[query] {query}", file=sys.stderr)
    
    tweets = client.search(query, limit=args.limit)
    output_tweets(tweets, args.format, query=query)


# ============================================================================
# Main
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Twitter Search CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Show debug output")
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # -------------------------------------------------------------------------
    # search command
    # -------------------------------------------------------------------------
    search_parser = subparsers.add_parser(
        "search",
        help="Search tweets",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Search tweets with filters",
        epilog="""
Examples:
  %(prog)s "artificial intelligence"
  %(prog)s "AI" --from elonmusk --min-likes 100
  %(prog)s "startup" --min-likes 500 --no-retweets --days 7
  %(prog)s "python" --has-links --lang en --limit 50
        """,
    )
    search_parser.add_argument("keywords", nargs="?", default="", help="Search keywords or phrase")
    
    # User filters
    user_group = search_parser.add_argument_group("user filters")
    user_group.add_argument("--from", dest="from_user", metavar="USER", help="Tweets from this user")
    user_group.add_argument("--to", dest="to_user", metavar="USER", help="Replies to this user")
    user_group.add_argument("--mention", metavar="USER", help="Tweets mentioning this user")
    
    # Content filters
    content_group = search_parser.add_argument_group("content filters")
    content_group.add_argument("--hashtag", "-t", action="append", metavar="TAG", help="Include hashtag (can repeat)")
    content_group.add_argument("--exclude", "-x", action="append", metavar="WORD", help="Exclude word (can repeat)")
    
    # Engagement filters
    engage_group = search_parser.add_argument_group("engagement filters")
    engage_group.add_argument("--min-likes", type=int, metavar="N", help="Minimum likes")
    engage_group.add_argument("--min-retweets", type=int, metavar="N", help="Minimum retweets")
    engage_group.add_argument("--min-replies", type=int, metavar="N", help="Minimum replies")
    
    # Date filters
    date_group = search_parser.add_argument_group("date filters")
    date_group.add_argument("--since", metavar="YYYY-MM-DD", help="Tweets after this date")
    date_group.add_argument("--until", metavar="YYYY-MM-DD", help="Tweets before this date")
    date_group.add_argument("--days", type=int, metavar="N", help="Tweets from last N days")
    
    # Type filters
    type_group = search_parser.add_argument_group("tweet type filters")
    type_group.add_argument("--no-retweets", action="store_true", help="Exclude retweets")
    type_group.add_argument("--no-replies", action="store_true", help="Exclude replies")
    type_group.add_argument("--only-replies", action="store_true", help="Only replies")
    
    # Media filters
    media_group = search_parser.add_argument_group("media filters")
    media_group.add_argument("--has-media", action="store_true", help="Has any media")
    media_group.add_argument("--has-images", action="store_true", help="Has images")
    media_group.add_argument("--has-videos", action="store_true", help="Has videos")
    media_group.add_argument("--has-links", action="store_true", help="Has links")
    media_group.add_argument("--url", metavar="DOMAIN", help="Links to this domain")
    
    # Other
    other_group = search_parser.add_argument_group("other options")
    other_group.add_argument("--lang", metavar="CODE", help="Language code (e.g., en, es, ja)")
    other_group.add_argument("--limit", type=int, default=20, help="Max results (default: 20)")
    other_group.add_argument("--format", "-f", choices=["text", "json", "csv"], default="text", help="Output format")
    
    # -------------------------------------------------------------------------
    # user command
    # -------------------------------------------------------------------------
    user_parser = subparsers.add_parser("user", help="Get user profile")
    user_parser.add_argument("username", help="Twitter username (without @)")
    user_parser.add_argument("--format", "-f", choices=["text", "json"], default="text", help="Output format")
    
    # -------------------------------------------------------------------------
    # tweets command
    # -------------------------------------------------------------------------
    tweets_parser = subparsers.add_parser(
        "tweets",
        help="Get user's tweets",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s naval
  %(prog)s karpathy --no-retweets --no-replies --limit 50
  %(prog)s elonmusk --days 7 --format json
        """,
    )
    tweets_parser.add_argument("username", help="Twitter username (without @)")
    tweets_parser.add_argument("--no-retweets", action="store_true", help="Exclude retweets")
    tweets_parser.add_argument("--no-replies", action="store_true", help="Exclude replies")
    tweets_parser.add_argument("--only-replies", action="store_true", help="Only replies")
    tweets_parser.add_argument("--since", metavar="YYYY-MM-DD", help="Tweets after this date")
    tweets_parser.add_argument("--until", metavar="YYYY-MM-DD", help="Tweets before this date")
    tweets_parser.add_argument("--days", type=int, metavar="N", help="Tweets from last N days")
    tweets_parser.add_argument("--limit", type=int, default=20, help="Max results (default: 20)")
    tweets_parser.add_argument("--format", "-f", choices=["text", "json", "csv"], default="text", help="Output format")
    
    # -------------------------------------------------------------------------
    # Parse and execute
    # -------------------------------------------------------------------------
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        client = Twitter241Client(verbose=args.verbose)
        
        if args.command == "search":
            cmd_search(args, client)
        elif args.command == "user":
            cmd_user(args, client)
        elif args.command == "tweets":
            cmd_tweets(args, client)
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
