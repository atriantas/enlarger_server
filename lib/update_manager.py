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

try:
    import ussl
    _HAS_SSL = True
except ImportError:
    try:
        import ssl as ussl
        _HAS_SSL = True
    except ImportError:
        ussl = None
        _HAS_SSL = False

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
    RAW_HOST = "raw.githubusercontent.com"
    
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
    
    def _connect(self, host, port, use_ssl=True):
        """Open a socket connection with optional TLS."""
        addr = socket.getaddrinfo(host, port)[0][-1]
        sock = socket.socket()
        sock.connect(addr)
        if use_ssl:
            if not _HAS_SSL:
                sock.close()
                raise OSError("SSL not available")
            try:
                sock = ussl.wrap_socket(sock)
            except Exception:
                # Some builds only accept positional args without kwargs
                sock = ussl.wrap_socket(sock)
        return sock

    def _decode_bytes(self, data):
        """Decode bytes to UTF-8 without keyword args (MicroPython compatibility)."""
        try:
            return data.decode("utf-8")
        except Exception:
            try:
                return data.decode()
            except Exception:
                return ""

    def _read_headers(self, sock):
        """Read HTTP response headers and return (status_code, headers, remainder)."""
        data = b""
        while b"\r\n\r\n" not in data:
            chunk = sock.recv(256)
            if not chunk:
                break
            data += chunk
        header_bytes, remainder = data.split(b"\r\n\r\n", 1)
        header_text = self._decode_bytes(header_bytes)
        lines = header_text.split("\r\n")
        status_line = lines[0] if lines else ""
        status_code = 0
        try:
            status_code = int(status_line.split(" ")[1])
        except Exception:
            status_code = 0
        headers = {}
        for line in lines[1:]:
            if ":" in line:
                key, value = line.split(":", 1)
                headers[key.strip().lower()] = value.strip()
        return status_code, headers, remainder

    def _readline(self, sock, buffer):
        """Read a line ending in CRLF from buffer/socket."""
        while b"\r\n" not in buffer:
            chunk = sock.recv(256)
            if not chunk:
                break
            buffer += chunk
        line, _, buffer = buffer.partition(b"\r\n")
        return line, buffer

    def _read_chunked(self, sock, initial, write_fn):
        """Read chunked HTTP body and stream to write_fn."""
        buffer = initial
        total = 0
        while True:
            line, buffer = self._readline(sock, buffer)
            if not line:
                break
            try:
                chunk_size = int(line.strip(), 16)
            except ValueError:
                break
            if chunk_size == 0:
                # Consume trailing CRLF after last chunk
                if b"\r\n" not in buffer:
                    _ = sock.recv(2)
                break
            while len(buffer) < chunk_size + 2:
                chunk = sock.recv(512)
                if not chunk:
                    break
                buffer += chunk
            chunk_data = buffer[:chunk_size]
            write_fn(chunk_data)
            total += len(chunk_data)
            buffer = buffer[chunk_size + 2:]
        return total

    async def check_latest_release(self):
        """
        Fetch latest release metadata from GitHub API.
        Returns dict with {success, version, tag_name, published_at, error}
        """
        try:
            print("[UpdateManager] Fetching latest release from GitHub...")
            
            # Build GitHub API URL
            url = f"/repos/{self.repo_owner}/{self.repo_name}/releases/latest"

            sock = self._connect(self.GITHUB_API_BASE, 443, use_ssl=True)
            request = (
                f"GET {url} HTTP/1.1\r\n"
                f"Host: {self.GITHUB_API_BASE}\r\n"
                "User-Agent: Pico2W-Darkroom\r\n"
                "Accept: application/json\r\n"
                "Connection: close\r\n\r\n"
            )
            sock.send(request.encode())

            status_code, headers, remainder = self._read_headers(sock)
            if status_code != 200:
                sock.close()
                raise ValueError(f"HTTP {status_code}")

            body_bytes = b""
            if headers.get("transfer-encoding") == "chunked":
                body_bytes = b""
                def _collect(chunk):
                    nonlocal body_bytes
                    body_bytes += chunk
                self._read_chunked(sock, remainder, _collect)
            else:
                body_bytes = remainder
                while True:
                    chunk = sock.recv(512)
                    if not chunk:
                        break
                    body_bytes += chunk
            sock.close()

            release_data = json.loads(self._decode_bytes(body_bytes))
            
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
        Returns {success, size, tmp_path} or {success, error}
        """
        try:
            print(f"[UpdateManager] Downloading {file_path}...")

            path = f"/{self.repo_owner}/{self.repo_name}/Back_Up/{file_path}"
            sock = self._connect(self.RAW_HOST, 443, use_ssl=True)
            request = (
                f"GET {path} HTTP/1.1\r\n"
                f"Host: {self.RAW_HOST}\r\n"
                "User-Agent: Pico2W-Darkroom\r\n"
                "Connection: close\r\n\r\n"
            )
            sock.send(request.encode())

            status_code, headers, remainder = self._read_headers(sock)
            if status_code == 404:
                sock.close()
                print(f"[UpdateManager] File not found: {file_path}")
                return {'success': False, 'error': 'File not found on GitHub'}
            if status_code != 200:
                sock.close()
                return {'success': False, 'error': f'HTTP {status_code}'}

            tmp_path = f"{file_path}.tmp"
            # Create lib directory if needed
            if '/' in file_path:
                dir_path = file_path.rsplit('/', 1)[0]
                try:
                    os.mkdir(dir_path)
                except OSError:
                    pass

            total_bytes = 0
            with open(tmp_path, 'wb') as f:
                if headers.get("transfer-encoding") == "chunked":
                    total_bytes = self._read_chunked(sock, remainder, f.write)
                else:
                    if remainder:
                        f.write(remainder)
                        total_bytes += len(remainder)
                    while True:
                        chunk = sock.recv(self.CHUNK_SIZE)
                        if not chunk:
                            break
                        f.write(chunk)
                        total_bytes += len(chunk)
                        if total_bytes % 5120 == 0:
                            gc.collect()

            sock.close()

            print(f"[UpdateManager] Downloaded {file_path}: {total_bytes} bytes")

            return {
                'success': True,
                'size': total_bytes,
                'tmp_path': tmp_path
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
                
                # Step 3: Commit temp file
                write_result = await self._commit_temp_file(
                    file_path,
                    result['tmp_path'],
                    result['size']
                )
                
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
    
    async def _commit_temp_file(self, file_path, tmp_path, expected_size):
        """
        Commit a temp file to final destination.
        1. Verify size matches expected
        2. Rename .tmp to final (atomic on most filesystems)
        """
        try:
            # Verify file was written
            stat_info = os.stat(tmp_path)
            if stat_info[6] != expected_size:
                os.remove(tmp_path)
                return {
                    'success': False,
                    'error': f'Size mismatch: wrote {stat_info[6]}, expected {expected_size}'
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
            print(f"[UpdateManager] Error committing {file_path}: {e}")
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
