#!/usr/bin/env python3
"""
MyPocketLawyer Data Sync Script
Uploads and downloads project data to/from Google Drive with OAuth authentication.
Maintains exact local file structure for seamless integration.
"""

import os
import json
import pickle
import zipfile
from pathlib import Path
from typing import List, Dict, Optional
import argparse
from datetime import datetime

# Google API imports
try:
    from google.auth.transport.requests import Request
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
    import io
except ImportError:
    print("❌ Missing Google API dependencies. Install with:")
    print("pip install google-auth google-auth-oauthlib google-api-python-client")
    exit(1)

# ============================================================
# CONFIGURATION
# ============================================================

class DataSyncConfig:
    """Configuration for Google Drive sync"""
    
    # Google Drive API settings
    SCOPES = ['https://www.googleapis.com/auth/drive']
    CREDENTIALS_FILE = 'client_secret_800648931401-m6spk0c3h53d17qtss63v8pd8kmp8t6f.apps.googleusercontent.com.json'  # Use OAuth credentials
    TOKEN_FILE = 'token.pickle'
    
    # Project structure to sync - focusing on data folder only
    SYNC_FOLDERS = [
        'data/processed',
        'data/raw'
    ]
    
    SYNC_FILES = [
        # Removed other files to focus only on data folder
    ]
    
    # Google Drive folder name
    DRIVE_FOLDER_NAME = 'MyPocketLawyer_RAG_Data'
    
    # Local project root
    PROJECT_ROOT = Path(__file__).parent

# ============================================================
# GOOGLE DRIVE SERVICE
# ============================================================

class GoogleDriveSync:
    """Handles Google Drive authentication and file operations"""
    
    def __init__(self, config: DataSyncConfig):
        self.config = config
        self.service = None
        self.drive_folder_id = None
        
    def authenticate(self) -> bool:
        """Authenticate with Google Drive using OAuth"""
        creds_path = self.config.PROJECT_ROOT / self.config.CREDENTIALS_FILE
        
        if not creds_path.exists():
            print(f"❌ Credentials file not found: {creds_path}")
            print("📋 To set up Google Drive authentication:")
            print("1. Go to https://console.cloud.google.com/")
            print("2. Create a project or select existing")
            print("3. Enable Google Drive API")
            print("4. Create OAuth 2.0 credentials")
            print("5. Download credentials.json to project root")
            return False
        
        try:
            # Check if it's a service account or OAuth file
            with open(creds_path, 'r') as f:
                creds_data = json.load(f)
            
            if creds_data.get('type') == 'service_account':
                print("❌ Service account detected, but we need OAuth for personal Drive")
                print("💡 Switching to OAuth authentication for better compatibility...")
                return False
            
            print("🔐 Using OAuth authentication...")
            creds = None
            token_path = self.config.PROJECT_ROOT / self.config.TOKEN_FILE
            
            # Load existing token
            if token_path.exists():
                with open(token_path, 'rb') as token:
                    creds = pickle.load(token)
            
            # Refresh or create new credentials
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    print("🔄 Refreshing expired credentials...")
                    creds.refresh(Request())
                else:
                    print("🔐 Starting OAuth authentication...")
                    print("⚠️  You need to authorize the app in your browser")
                    print("💡 If you see 'app not verified', click 'Advanced' → 'Go to [your-app-name] (unsafe)'")
                    
                    try:
                        flow = InstalledAppFlow.from_client_secrets_file(
                            creds_path, self.config.SCOPES)
                        # Try local server first
                        creds = flow.run_local_server(port=0)
                    except Exception as local_error:
                        print(f"⚠️  Local server failed: {local_error}")
                        print("🔄 Trying manual OAuth flow...")
                        
                        # Fallback to manual flow
                        flow = InstalledAppFlow.from_client_secrets_file(
                            creds_path, self.config.SCOPES)
                        flow.redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'
                        auth_url, _ = flow.authorization_url(prompt='consent')
                        
                        print(f"\n🌐 Please visit this URL to authorize the application:")
                        print(f"{auth_url}")
                        print("\n📝 After authorization, copy the authorization code and paste it below:")
                        auth_code = input("Enter authorization code: ").strip()
                        
                        if not auth_code:
                            print("❌ No authorization code provided.")
                            return False
                        
                        flow.fetch_token(code=auth_code)
                        creds = flow.credentials
                
                # Save credentials for future use
                with open(token_path, 'wb') as token:
                    pickle.dump(creds, token)
            
            # Build Drive service
            self.service = build('drive', 'v3', credentials=creds)
            print("✅ OAuth authentication successful!")
            return True
            
        except Exception as e:
            print(f"❌ Authentication failed: {str(e)}")
            return False
    
    def get_or_create_folder(self, folder_name: str, parent_id: str = None) -> str:
        """Get existing folder ID or create new folder"""
        # Search for existing folder
        query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
        if parent_id:
            query += f" and parents in '{parent_id}'"
        
        results = self.service.files().list(q=query).execute()
        folders = results.get('files', [])
        
        if folders:
            print(f"📁 Found existing folder: {folder_name}")
            return folders[0]['id']
        
        # Create new folder
        folder_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        if parent_id:
            folder_metadata['parents'] = [parent_id]
        
        folder = self.service.files().create(body=folder_metadata).execute()
        print(f"📁 Created new folder: {folder_name}")
        return folder['id']
    
    def upload_file(self, local_path: Path, drive_folder_id: str, drive_filename: str = None) -> str:
        """Upload file to Google Drive"""
        if not drive_filename:
            drive_filename = local_path.name
        
        # Check if file already exists
        query = f"name='{drive_filename}' and parents in '{drive_folder_id}' and trashed=false"
        results = self.service.files().list(q=query).execute()
        existing_files = results.get('files', [])
        
        file_metadata = {'name': drive_filename, 'parents': [drive_folder_id]}
        media = MediaFileUpload(str(local_path), resumable=True)
        
        if existing_files:
            # Update existing file (without parents field)
            file_id = existing_files[0]['id']
            update_metadata = {'name': drive_filename}
            self.service.files().update(
                fileId=file_id, 
                body=update_metadata, 
                media_body=media
            ).execute()
            print(f"📤 Updated: {drive_filename}")
        else:
            # Create new file
            self.service.files().create(
                body=file_metadata, 
                media_body=media
            ).execute()
            print(f"📤 Uploaded: {drive_filename}")
        
        return drive_filename
    
    def download_file(self, drive_file_id: str, local_path: Path) -> bool:
        """Download file from Google Drive"""
        try:
            request = self.service.files().get_media(fileId=drive_file_id)
            file_io = io.BytesIO()
            downloader = MediaIoBaseDownload(file_io, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
            
            # Ensure parent directory exists
            local_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write file content
            with open(local_path, 'wb') as f:
                f.write(file_io.getvalue())
            
            print(f"📥 Downloaded: {local_path.name}")
            return True
        except Exception as e:
            print(f"❌ Failed to download {local_path.name}: {str(e)}")
            return False
    
    def list_drive_files(self, folder_id: str) -> List[Dict]:
        """List all files in a Drive folder"""
        query = f"parents in '{folder_id}' and trashed=false"
        results = self.service.files().list(q=query, fields="files(id, name, mimeType)").execute()
        return results.get('files', [])

# ============================================================
# MAIN SYNC CLASS
# ============================================================

class MyPocketLawyerDataSync:
    """Main class for syncing MyPocketLawyer data with Google Drive"""
    
    def __init__(self):
        self.config = DataSyncConfig()
        self.drive_sync = GoogleDriveSync(self.config)
        self.stats = {
            'uploaded': 0,
            'downloaded': 0,
            'errors': 0
        }
    
    def setup(self) -> bool:
        """Initialize Google Drive connection"""
        print("🚀 MyPocketLawyer Data Sync Tool")
        print("=" * 50)
        
        if not self.drive_sync.authenticate():
            return False
        
        # Get or create main project folder
        self.drive_sync.drive_folder_id = self.drive_sync.get_or_create_folder(
            self.config.DRIVE_FOLDER_NAME
        )
        
        return True
    
    def create_archive(self, archive_path: Path) -> bool:
        """Create ZIP archive of all sync data"""
        print("📦 Creating data archive...")
        
        try:
            with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                
                # Add folders
                for folder in self.config.SYNC_FOLDERS:
                    folder_path = self.config.PROJECT_ROOT / folder
                    if folder_path.exists():
                        for file_path in folder_path.rglob('*'):
                            if file_path.is_file():
                                # Maintain relative path structure in archive
                                arc_name = file_path.relative_to(self.config.PROJECT_ROOT)
                                zipf.write(file_path, arc_name)
                                print(f"  📄 Added: {arc_name}")
                
                # Add individual files
                for file_name in self.config.SYNC_FILES:
                    file_path = self.config.PROJECT_ROOT / file_name
                    if file_path.exists():
                        zipf.write(file_path, file_name)
                        print(f"  📄 Added: {file_name}")
            
            print(f"✅ Archive created: {archive_path}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to create archive: {str(e)}")
            return False
    
    def extract_archive(self, archive_path: Path) -> bool:
        """Extract ZIP archive to maintain file structure"""
        print("📦 Extracting data archive...")
        
        try:
            with zipfile.ZipFile(archive_path, 'r') as zipf:
                zipf.extractall(self.config.PROJECT_ROOT)
                
                # List extracted files
                for file_info in zipf.filelist:
                    print(f"  📄 Extracted: {file_info.filename}")
            
            print(f"✅ Archive extracted to: {self.config.PROJECT_ROOT}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to extract archive: {str(e)}")
            return False
    
    def upload_data(self) -> bool:
        """Upload all sync data to Google Drive as ZIP archive"""
        print("\n🔄 Starting data upload...")
        
        # Create temporary archive
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_name = f"mypocketlawyer_data_{timestamp}.zip"
        temp_archive = self.config.PROJECT_ROOT / "temp" / archive_name
        temp_archive.parent.mkdir(exist_ok=True)
        
        try:
            # Create archive
            if not self.create_archive(temp_archive):
                return False
            
            # Upload to Drive
            self.drive_sync.upload_file(
                temp_archive, 
                self.drive_sync.drive_folder_id, 
                "mypocketlawyer_data_latest.zip"
            )
            
            # Create metadata file
            metadata = {
                "timestamp": timestamp,
                "sync_folders": self.config.SYNC_FOLDERS,
                "sync_files": self.config.SYNC_FILES,
                "archive_size_mb": round(temp_archive.stat().st_size / 1024 / 1024, 2)
            }
            
            metadata_path = temp_archive.parent / "sync_metadata.json"
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            self.drive_sync.upload_file(
                metadata_path,
                self.drive_sync.drive_folder_id,
                "sync_metadata.json"
            )
            
            self.stats['uploaded'] += 2
            print(f"\n✅ Upload completed successfully!")
            print(f"📊 Archive size: {metadata['archive_size_mb']} MB")
            
            return True
            
        except Exception as e:
            print(f"❌ Upload failed: {str(e)}")
            self.stats['errors'] += 1
            return False
        
        finally:
            # Cleanup temporary files
            if temp_archive.exists():
                temp_archive.unlink()
            if temp_archive.parent.exists():
                import shutil
                shutil.rmtree(temp_archive.parent)
    
    def download_data(self) -> bool:
        """Download data from Google Drive and extract to maintain structure"""
        print("\n🔄 Starting data download...")
        
        try:
            # List files in Drive folder
            drive_files = self.drive_sync.list_drive_files(self.drive_sync.drive_folder_id)
            
            # Find latest data archive
            data_archive = None
            metadata_file = None
            
            for file_info in drive_files:
                if file_info['name'] == 'mypocketlawyer_data_latest.zip':
                    data_archive = file_info
                elif file_info['name'] == 'sync_metadata.json':
                    metadata_file = file_info
            
            if not data_archive:
                print("❌ No data archive found in Google Drive")
                return False
            
            # Create temporary directory
            temp_dir = self.config.PROJECT_ROOT / "temp"
            temp_dir.mkdir(exist_ok=True)
            temp_archive = temp_dir / "downloaded_data.zip"
            
            # Download archive
            if not self.drive_sync.download_file(data_archive['id'], temp_archive):
                return False
            
            # Download metadata if available
            if metadata_file:
                metadata_path = temp_dir / "metadata.json"
                self.drive_sync.download_file(metadata_file['id'], metadata_path)
                
                # Display metadata
                try:
                    with open(metadata_path, 'r') as f:
                        metadata = json.load(f)
                    print(f"📅 Data timestamp: {metadata.get('timestamp', 'Unknown')}")
                    print(f"📦 Archive size: {metadata.get('archive_size_mb', 'Unknown')} MB")
                except:
                    pass
            
            # Extract archive
            if not self.extract_archive(temp_archive):
                return False
            
            self.stats['downloaded'] += 1
            print(f"\n✅ Download completed successfully!")
            
            return True
            
        except Exception as e:
            print(f"❌ Download failed: {str(e)}")
            self.stats['errors'] += 1
            return False
        
        finally:
            # Cleanup temporary files
            temp_dir = self.config.PROJECT_ROOT / "temp"
            if temp_dir.exists():
                import shutil
                shutil.rmtree(temp_dir)
    
    def check_status(self) -> None:
        """Check Google Drive sync status"""
        print("\n🔍 Checking Google Drive status...")
        
        try:
            drive_files = self.drive_sync.list_drive_files(self.drive_sync.drive_folder_id)
            
            print(f"📁 Drive folder: {self.config.DRIVE_FOLDER_NAME}")
            print(f"📄 Files in Drive: {len(drive_files)}")
            
            for file_info in drive_files:
                print(f"  • {file_info['name']} ({file_info['mimeType'].split('.')[-1]})")
            
            # Check local files status
            print(f"\n💻 Local sync status:")
            for folder in self.config.SYNC_FOLDERS:
                folder_path = self.config.PROJECT_ROOT / folder
                if folder_path.exists():
                    file_count = len(list(folder_path.rglob('*')))
                    print(f"  • {folder}/: {file_count} files")
                else:
                    print(f"  • {folder}/: ❌ Not found")
            
            for file_name in self.config.SYNC_FILES:
                file_path = self.config.PROJECT_ROOT / file_name
                status = "✅" if file_path.exists() else "❌"
                print(f"  • {file_name}: {status}")
                
        except Exception as e:
            print(f"❌ Status check failed: {str(e)}")
    
    def print_stats(self) -> None:
        """Print operation statistics"""
        print("\n📊 Sync Statistics:")
        print(f"  📤 Uploaded: {self.stats['uploaded']} files")
        print(f"  📥 Downloaded: {self.stats['downloaded']} files") 
        print(f"  ❌ Errors: {self.stats['errors']}")

# ============================================================
# CLI INTERFACE
# ============================================================

def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(
        description="MyPocketLawyer Google Drive Data Sync Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python data_sync.py upload          # Upload data to Google Drive
  python data_sync.py download        # Download data from Google Drive  
  python data_sync.py status          # Check sync status
  python data_sync.py setup           # Initial setup and authentication
        """
    )
    
    parser.add_argument(
        'command',
        choices=['upload', 'download', 'status', 'setup'],
        help='Action to perform'
    )
    
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force operation without confirmation prompts'
    )
    
    args = parser.parse_args()
    
    # Initialize sync tool
    sync_tool = MyPocketLawyerDataSync()
    
    if args.command == 'setup':
        if sync_tool.setup():
            print("\n✅ Setup completed successfully!")
            sync_tool.check_status()
        else:
            print("\n❌ Setup failed!")
            return 1
    
    elif args.command == 'status':
        if sync_tool.setup():
            sync_tool.check_status()
        else:
            return 1
    
    elif args.command == 'upload':
        if not args.force:
            confirm = input("\n⚠️  This will upload local data to Google Drive. Continue? (y/N): ")
            if confirm.lower() != 'y':
                print("Operation cancelled.")
                return 0
        
        if sync_tool.setup():
            success = sync_tool.upload_data()
            sync_tool.print_stats()
            return 0 if success else 1
        else:
            return 1
    
    elif args.command == 'download':
        if not args.force:
            confirm = input("\n⚠️  This will overwrite local data with Google Drive content. Continue? (y/N): ")
            if confirm.lower() != 'y':
                print("Operation cancelled.")
                return 0
        
        if sync_tool.setup():
            success = sync_tool.download_data()
            sync_tool.print_stats()
            return 0 if success else 1
        else:
            return 1

if __name__ == "__main__":
    exit(main())
