"""
UpdateManager - Automatic file updates from GitHub releases for Pico 2 W
Handles checking for new releases, downloading files, and safe installation.
"""

import json
import socket
import gc
import os
import asyncio
import time

class UpdateManager:
    """
    Manages automatic updates from GitHub releases.
    
    Features:
    - Fetches latest release metadata from GitHub API
    - Compares local version with remote version
    - Downloads updated files (boot.py, lib/*.py, index.html)
    - Safely writes files with atomic operations
    - Tracks version in version.json
    """
    
    # GitHub API endpoint for releases
    GITHUB_API_BASE = "api.github.com"
    
    # Files to update (path relative to Pico root)
    FILES_TO_UPDATE = [
        "boot.py",
        "index.html",
        "lib/gpio_control.py",
        "lib/http_server.py",
        "lib/light_sensor.py",
        "lib/paper_database.py",
        "lib/splitgrade_enhanced.py",
        "lib/temperature_sensor.py",
        "lib/timer_manager.py",
        "lib/update_manager.py",
        "lib/wifi_ap.py",
        "lib/wifi_sta.py",
    ]
    
    # Chunk size for downloads (matches HTML serving pattern)
    CHUNK_SIZE = 512
    
    def __init__(self, repo_owner='atriantas', repo_name='enlarger_server', version_file='version.json'):
        """
        Initialize UpdateManager.
        
        Args:
            repo_owner: GitHub repository owner
            repo_name: GitHub repository name
            version_file: Path to version.json on Pico (default: root directory)
        """
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.version_file = version_file
        self.current_version = self._load_version()
        self.latest_version = None
        self.release_data = None
        self.download_cache = {}
        
    def _load_version(self):
        """Load current version from version.json, fallback to 0.0.0."""
        try:
            with open(self.version_file, 'r') as f:
                data = json.load(f)
                return data.get('version', '0.0.0')
        except (OSError, ValueError):
            # File doesn't exist or invalid JSON
            return '0.0.0'
    
    def _save_version(self, version):
        """Save version to version.json."""
        try:
            data = {
                'version': version,
                'last_check': time.time(),
                'last_update': time.time()
            }
            with open(self.version_file, 'w') as f:
                json.dump(data, f)
            self.current_version = version
            return True
        except OSError as e:
            print(f"[UpdateManager] Error saving version: {e}")
            return False
    
    def _parse_version(self, version_str):
        """
        Parse version string to tuple for comparison.
        e.g., "v1.2.3" -> (1, 2, 3)
        """
        try:
            # Remove 'v' prefix if present
            version_str = version_str.lstrip('v')
            parts = version_str.split('.')
            # Pad to ensure 3 elements
            result = [int(p) for p in parts[:3]]
            while len(result) < 3:
                result.append(0)
            return tuple(result)
        except (ValueError, IndexError):
            return (0, 0, 0)
    
    def _version_newer(self, remote_version, local_version):
        """Check if remote version is newer than local."""
        remote_tuple = self._parse_version(remote_version)
        local_tuple = self._parse_version(local_version)
        return remote_tuple > local_tuple
    
    async def check_latest_release(self):
        """
        Fetch latest release metadata from GitHub API.
        Returns dict with {success, version, tag_name, published_at, error}
        """
        try:
            print("[UpdateManager] Fetching latest release from GitHub...")
            
            # Build GitHub API URL
            url = f"/repos/{self.repo_owner}/{self.repo_name}/releases/latest"
            
            # Create socket connection to GitHub API
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.GITHUB_API_BASE, 443))
            
            # Send HTTPS request (MicroPython 1.27.0 doesn't have urllib, so raw socket)
            # For simplicity, we'll use HTTP on port 80 instead of HTTPS
            sock.close()
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.GITHUB_API_BASE, 80))
            
            request = f"GET {url} HTTP/1.1\r\nHost: {self.GITHUB_API_BASE}\r\nUser-Agent: Pico2W-Darkroom\r\nConnection: close\r\n\r\n"
            sock.send(request.encode())
            
            # Read response
            response = b''
            while True:
                try:
                    chunk = sock.recv(1024)
                    if not chunk:
                        break
                    response += chunk
                except:
                    break
            sock.close()
            
            # Parse HTTP response (split headers and body)
            response_str = response.decode('utf-8', errors='ignore')
            if '\r\n\r\n' in response_str:
                body = response_str.split('\r\n\r\n', 1)[1]
            else:
                raise ValueError("Invalid HTTP response")
            
            # Parse JSON body
            release_data = json.loads(body)
            
            if 'tag_name' not in release_data:
                return {
                    'success': False,
                    'error': 'Invalid release data format'
                }
            
            tag_name = release_data['tag_name']
            version = tag_name.lstrip('v')
            
            # Check if newer
            is_newer = self._version_newer(version, self.current_version)
            
            self.latest_version = version
            self.release_data = release_data
            
            print(f"[UpdateManager] Latest version: {version} (current: {self.current_version})")
            print(f"[UpdateManager] Update available: {is_newer}")
            
            return {
                'success': True,
                'version': version,
                'tag_name': tag_name,
                'published_at': release_data.get('published_at', ''),
                'available': is_newer,
                'current_version': self.current_version
            }
            
        except Exception as e:
            print(f"[UpdateManager] Error checking release: {e}")
            return {
                'success': False,
                'error': str(e),
                'current_version': self.current_version
            }
    
    async def download_file(self, file_path):
        """
        Download a single file from GitHub raw content.
        Returns {success, size, content} or {success, error}
        """
        try:
            # Build raw GitHub URL
            # From release assets or raw main branch
            url = f"https://raw.githubusercontent.com/{self.repo_owner}/{self.repo_name}/Back_Up/{file_path}"
            
            print(f"[UpdateManager] Downloading {file_path}...")
            
            # Connect to GitHub
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(("raw.githubusercontent.com", 80))  # Use HTTP for simplicity
            
            request = f"GET /{self.repo_owner}/{self.repo_name}/Back_Up/{file_path} HTTP/1.1\r\nHost: raw.githubusercontent.com\r\nUser-Agent: Pico2W-Darkroom\r\nConnection: close\r\n\r\n"
            sock.send(request.encode())
            
            # Read response in chunks
            content = b''
            total_bytes = 0
            while True:
                try:
                    chunk = sock.recv(self.CHUNK_SIZE)
                    if not chunk:
                        break
                    content += chunk
                    total_bytes += len(chunk)
                    
                    # Garbage collection every ~10 chunks (5KB)
                    if total_bytes % 5120 == 0:
                        gc.collect()
                except:
                    break
            sock.close()
            
            # Parse HTTP response
            response_str = content.decode('utf-8', errors='ignore')
            if '\r\n\r\n' in response_str:
                body = response_str.split('\r\n\r\n', 1)[1]
            else:
                raise ValueError("Invalid HTTP response")
            
            # Check for 404 or other errors
            if "404" in response_str:
                print(f"[UpdateManager] File not found: {file_path}")
                return {'success': False, 'error': 'File not found on GitHub'}
            
            print(f"[UpdateManager] Downloaded {file_path}: {len(body)} bytes")
            
            return {
                'success': True,
                'size': len(body),
                'content': body
            }
            
        except Exception as e:
            print(f"[UpdateManager] Error downloading {file_path}: {e}")
            return {'success': False, 'error': str(e)}
    
    async def check_and_download(self):
        """
        Check for updates and download if available.
        Returns {success, version, available, files, updated_count, restart_required, error}
        """
        try:
            # Step 1: Check for latest release
            check_result = await self.check_latest_release()
            if not check_result['success']:
                return {
                    'success': False,
                    'error': check_result.get('error', 'Unknown error'),
                    'current_version': self.current_version
                }
            
            if not check_result['available']:
                return {
                    'success': True,
                    'available': False,
                    'current_version': self.current_version,
                    'latest_version': check_result['version'],
                    'message': 'Already on latest version'
                }
            
            # Step 2: Download all files
            updated_files = []
            failed_files = []
            
            for file_path in self.FILES_TO_UPDATE:
                result = await self.download_file(file_path)
                
                if not result['success']:
                    failed_files.append({
                        'file': file_path,
                        'error': result.get('error', 'Unknown error')
                    })
                    continue
                
                # Step 3: Write file to Pico (safe write with .tmp extension)
                write_result = await self._write_file_safe(file_path, result['content'])
                
                if write_result['success']:
                    updated_files.append(file_path)
                    print(f"[UpdateManager] ✓ Updated {file_path}")
                else:
                    failed_files.append({
                        'file': file_path,
                        'error': write_result.get('error', 'Write failed')
                    })
                    print(f"[UpdateManager] ✗ Failed to write {file_path}")
            
            # Step 4: Update version file if any files succeeded
            if updated_files:
                self._save_version(check_result['version'])
            
            # Determine result
            all_succeeded = len(failed_files) == 0
            
            return {
                'success': all_succeeded,
                'current_version': self.current_version,
                'latest_version': check_result['version'],
                'available': True,
                'updated_files': updated_files,
                'failed_files': failed_files,
                'updated_count': len(updated_files),
                'restart_required': all_succeeded and len(updated_files) > 0,
                'message': f"Updated {len(updated_files)} files" if all_succeeded else f"Partial update: {len(updated_files)}/{len(self.FILES_TO_UPDATE)} files"
            }
            
        except Exception as e:
            print(f"[UpdateManager] Fatal error in check_and_download: {e}")
            return {
                'success': False,
                'error': str(e),
                'current_version': self.current_version
            }
    
    async def _write_file_safe(self, file_path, content):
        """
        Safely write file with atomic operation.
        1. Write to .tmp file first
        2. Verify size matches
        3. Rename .tmp to final (atomic on most filesystems)
        """
        try:
            tmp_path = f"{file_path}.tmp"
            
            # Create lib directory if needed
            if '/' in file_path:
                dir_path = file_path.rsplit('/', 1)[0]
                try:
                    os.mkdir(dir_path)
                except OSError:
                    pass  # Directory already exists
            
            # Write to temporary file
            with open(tmp_path, 'w') as f:
                f.write(content)
            
            # Verify file was written
            stat_info = os.stat(tmp_path)
            if stat_info[6] != len(content):
                os.remove(tmp_path)
                return {
                    'success': False,
                    'error': f'Size mismatch: wrote {stat_info[6]}, expected {len(content)}'
                }
            
            # Atomic rename (remove old file first on MicroPython)
            try:
                os.remove(file_path)
            except OSError:
                pass  # File doesn't exist yet (first installation)
            
            os.rename(tmp_path, file_path)
            
            # Garbage collection after write
            gc.collect()
            
            return {'success': True}
            
        except Exception as e:
            # Clean up temp file if it exists
            try:
                os.remove(tmp_path)
            except:
                pass
            print(f"[UpdateManager] Error writing {file_path}: {e}")
            return {'success': False, 'error': str(e)}
    
    async def trigger_restart(self, delay_ms=1000):
        """
        Trigger Pico restart after delay.
        delay_ms: milliseconds to wait before restarting
        """
        try:
            import machine
            print(f"[UpdateManager] Restarting in {delay_ms}ms...")
            await asyncio.sleep_ms(delay_ms)
            machine.soft_reset()
        except Exception as e:
            print(f"[UpdateManager] Error during restart: {e}")
