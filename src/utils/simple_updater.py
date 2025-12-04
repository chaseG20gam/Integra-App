
from __future__ import annotations

import json
import os
import sys
import shutil
import tempfile
import zipfile
import subprocess
import platform
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
                    self.check_failed.emit("No hay descargas compatibles en esta plataforma")
            else:
                self.no_update.emit()
                
        except urllib.error.HTTPError as e:
            if e.code == 404:
                # no releases found - this is normal for new repositories
                self.no_update.emit()
            else:
                self.check_failed.emit(f"HTTP error {e.code}: {str(e)}")
        except urllib.error.URLError as e:
            self.check_failed.emit(f"Error de red: {str(e)}")
        except json.JSONDecodeError:
            self.check_failed.emit("No hay respuesta del servidor")
        except ValueError as e:
            self.check_failed.emit(f"Error: {str(e)}")
        except Exception as e:
            self.check_failed.emit(f"Error inesperado: {str(e)}")
    
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
    # simple background thread for downloading and installing updates
    
    download_progress = pyqtSignal(int, int)  # bytes_downloaded, total_bytes
    extraction_started = pyqtSignal()  # extraction phase
    installation_started = pyqtSignal()  # installation phase
    update_completed = pyqtSignal()  # update installed
    download_failed = pyqtSignal(str)  # error message
    
    def __init__(self, update_info: UpdateInfo, parent=None):
        super().__init__(parent)
        self.update_info = update_info
        self.download_path = None
    
    def run(self):
        # download and install update file in background
        try:
            # step 1. download
            temp_dir = tempfile.mkdtemp(prefix="integra_update_")
            filename = f"integra_update_{self.update_info.version}.zip"
            self.download_path = os.path.join(temp_dir, filename)
            
            # download with progress tracking
            def progress_hook(block_num, block_size, total_size):
                downloaded = min(block_num * block_size, total_size)
                self.download_progress.emit(downloaded, total_size)
            
            urllib.request.urlretrieve(
                self.update_info.download_url,
                self.download_path,
                progress_hook
            )
            
            # step 2. extract
            self.extraction_started.emit()
            extract_dir = os.path.join(temp_dir, "extracted")
            os.makedirs(extract_dir, exist_ok=True)
            
            with zipfile.ZipFile(self.download_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
            
            # step 3. install
            self.installation_started.emit()
            self._install_update(extract_dir)
            
            self.update_completed.emit()
                
        except Exception as e:
            self.download_failed.emit(str(e))
    
    def _install_update(self, extract_dir):
        # install the update by replacing the current executable
        try:
            # find the new executable in the extracted files (cross-platform)
            new_exe_path = None
            is_windows = platform.system() == 'Windows'
            is_mac = platform.system() == 'Darwin'
            
            for root, dirs, files in os.walk(extract_dir):
                for file in files:
                    file_lower = file.lower()
                    if 'integra' in file_lower:
                        if is_windows and file.endswith('.exe'):
                            new_exe_path = os.path.join(root, file)
                            break
                        elif is_mac and (file.endswith('.app') or '.' not in file):
                            # Mac app bundle or executable without extension
                            new_exe_path = os.path.join(root, file)
                            break
                if new_exe_path:
                    break
            
            if not new_exe_path:
                raise Exception("No se ha encontrado el ejecutable")
            
            # get current executable path
            if getattr(sys, 'frozen', False):
                # running as PyInstaller executable
                current_exe = sys.executable
            else:
                # running in development (not in prod)
                raise Exception("No se puede actualizar desde desarrollo")
            
            # create backup of current executable
            backup_path = current_exe + ".backup"
            if os.path.exists(backup_path):
                os.remove(backup_path)
            shutil.copy2(current_exe, backup_path)
            
            # create appropriate script for the platform
            if platform.system() == "Windows":
                script_path = self._create_windows_update_script(current_exe, new_exe_path, backup_path)
                # execute the batch script using os.system for better compatibility
                import os
                os.system(f'start /min "" "{script_path}"')
            else:
                # Mac/Linux - use shell script
                script_path = self._create_unix_update_script(current_exe, new_exe_path, backup_path)
                import os
                os.system(f'chmod +x "{script_path}" && nohup "{script_path}" > /dev/null 2>&1 &')
            
        except Exception as e:
            raise Exception(f"Instalacion fallida: {str(e)}")
    
    def _create_windows_update_script(self, current_exe, new_exe_path, backup_path):
        # create a batch script to handle the file replacement and restart
        script_dir = os.path.dirname(current_exe)
        script_path = os.path.join(script_dir, "update_integra.bat")
        
        # use forward slashes converted to backslashes for Windows paths
        current_exe_win = current_exe.replace('/', '\\')
        new_exe_win = new_exe_path.replace('/', '\\')
        backup_path_win = backup_path.replace('/', '\\')
        script_dir_win = script_dir.replace('/', '\\')
        
        script_content = f'''@echo off
        title Integra Update
        echo Updating Integra Client Manager...

        :: Change to application directory
        cd /d "{script_dir_win}"

        :: Wait for application to fully close
        echo Waiting for application to close...
        timeout /t 5 /nobreak > nul

        :: Try to replace the executable multiple times if needed
        :RETRY
        echo Attempting to update executable...
        copy /y "{new_exe_win}" "{current_exe_win}" >nul 2>&1

        if errorlevel 1 (
            echo Retrying in 2 seconds...
            timeout /t 2 /nobreak > nul
            goto RETRY
        )

        :: Verify the copy worked
        if not exist "{current_exe_win}" (
            echo Update failed, restoring backup...
            copy /y "{backup_path_win}" "{current_exe_win}" >nul 2>&1
            echo Update failed. Press any key to exit.
            pause >nul
            exit /b 1
        )

        :: Clean up backup and temp files
        if exist "{backup_path_win}" del "{backup_path_win}" >nul 2>&1

        :: Restart the application
        echo Update completed! Restarting application...
        timeout /t 1 /nobreak > nul
        start "" "{current_exe_win}"

        :: Self-destruct this script
        timeout /t 2 /nobreak > nul
        del "%~f0" >nul 2>&1
        exit /b 0
        '''
        
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        return script_path
    
    def _create_unix_update_script(self, current_exe, new_exe_path, backup_path):
        # create a shell script to handle the file replacement and restart on Mac/Linux
        script_dir = os.path.dirname(current_exe)
        script_path = os.path.join(script_dir, "update_integra.sh")
        
        script_content = f'''#!/bin/bash
        echo "Updating Integra Client Manager..."

        # Change to application directory  
        cd "{script_dir}"

        # Wait for application to fully close
        echo "Waiting for application to close..."
        sleep 5

        # Try to replace the executable multiple times if needed
        for i in {{1..10}}; do
            echo "Attempting to update executable (attempt $i)..."
            if cp "{new_exe_path}" "{current_exe}"; then
                break
            fi
            echo "Retrying in 2 seconds..."
            sleep 2
        done

        # Verify the copy worked
        if [ ! -f "{current_exe}" ]; then
            echo "Update failed, restoring backup..."
            cp "{backup_path}" "{current_exe}"
            echo "Update failed."
            exit 1
        fi

        # Clean up backup and temp files
        rm -f "{backup_path}"

        # Restart the application
        echo "Update completed! Restarting application..."
        sleep 1
        open "{current_exe}" &

        # Self-destruct this script
        sleep 2
        rm -f "$0"
        exit 0
        '''
        
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        return script_path


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