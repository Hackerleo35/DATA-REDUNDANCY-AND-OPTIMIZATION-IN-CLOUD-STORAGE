"""
Standalone Demo Script
Author: Mohammed Hassan (4MH23CA030)
"""

import hashlib
import zlib

def demo():
    print("\n" + "="*60)
    print("Cloud Storage System - Quick Demo")
    print("Author: Mohammed Hassan (4MH23CA030)")
    print("="*60)
    
    # Demo 1: Deduplication
    print("\n📌 DEMO 1: Deduplication")
    file1 = b"Important document content"
    file2 = b"Important document content"
    
    hash1 = hashlib.sha256(file1).hexdigest()
    hash2 = hashlib.sha256(file2).hexdigest()
    
    print(f"File 1 hash: {hash1[:16]}...")
    print(f"File 2 hash: {hash2[:16]}...")
    print(f"Result: {'Duplicate detected!' if hash1 == hash2 else 'Different files'}")
    
    # Demo 2: Compression
    print("\n📌 DEMO 2: Compression")
    original = b"Hello World! " * 100
    compressed = zlib.compress(original)
    
    print(f"Original size: {len(original)} bytes")
    print(f"Compressed size: {len(compressed)} bytes")
    print(f"Savings: {((1 - len(compressed)/len(original)) * 100):.1f}%")
    
    # Demo 3: Redundancy
    print("\n📌 DEMO 3: Redundancy")
    regions = ['us-east', 'us-west', 'eu-central', 'asia-pacific']
    redundancy = 3
    print(f"File replicated to {redundancy} regions:")
    for i, region in enumerate(regions[:redundancy], 1):
        print(f"  {i}. {region}")
    
    print("\n✓ Demo complete!")
    print("="*60 + "\n")

if __name__ == '__main__':
    demo()
