
from __future__ import annotations

import json
import os
import tempfile
from typing import Optional
import urllib.request
import urllib.error

from PyQt6.QtCore import QObject, pyqtSignal, QThread

from utils.version import Version, CURRENT_VERSION, UPDATE_CONFIG


class UpdateInfo(object):
    # information about an available update
    
    def __init__(self, version: Version, download_url: str, release_notes: str = ""):
        self.version = version
        self.download_url = download_url
        self.release_notes = release_notes


class SimpleUpdateChecker(QThread):
    # simple background thread for checking updates when button is clicked
    
    update_available = pyqtSignal(object)  # UpdateInfo
    no_update = pyqtSignal()
    check_failed = pyqtSignal(str)  # error message
    
    def run(self):
        # check for updates in background thread
        try:
            # make request to github api
            request = urllib.request.Request(
                UPDATE_CONFIG["check_url"],
                headers={'User-Agent': UPDATE_CONFIG["user_agent"]}
            )
            
            with urllib.request.urlopen(request, timeout=10) as response:
                data = json.loads(response.read().decode())
            
            # parse release information
            tag_name = data.get("tag_name", "").lstrip("v")
            if not tag_name:
                self.no_update.emit()
                return
            
            remote_version = Version.from_string(tag_name)
            
            if remote_version > CURRENT_VERSION:
                # find download url for our platform
                download_url = self._find_download_url(data.get("assets", []))
                
                if download_url:
                    update_info = UpdateInfo(
                        version=remote_version,
                        download_url=download_url,
                        release_notes=data.get("body", "")
                    )
                    self.update_available.emit(update_info)
                else:
                    self.check_failed.emit("No compatible download found for your platform")
            else:
                self.no_update.emit()
                
        except urllib.error.HTTPError as e:
            if e.code == 404:
                # no releases found - this is normal for new repositories
                self.no_update.emit()
            else:
                self.check_failed.emit(f"HTTP error {e.code}: {str(e)}")
        except urllib.error.URLError as e:
            self.check_failed.emit(f"Network error: {str(e)}")
        except json.JSONDecodeError:
            self.check_failed.emit("Invalid response from update server")
        except ValueError as e:
            self.check_failed.emit(f"Version parsing error: {str(e)}")
        except Exception as e:
            self.check_failed.emit(f"Unexpected error: {str(e)}")
    
    def _find_download_url(self, assets: list) -> Optional[str]:
        # find appropriate download url for current platform
        # look for windows-compatible files
        for asset in assets:
            name = asset.get("name", "").lower()
            if name.endswith((".zip", ".exe")) and "windows" in name:
                return asset.get("browser_download_url")
        
        # fallback: look for any zip file
        for asset in assets:
            name = asset.get("name", "").lower()
            if name.endswith(".zip"):
                return asset.get("browser_download_url")
        
        return None


class UpdateDownloader(QThread):
    # simple background thread for downloading updates
    
    download_progress = pyqtSignal(int, int)  # bytes_downloaded, total_bytes
    download_completed = pyqtSignal(str)  # file_path
    download_failed = pyqtSignal(str)  # error message
    
    def __init__(self, update_info: UpdateInfo, parent=None):
        super().__init__(parent)
        self.update_info = update_info
        self.download_path = None
    
    def run(self):
        # download update file in background
        try:
            # create temporary download path
            temp_dir = tempfile.mkdtemp(prefix="integra_update_")
            filename = f"integra_update_{self.update_info.version}.zip"
            self.download_path = os.path.join(temp_dir, filename)
            
            # real download with progress tracking
            def progress_hook(block_num, block_size, total_size):
                downloaded = min(block_num * block_size, total_size)
                self.download_progress.emit(downloaded, total_size)
            
            urllib.request.urlretrieve(
                self.update_info.download_url,
                self.download_path,
                progress_hook
            )
            
            self.download_completed.emit(self.download_path)
                
        except Exception as e:
            self.download_failed.emit(str(e))


class SimpleUpdateManager(QObject):
    # simplified update management system - only manual checks
    
    update_available = pyqtSignal(object)  # UpdateInfo
    no_update_available = pyqtSignal()
    update_check_failed = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.checker = None
        self.downloader = None
        self.skipped_versions = set()  # track versions user chose to skip
    
    def check_for_update(self):
        # check for updates manually when user clicks button
        if self.checker and self.checker.isRunning():
            return  # already checking
        
        self.checker = SimpleUpdateChecker()
        self.checker.update_available.connect(self._on_update_available)
        self.checker.no_update.connect(self._on_no_update)
        self.checker.check_failed.connect(self._on_check_failed)
        self.checker.start()
    
    def download_update(self, update_info: UpdateInfo):
        # start downloading an update
        if self.downloader and self.downloader.isRunning():
            return None  # already downloading
        
        self.downloader = UpdateDownloader(update_info)
        return self.downloader
    
    def skip_version(self, version: Version):
        # mark a version as skipped so it won't be notified again
        self.skipped_versions.add(str(version))
    
    def _on_update_available(self, update_info):
        # handle when update is available
        # check if this version was skipped
        if str(update_info.version) not in self.skipped_versions:
            self.update_available.emit(update_info)
        else:
            self.no_update_available.emit()
    
    def _on_no_update(self):
        # handle when no update is available
        self.no_update_available.emit()
    
    def _on_check_failed(self, error):
        # handle when update check fails
        self.update_check_failed.emit(error)