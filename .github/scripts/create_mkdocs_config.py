#!/usr/bin/env python3
"""Create mkdocs configuration if it doesn't exist."""

import yaml
import os

def create_mkdocs_config():
    """Create mkdocs.yml configuration file."""
    if os.path.exists('mkdocs.yml'):
        print('✅ mkdocs.yml already exists')
        return

    config = {
        'site_name': 'OpenMCP Documentation',
        'site_description': 'A collection of optimized MCP services for AI Agents',
        'site_url': 'https://openmcp.github.io/openmcp',
        'repo_url': 'https://github.com/openmcp/openmcp',
        'nav': [
            {'Home': 'index.md'},
            {'User Guide': [
                {'Getting Started': 'user-guide/getting-started.md'},
                {'Browser Service': 'user-guide/browser-service.md'},
                {'Observe Function': 'user-guide/observe-function.md'}
            ]},
            {'API Reference': [
                {'Browser Service': 'api/browseruse.md'}
            ]},
            {'Examples': [
                {'Basic Usage': 'examples/basic.md'},
                {'Observe Function': 'examples/observe.md'}
            ]},
            {'Development': [
                {'Contributing': 'development/contributing.md'},
                {'Testing': 'development/testing.md'}
            ]}
        ],
        'theme': {
            'name': 'material',
            'features': [
                'navigation.tabs',
                'navigation.sections',
                'navigation.expand',
                'navigation.top',
                'search.suggest',
                'search.highlight',
                'content.code.annotate'
            ]
        },
        'plugins': [
            'search',
            {
                'mkdocstrings': {
                    'handlers': {
                        'python': {
                            'options': {
                                'show_source': True,
                                'show_root_heading': True,
                                'show_root_toc_entry': False
                            }
                        }
                    }
                }
            }
        ],
        'markdown_extensions': [
            'pymdownx.highlight',
            'pymdownx.inlinehilite',
            'pymdownx.snippets',
            'pymdownx.superfences',
            'admonition',
            'pymdownx.details',
            'attr_list',
            'md_in_html'
        ],
        'extra': {
            'social': [
                {
                    'icon': 'fontawesome/brands/github',
                    'link': 'https://github.com/openmcp/openmcp'
                }
            ]
        }
    }
    
    with open('mkdocs.yml', 'w') as f:
        yaml.dump(config, f, default_flow_style=False)
    
    print('✅ mkdocs.yml created')

if __name__ == "__main__":
    create_mkdocs_config()