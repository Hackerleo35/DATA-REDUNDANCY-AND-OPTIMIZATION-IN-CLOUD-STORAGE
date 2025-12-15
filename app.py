"""
Cloud Storage Redundancy & Optimization System
Main Application File
Author: Mohammed Hassan (4MH23CA030)
"""

import hashlib
import zlib
import json
import os
from datetime import datetime
from flask import Flask, request, jsonify, render_template_string
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# In-memory storage (in production, use database)
storage = {
    'files': [],
    'stats': {
        'total_files': 0,
        'total_original_size': 0,
        'total_compressed_size': 0,
        'duplicates_removed': 0,
        'redundancy_level': 3
    },
    'hashes': set(),  # For deduplication
    'logs': []
}

# Storage tiers with cost multipliers
STORAGE_TIERS = {
    'hot': {'cost': 0.023, 'retrieval_ms': 10},
    'warm': {'cost': 0.010, 'retrieval_ms': 100},
    'cold': {'cost': 0.004, 'retrieval_ms': 1000}
}


def calculate_hash(data):
    """Calculate SHA-256 hash for deduplication"""
    return hashlib.sha256(data).hexdigest()


def compress_data(data):
    """Compress data using zlib"""
    compressed = zlib.compress(data)
    compression_ratio = (1 - len(compressed) / len(data)) * 100
    return compressed, compression_ratio


def add_log(message, log_type='info'):
    """Add entry to activity log"""
    log_entry = {
        'message': message,
        'type': log_type,
        'timestamp': datetime.now().isoformat()
    }
    storage['logs'].append(log_entry)
    # Keep only last 50 logs
    if len(storage['logs']) > 50:
        storage['logs'] = storage['logs'][-50:]
    print(f"[{log_entry['timestamp']}] {message}")


def replicate_data(file_id, replicas):
    """Simulate data replication across nodes"""
    regions = ['us-east', 'us-west', 'eu-central', 'asia-pacific', 'south-america']
    replication_map = {
        'primary': regions[0],
        'replicas': regions[1:replicas]
    }
    add_log(f"Replicated file {file_id} to {replicas} regions", 'success')
    return replication_map


@app.route('/')
def index():
    """Serve simple HTML interface"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Cloud Storage System</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 1200px; margin: 50px auto; padding: 20px; background: #f5f5f5; }
            .container { background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #333; border-bottom: 3px solid #4CAF50; padding-bottom: 10px; }
            .stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin: 20px 0; }
            .stat-card { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; }
            .stat-card h3 { margin: 0 0 10px 0; font-size: 14px; opacity: 0.9; }
            .stat-card p { margin: 0; font-size: 28px; font-weight: bold; }
            button { background: #4CAF50; color: white; border: none; padding: 12px 24px; border-radius: 4px; cursor: pointer; font-size: 16px; }
            button:hover { background: #45a049; }
            .upload-form { margin: 20px 0; padding: 20px; background: #f9f9f9; border-radius: 8px; }
            .log { background: #f4f4f4; padding: 15px; border-radius: 4px; max-height: 300px; overflow-y: auto; font-family: monospace; font-size: 12px; }
            .log-entry { padding: 5px; margin: 2px 0; border-radius: 3px; }
            .log-info { background: #e3f2fd; }
            .log-success { background: #e8f5e9; }
            .log-warning { background: #fff3e0; }
            .log-error { background: #ffebee; }
            input[type="file"] { margin: 10px 0; }
            select { padding: 8px; margin: 10px 0; border-radius: 4px; border: 1px solid #ddd; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>☁️ Cloud Storage Redundancy & Optimization System</h1>
            
            <div class="stats">
                <div class="stat-card">
                    <h3>Total Files</h3>
                    <p id="totalFiles">0</p>
                </div>
                <div class="stat-card">
                    <h3>Storage Saved</h3>
                    <p id="storageSaved">0%</p>
                </div>
                <div class="stat-card">
                    <h3>Duplicates Removed</h3>
                    <p id="duplicates">0</p>
                </div>
                <div class="stat-card">
                    <h3>Total Size</h3>
                    <p id="totalSize">0 KB</p>
                </div>
            </div>
            
            <div class="upload-form">
                <h2>Upload File</h2>
                <form id="uploadForm" enctype="multipart/form-data">
                    <input type="file" id="fileInput" name="file" required>
                    <br>
                    <label>Storage Tier:</label>
                    <select id="tier" name="tier">
                        <option value="hot">Hot (Fast, Expensive)</option>
                        <option value="warm" selected>Warm (Medium)</option>
                        <option value="cold">Cold (Slow, Cheap)</option>
                    </select>
                    <br>
                    <label>Redundancy:</label>
                    <select id="redundancy" name="redundancy">
                        <option value="1">1x (No Backup)</option>
                        <option value="2">2x (Single Backup)</option>
                        <option value="3" selected>3x (Standard)</option>
                        <option value="5">5x (High Availability)</option>
                    </select>
                    <br>
                    <button type="submit">Upload & Process</button>
                </form>
            </div>
            
            <h2>Activity Log</h2>
            <div class="log" id="logContainer"></div>
            
            <div style="margin-top: 20px;">
                <button onclick="simulateFailure()">🔥 Simulate Node Failure</button>
                <button onclick="getStats()" style="background: #2196F3;">📊 Refresh Stats</button>
            </div>
        </div>
        
        <script>
            function updateStats() {
                fetch('/stats')
                    .then(r => r.json())
                    .then(data => {
                        document.getElementById('totalFiles').textContent = data.total_files;
                        document.getElementById('duplicates').textContent = data.duplicates_removed;
                        const saved = data.total_original_size > 0 ? 
                            ((1 - data.total_compressed_size / data.total_original_size) * 100).toFixed(1) : 0;
                        document.getElementById('storageSaved').textContent = saved + '%';
                        document.getElementById('totalSize').textContent = (data.total_compressed_size / 1024).toFixed(2) + ' KB';
                    });
            }
            
            function updateLogs() {
                fetch('/logs')
                    .then(r => r.json())
                    .then(data => {
                        const container = document.getElementById('logContainer');
                        container.innerHTML = data.logs.map(log => 
                            `<div class="log-entry log-${log.type}">[${new Date(log.timestamp).toLocaleTimeString()}] ${log.message}</div>`
                        ).reverse().join('');
                    });
            }
            
            document.getElementById('uploadForm').addEventListener('submit', function(e) {
                e.preventDefault();
                const formData = new FormData(this);
                fetch('/upload', { method: 'POST', body: formData })
                    .then(r => r.json())
                    .then(data => {
                        alert(data.message);
                        updateStats();
                        updateLogs();
                    })
                    .catch(err => alert('Error: ' + err));
            });
            
            function simulateFailure() {
                fetch('/simulate-failure', { method: 'POST' })
                    .then(r => r.json())
                    .then(data => {
                        alert(data.message);
                        updateLogs();
                    });
            }
            
            function getStats() {
                updateStats();
                updateLogs();
            }
            
            // Auto-refresh every 5 seconds
            setInterval(() => {
                updateStats();
                updateLogs();
            }, 5000);
            
            // Initial load
            updateStats();
            updateLogs();
        </script>
    </body>
    </html>
    """
    return render_template_string(html)


@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload with optimization and redundancy"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Read file data
    file_data = file.read()
    filename = secure_filename(file.filename)
    original_size = len(file_data)
    
    add_log(f"Received file: {filename} ({original_size} bytes)", 'info')
    
    # Step 1: Deduplication
    file_hash = calculate_hash(file_data)
    if file_hash in storage['hashes']:
        storage['stats']['duplicates_removed'] += 1
        add_log(f"Duplicate detected! File {filename} already exists", 'warning')
        return jsonify({
            'message': 'Duplicate file detected and rejected',
            'status': 'duplicate'
        })
    
    # Step 2: Compression
    compressed_data, compression_ratio = compress_data(file_data)
    compressed_size = len(compressed_data)
    add_log(f"Compressed {filename}: {original_size}B → {compressed_size}B ({compression_ratio:.1f}% reduction)", 'success')
    
    # Step 3: Redundancy
    tier = request.form.get('tier', 'warm')
    redundancy = int(request.form.get('redundancy', 3))
    
    file_id = len(storage['files']) + 1
    replication_map = replicate_data(file_id, redundancy)
    
    # Store file metadata
    file_entry = {
        'id': file_id,
        'name': filename,
        'hash': file_hash,
        'original_size': original_size,
        'compressed_size': compressed_size,
        'compression_ratio': compression_ratio,
        'tier': tier,
        'redundancy': redundancy,
        'replication_map': replication_map,
        'upload_time': datetime.now().isoformat(),
        'access_count': 0
    }
    
    storage['files'].append(file_entry)
    storage['hashes'].add(file_hash)
    
    # Update statistics
    storage['stats']['total_files'] += 1
    storage['stats']['total_original_size'] += original_size
    storage['stats']['total_compressed_size'] += compressed_size * redundancy
    storage['stats']['redundancy_level'] = redundancy
    
    add_log(f"Stored {filename} in {tier} tier with {redundancy}x replication", 'success')
    
    return jsonify({
        'message': f'File uploaded successfully with {redundancy}x redundancy',
        'status': 'success',
        'file': file_entry
    })


@app.route('/stats', methods=['GET'])
def get_stats():
    """Return current system statistics"""
    return jsonify(storage['stats'])


@app.route('/logs', methods=['GET'])
def get_logs():
    """Return activity logs"""
    return jsonify({'logs': storage['logs']})


@app.route('/files', methods=['GET'])
def list_files():
    """List all stored files"""
    return jsonify({'files': storage['files']})


@app.route('/simulate-failure', methods=['POST'])
def simulate_failure():
    """Simulate node failure and recovery"""
    add_log("⚠️ ALERT: Primary node failure detected!", 'error')
    add_log("Initiating failover to replica nodes...", 'warning')
    add_log("Data recovery in progress...", 'info')
    add_log("✓ All data recovered from replica nodes", 'success')
    add_log("System operational - Zero data loss!", 'success')
    
    return jsonify({
        'message': 'Node failure simulated - Recovery successful',
        'status': 'recovered'
    })


@app.route('/optimize', methods=['POST'])
def optimize_storage():
    """Run storage optimization (move cold files to cold tier)"""
    optimized = 0
    for file in storage['files']:
        if file['access_count'] == 0 and file['tier'] != 'cold':
            file['tier'] = 'cold'
            optimized += 1
            add_log(f"Moved {file['name']} to cold storage", 'info')
    
    add_log(f"Optimization complete: {optimized} files moved to cold tier", 'success')
    return jsonify({
        'message': f'Optimized {optimized} files',
        'files_optimized': optimized
    })


if __name__ == '__main__':
    add_log("Cloud Storage System started", 'success')
    add_log("System ready for file uploads", 'info')
    print("\n" + "="*60)
    print("Cloud Storage Redundancy & Optimization System")
    print("Author: Mohammed Hassan (4MH23CA030)")
    print("="*60)
    print("\nServer running at: http://127.0.0.1:5000")
    print("Press CTRL+C to stop\n")
    app.run(debug=True, host='0.0.0.0', port=5000)