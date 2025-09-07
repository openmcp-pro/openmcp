#!/usr/bin/env python3
"""Integration test for browser functionality."""

import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from openmcp.services.browseruse_service import BrowseruseService


async def test_integration():
    """Run integration test."""
    try:
        config = {'headless': True, 'timeout': 30, 'max_sessions': 5}
        service = BrowseruseService(config)
        await service.start()
        
        # Test session creation
        session_result = await service.call_tool('create_session', {'headless': True})
        assert 'session_id' in session_result
        
        session_id = session_result['session_id']
        
        # Test navigation
        nav_result = await service.call_tool('navigate', {'url': 'https://httpbin.org'}, session_id)
        assert nav_result.get('status') == 'success'
        
        # Test observe function
        observe_result = await service.call_tool('observe', {}, session_id)
        assert observe_result.get('status') == 'success'
        assert 'interactive_count' in observe_result
        assert 'formatted_text' in observe_result
        
        # Cleanup
        await service.call_tool('close_session', {}, session_id)
        await service.stop()
        
        print('✅ Integration test passed')
        
    except Exception as e:
        print(f'❌ Integration test failed: {e}')
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(test_integration())