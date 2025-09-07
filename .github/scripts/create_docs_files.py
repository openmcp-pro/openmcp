#!/usr/bin/env python3
"""Create basic documentation files for the project."""

import os

def create_docs_files():
    """Create basic documentation structure and files."""
    # Create directories
    os.makedirs('docs/user-guide', exist_ok=True)
    os.makedirs('docs/examples', exist_ok=True)
    os.makedirs('docs/development', exist_ok=True)
    
    # Create index page
    if not os.path.exists('docs/index.md'):
        with open('docs/index.md', 'w') as f:
            f.write("""# OpenMCP

A collection of optimized MCP (Model Context Protocol) services for AI Agents.

## Features

- **Browser Automation**: Full-featured browser service with Selenium
- **DOM Observation**: Smart page analysis with the observe function
- **Multi-session Support**: Handle multiple concurrent browser sessions
- **AI-Optimized**: Designed specifically for AI agent interactions

## Quick Start

```bash
pip install openmcp
openmcp serve
```

## Services

### Browser Service

The browser service provides comprehensive web automation capabilities:

- Navigate to web pages
- Interact with elements (click, type, etc.)
- Take screenshots
- **Observe function**: Get simplified DOM structure for AI agents

## Documentation

- [Getting Started](user-guide/getting-started.md)
- [Browser Service](user-guide/browser-service.md)
- [Observe Function](user-guide/observe-function.md)
- [API Reference](api/browseruse.md)
""")
        print('✅ Created docs/index.md')
    
    # Create observe function guide
    if not os.path.exists('docs/user-guide/observe-function.md'):
        with open('docs/user-guide/observe-function.md', 'w') as f:
            f.write("""# Observe Function

The observe function is a powerful feature that provides AI agents with a simplified, text-based representation of web page DOM structure.

## What it does

- Extracts visible, interactive elements (buttons, links, inputs, etc.)
- Provides DOM paths for precise element targeting
- Includes element text, attributes, and position information
- Filters out hidden or non-interactive elements

## Example Output

```
=== PAGE OBSERVATION ===
Title: Example Form
URL: https://example.com/form
Viewport: 1920x941

=== INTERACTIVE ELEMENTS (5) ===
[1] INPUT
    Path: #name
    Attributes: placeholder='Enter your name', type='text'
    Position: (100, 200) Size: 200x30

[2] BUTTON
    Path: form > button:nth-child(3).submit-btn
    Text: Submit Form
    Attributes: type='submit'
    Position: (100, 300) Size: 120x40
```

## Usage

```python
import openmcp

async with openmcp.browser() as browser:
    await browser.navigate("https://example.com")
    
    # Get page observation
    observation = await browser.observe()
    
    # Use DOM paths to interact with elements
    await browser.type("#name", "John Doe")
    await browser.click("form > button:nth-child(3).submit-btn")
```

## Benefits for AI Agents

1. **Simplified Structure**: Complex HTML reduced to essential interactive elements
2. **Precise Targeting**: DOM paths enable accurate element interaction
3. **Context Awareness**: Element text and attributes provide semantic meaning
4. **Position Information**: Spatial layout understanding
""")
        print('✅ Created docs/user-guide/observe-function.md')

if __name__ == "__main__":
    create_docs_files()