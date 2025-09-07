#!/usr/bin/env python3
"""Stress test for observe function."""

import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from openmcp.services.browseruse_service import BrowseruseService


async def stress_test():
    """Stress test the observe function with multiple complex pages."""
    config = {'headless': True, 'timeout': 30, 'max_sessions': 5}
    service = BrowseruseService(config)
    
    test_urls = [
        'https://httpbin.org/forms/post',
        'https://github.com',
        'https://stackoverflow.com',
        'https://docs.python.org/3/',
    ]
    
    try:
        await service.start()
        
        for url in test_urls:
            print(f'Testing observe function on: {url}')
            
            # Create session
            session_result = await service.call_tool('create_session', {'headless': True})
            session_id = session_result['session_id']
            
            try:
                # Navigate
                await service.call_tool('navigate', {'url': url}, session_id)
                await asyncio.sleep(2)  # Wait for page load
                
                # Test observe function
                observe_result = await service.call_tool('observe', {}, session_id)
                
                assert observe_result.get('status') == 'success'
                assert 'interactive_count' in observe_result
                assert observe_result['interactive_count'] >= 0
                
                print(f'✅ {url}: Found {observe_result["interactive_count"]} interactive elements')
                
            finally:
                # Always cleanup session
                await service.call_tool('close_session', {}, session_id)
        
        print('✅ All stress tests passed')
        
    except Exception as e:
        print(f'❌ Stress test failed: {e}')
        sys.exit(1)
    finally:
        await service.stop()


if __name__ == "__main__":
    asyncio.run(stress_test())