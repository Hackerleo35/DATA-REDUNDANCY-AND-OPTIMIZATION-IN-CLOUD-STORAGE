"""
Testing Script for Cloud Storage System
Author: Mohammed Hassan (4MH23CA030)
"""

import hashlib
import zlib
import time
import random
import string

def test_deduplication():
    """Test deduplication logic"""
    print("\n" + "="*60)
    print("TEST 1: Deduplication")
    print("="*60)
    
    data1 = b"This is test data"
    data2 = b"This is test data"
    data3 = b"Different data"
    
    hash1 = hashlib.sha256(data1).hexdigest()
    hash2 = hashlib.sha256(data2).hexdigest()
    hash3 = hashlib.sha256(data3).hexdigest()
    
    print(f"Hash 1: {hash1[:16]}...")
    print(f"Hash 2: {hash2[:16]}...")
    print(f"Hash 3: {hash3[:16]}...")
    
    if hash1 == hash2:
        print("✓ Deduplication works: Same data produces same hash")
    if hash1 != hash3:
        print("✓ Different data produces different hash")

def test_compression():
    """Test compression efficiency"""
    print("\n" + "="*60)
    print("TEST 2: Compression")
    print("="*60)
    
    # Generate test data
    test_data = ''.join(random.choices(string.ascii_letters, k=10000)).encode()
    
    original_size = len(test_data)
    compressed = zlib.compress(test_data)
    compressed_size = len(compressed)
    ratio = (1 - compressed_size / original_size) * 100
    
    print(f"Original size: {original_size} bytes")
    print(f"Compressed size: {compressed_size} bytes")
    print(f"Compression ratio: {ratio:.2f}%")
    print(f"✓ Space saved: {original_size - compressed_size} bytes")

def test_redundancy():
    """Test redundancy calculation"""
    print("\n" + "="*60)
    print("TEST 3: Redundancy & Cost")
    print("="*60)
    
    file_size = 1024  # 1 KB
    redundancy_levels = [1, 2, 3, 5]
    
    for level in redundancy_levels:
        total_storage = file_size * level
        print(f"{level}x redundancy: {total_storage} bytes total storage")

def test_performance():
    """Test operation performance"""
    print("\n" + "="*60)
    print("TEST 4: Performance")
    print("="*60)
    
    data = b"x" * 100000  # 100 KB
    
    # Hash performance
    start = time.time()
    for _ in range(1000):
        hashlib.sha256(data).hexdigest()
    hash_time = time.time() - start
    print(f"1000 hash operations: {hash_time:.3f}s")
    
    # Compression performance
    start = time.time()
    for _ in range(100):
        zlib.compress(data)
    compress_time = time.time() - start
    print(f"100 compression operations: {compress_time:.3f}s")

if __name__ == '__main__':
    print("\n" + "="*60)
    print("Cloud Storage System - Test Suite")
    print("Author: Mohammed Hassan (4MH23CA030)")
    print("="*60)
    
    test_deduplication()
    test_compression()
    test_redundancy()
    test_performance()
    
    print("\n" + "="*60)
    print("All tests completed!")
    print("="*60 + "\n")

