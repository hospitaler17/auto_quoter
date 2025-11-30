import os
from typing import Any, Dict, Optional, Tuple

from src.github.status_client import GitHubStatusClient
from src.parser.site_parser import QuoteParser


def build_parser(config: Dict[str, Any]) -> QuoteParser:
    parser_cfg = config.get('parser') or {}
    return QuoteParser(
        parser_cfg.get('url'),
        parser_cfg.get('quote_selector'),
        parser_cfg.get('source_selector'),
        parser_cfg.get('source_attr', 'data-source'),
        parser_cfg.get('block_selector'),
        timeout=config.get('timeout', 10),
    )


def build_github_client(
    config: Optional[Dict[str, Any]], debug: bool = False
) -> Tuple[Optional[GitHubStatusClient], bool]:
    if not config:
        return None, False

    enabled = config.get('enabled', True)
    if not enabled:
        return None, False

    token = os.getenv('AUTO_QUOTER_GITHUB_TOKEN') or config.get('token')
    dry_run = config.get('dry_run', False)
    if not token and not dry_run:
        print("GitHub token не указан, статус обновляться не будет.")
        return None, True

    client_kwargs = {
        'token': token,
        'default_emoji': config.get('emoji'),
        'timeout': config.get('timeout', 10),
        'dry_run': dry_run,
        'debug': bool(debug),
    }
    if config.get('graphql_url'):
        client_kwargs['api_url'] = config['graphql_url']

    client = GitHubStatusClient(**client_kwargs)
    return client, True
