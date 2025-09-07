#!/usr/bin/env python3
"""Performance benchmark for observe function."""

import asyncio
import time
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from openmcp.services.browseruse_service import BrowseruseService


async def benchmark_observe():
    """Benchmark the observe function performance."""
    config = {'headless': True, 'timeout': 30, 'max_sessions': 5}
    service = BrowseruseService(config)
    
    try:
        await service.start()
        
        # Create session
        session_result = await service.call_tool('create_session', {'headless': True})
        session_id = session_result['session_id']
        
        # Navigate to a complex page
        await service.call_tool('navigate', {'url': 'https://github.com'}, session_id)
        await asyncio.sleep(2)
        
        # Benchmark observe function
        times = []
        for i in range(10):
            start_time = time.time()
            observe_result = await service.call_tool('observe', {}, session_id)
            end_time = time.time()
            
            if observe_result.get('status') == 'success':
                times.append(end_time - start_time)
                print(f'Run {i+1}: {end_time - start_time:.3f}s')
        
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)
        
        print(f'Observe function performance:')
        print(f'  Average: {avg_time:.3f}s')
        print(f'  Min: {min_time:.3f}s')
        print(f'  Max: {max_time:.3f}s')
        
        # Alert if performance degrades
        if avg_time > 5.0:  # Alert if average time > 5 seconds
            print('⚠️ Performance degradation detected!')
            sys.exit(1)
        else:
            print('✅ Performance within acceptable limits')
        
        await service.call_tool('close_session', {}, session_id)
        
    finally:
        await service.stop()


if __name__ == "__main__":
    asyncio.run(benchmark_observe())