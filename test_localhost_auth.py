#!/usr/bin/env python3
"""
Test script to demonstrate localhost authentication bypass and mock API key functionality.
"""

import asyncio
import httpx


async def test_localhost_without_auth():
    """Test making requests from localhost without authentication header."""
    print("Testing localhost access without Authorization header...")
    
    try:
        async with httpx.AsyncClient() as client:
            # Test health endpoint (no auth required)
            response = await client.get("http://localhost:8000/health")
            print(f"Health check: {response.status_code}")
            
            # Test services endpoint (normally requires auth, but should work from localhost)
            response = await client.get("http://localhost:8000/api/v1/services")
            print(f"Services endpoint without auth: {response.status_code}")
            if response.status_code == 200:
                print("✓ Localhost bypass working!")
                services = response.json()
                print(f"Available services: {services.get('available_services', [])}")
            else:
                print(f"✗ Localhost bypass failed: {response.text}")
                
    except Exception as e:
        print(f"Error testing localhost: {e}")


async def test_mock_api_key():
    """Test using the mock API key."""
    print("\nTesting mock API key 'openmcp-localhost-auth'...")
    
    headers = {"Authorization": "Bearer openmcp-localhost-auth"}
    
    try:
        async with httpx.AsyncClient() as client:
            # Test services endpoint with mock API key
            response = await client.get(
                "http://localhost:8000/api/v1/services",
                headers=headers
            )
            print(f"Services endpoint with mock key: {response.status_code}")
            if response.status_code == 200:
                print("✓ Mock API key working!")
                services = response.json()
                print(f"Available services: {services.get('available_services', [])}")
            else:
                print(f"✗ Mock API key failed: {response.text}")
                
    except Exception as e:
        print(f"Error testing mock API key: {e}")


async def test_invalid_key_from_remote():
    """Test that invalid keys still fail from remote IPs."""
    print("\nTesting invalid API key (should fail)...")
    
    headers = {"Authorization": "Bearer invalid-key"}
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "http://localhost:8000/api/v1/services",
                headers=headers
            )
            print(f"Services endpoint with invalid key: {response.status_code}")
            if response.status_code == 401:
                print("✓ Invalid key properly rejected!")
            else:
                print(f"✗ Invalid key not rejected: {response.text}")
                
    except Exception as e:
        print(f"Error testing invalid key: {e}")


async def main():
    """Run all tests."""
    print("Testing OpenMCP localhost authentication bypass and mock API key...\n")
    print("Make sure the OpenMCP server is running on localhost:8000")
    print("=" * 60)
    
    await test_localhost_without_auth()
    await test_mock_api_key()
    await test_invalid_key_from_remote()
    
    print("\n" + "=" * 60)
    print("Test completed!")


if __name__ == "__main__":
    asyncio.run(main())