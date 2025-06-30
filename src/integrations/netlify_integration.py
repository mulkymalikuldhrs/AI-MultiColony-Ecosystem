"""
Netlify Integration for Agentic AI System
Automated deployment and site management

Made with ❤️ by Mulky Malikul Dhaher in Indonesia 🇮🇩
"""

import os
import json
import requests
import zipfile
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import tempfile
import shutil

class NetlifyIntegration:
    """Netlify integration for automated deployment"""
    
    def __init__(self):
        self.access_token = os.getenv('NETLIFY_ACCESS_TOKEN')
        self.client_id = os.getenv('NETLIFY_CLIENT_ID')
        self.client_secret = os.getenv('NETLIFY_CLIENT_SECRET')
        self.base_url = "https://api.netlify.com/api/v1"
        
        if not self.access_token:
            raise ValueError("Netlify access token is required")
        
        self.headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
    
    def get_sites(self) -> List[Dict]:
        """Get all sites in the account"""
        try:
            response = requests.get(f"{self.base_url}/sites", headers=self.headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error getting sites: {e}")
            return []
    
    def get_site(self, site_id: str) -> Optional[Dict]:
        """Get specific site information"""
        try:
            response = requests.get(f"{self.base_url}/sites/{site_id}", headers=self.headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error getting site {site_id}: {e}")
            return None
    
    def create_site(self, name: str, repo_url: str = None) -> Optional[Dict]:
        """Create a new site"""
        try:
            site_data = {
                'name': name,
                'custom_domain': f"{name}.netlify.app"
            }
            
            if repo_url:
                site_data['repo'] = {
                    'repo': repo_url,
                    'branch': 'main',
                    'cmd': 'python build_static.py',
                    'dir': 'web_interface/static'
                }
            
            response = requests.post(
                f"{self.base_url}/sites", 
                headers=self.headers,
                json=site_data
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error creating site: {e}")
            return None
    
    def deploy_site(self, site_id: str, build_dir: str = None) -> Optional[Dict]:
        """Deploy site with files"""
        try:
            if not build_dir:
                build_dir = "web_interface"
            
            # Create zip file of the build directory
            zip_path = self._create_deployment_zip(build_dir)
            
            # Upload the zip file
            with open(zip_path, 'rb') as zip_file:
                files = {'file': zip_file}
                headers = {'Authorization': f'Bearer {self.access_token}'}
                
                response = requests.post(
                    f"{self.base_url}/sites/{site_id}/deploys",
                    headers=headers,
                    files=files
                )
                response.raise_for_status()
            
            # Clean up temporary zip file
            os.unlink(zip_path)
            
            return response.json()
            
        except Exception as e:
            print(f"Error deploying site: {e}")
            return None
    
    def _create_deployment_zip(self, source_dir: str) -> str:
        """Create a zip file for deployment"""
        temp_dir = tempfile.mkdtemp()
        zip_path = os.path.join(temp_dir, 'deployment.zip')
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            source_path = Path(source_dir)
            
            for file_path in source_path.rglob('*'):
                if file_path.is_file():
                    # Skip certain files
                    if any(skip in str(file_path) for skip in ['.pyc', '__pycache__', '.git']):
                        continue
                    
                    archive_name = file_path.relative_to(source_path)
                    zipf.write(file_path, archive_name)
        
        return zip_path
    
    def get_deploys(self, site_id: str) -> List[Dict]:
        """Get deployment history for a site"""
        try:
            response = requests.get(
                f"{self.base_url}/sites/{site_id}/deploys",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error getting deploys: {e}")
            return []
    
    def get_deploy_status(self, site_id: str, deploy_id: str) -> Optional[Dict]:
        """Get status of a specific deployment"""
        try:
            response = requests.get(
                f"{self.base_url}/sites/{site_id}/deploys/{deploy_id}",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error getting deploy status: {e}")
            return None
    
    def update_site_settings(self, site_id: str, settings: Dict) -> Optional[Dict]:
        """Update site settings"""
        try:
            response = requests.patch(
                f"{self.base_url}/sites/{site_id}",
                headers=self.headers,
                json=settings
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error updating site settings: {e}")
            return None
    
    def delete_site(self, site_id: str) -> bool:
        """Delete a site"""
        try:
            response = requests.delete(
                f"{self.base_url}/sites/{site_id}",
                headers=self.headers
            )
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"Error deleting site: {e}")
            return False
    
    def get_usage_stats(self) -> Optional[Dict]:
        """Get account usage statistics"""
        try:
            response = requests.get(f"{self.base_url}/accounts", headers=self.headers)
            response.raise_for_status()
            accounts = response.json()
            
            if accounts:
                account = accounts[0]  # Get first account
                return {
                    'account_id': account.get('id'),
                    'name': account.get('name'),
                    'slug': account.get('slug'),
                    'type': account.get('type_name'),
                    'created_at': account.get('created_at'),
                    'sites_count': len(self.get_sites())
                }
            
            return None
        except Exception as e:
            print(f"Error getting usage stats: {e}")
            return None
    
    def test_connection(self) -> Dict[str, Any]:
        """Test Netlify connection"""
        try:
            sites = self.get_sites()
            usage = self.get_usage_stats()
            
            return {
                'connected': True,
                'sites_count': len(sites),
                'account_info': usage,
                'test_timestamp': datetime.now().isoformat(),
                'api_version': 'v1'
            }
        except Exception as e:
            return {
                'connected': False,
                'error': str(e),
                'test_timestamp': datetime.now().isoformat()
            }

# Global instance
netlify_integration = NetlifyIntegration()
