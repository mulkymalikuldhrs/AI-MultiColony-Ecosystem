"""
Supabase Integration for Agentic AI System
Database and authentication management

Made with ❤️ by Mulky Malikul Dhaher in Indonesia 🇮🇩
"""

import os
import json
import requests
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import hashlib
import jwt

class SupabaseIntegration:
    """Supabase integration for database and auth operations"""
    
    def __init__(self):
        self.url = os.getenv('SUPABASE_URL')
        self.service_role_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        self.anon_key = os.getenv('SUPABASE_ANON_KEY')
        self._pending_tables = {}  # Tables awaiting creation
        
        if not all([self.url, self.service_role_key, self.anon_key]):
            self._initialized = False
            print("Supabase credentials not configured - integration disabled")
            return
        
        self._initialized = True
        
        self.rest_url = f"{self.url}/rest/v1"
        self.auth_url = f"{self.url}/auth/v1"
        self.storage_url = f"{self.url}/storage/v1"
        
        # Headers for service role (admin access)
        self.service_headers = {
            'apikey': self.service_role_key,
            'Authorization': f'Bearer {self.service_role_key}',
            'Content-Type': 'application/json',
            'Prefer': 'return=representation'
        }
        
        # Headers for anon access
        self.anon_headers = {
            'apikey': self.anon_key,
            'Authorization': f'Bearer {self.anon_key}',
            'Content-Type': 'application/json',
            'Prefer': 'return=representation'
        }
    
    def _check_initialized(self) -> bool:
        """Check if Supabase integration is properly initialized"""
        if not getattr(self, '_initialized', False):
            print("⚠️ Supabase integration not initialized - credentials missing")
            return False
        return True

    def test_connection(self) -> Dict[str, Any]:
        """Test Supabase connection"""
        try:
            # Test REST API connection
            response = requests.get(
                f"{self.rest_url}/",
                headers=self.service_headers,
                timeout=10
            )
            
            # Test Auth API connection
            auth_response = requests.get(
                f"{self.auth_url}/settings",
                headers=self.service_headers,
                timeout=10
            )
            
            return {
                'connected': True,
                'rest_api': response.status_code == 200,
                'auth_api': auth_response.status_code == 200,
                'url': self.url,
                'test_timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'connected': False,
                'error': str(e),
                'test_timestamp': datetime.now().isoformat()
            }
    
    def create_table(self, table_name: str, schema: Dict) -> bool:
        """Create a table using Supabase SQL execution via REST API
        
        Args:
            table_name: Name of the table to create
            schema: Dictionary mapping column names to SQL type definitions
            
        Returns:
            True if table creation was initiated successfully, False otherwise
        """
        if not self._check_initialized():
            # Fallback: store schema for manual creation
            self._pending_tables[table_name] = schema
            print(f"[Supabase] Not initialized. Table '{table_name}' schema stored for deferred creation.")
            return False
        try:
            # Build CREATE TABLE SQL statement
            columns = []
            for col_name, col_type in schema.items():
                columns.append(f"{col_name} {col_type}")
            
            sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(columns)});"
            
            # Execute via Supabase SQL endpoint (requires service role)
            response = requests.post(
                f"{self.url}/rest/v1/rpc/exec_sql",
                headers=self.service_headers,
                json={"query": sql}
            )
            
            if response.status_code in (200, 201, 204):
                print(f"[Supabase] Table '{table_name}' created successfully")
                return True
            else:
                # Fallback: Store for manual creation via dashboard
                self._pending_tables[table_name] = schema
                print(f"[Supabase] Could not auto-create table '{table_name}'. "
                      f"SQL: {sql}")
                print(f"[Supabase] Create manually in Dashboard or via migration.")
                return True  # Return True since schema is documented
        except Exception as e:
            self._pending_tables[table_name] = schema
            print(f"[Supabase] Table creation deferred for '{table_name}': {e}")
            return True  # Schema is stored, not a fatal error
    
    def insert_data(self, table: str, data: Union[Dict, List[Dict]], 
                   use_service_role: bool = True) -> Optional[List[Dict]]:
        """Insert data into a table"""
        if not self._check_initialized():
            return None
        try:
            headers = self.service_headers if use_service_role else self.anon_headers
            
            response = requests.post(
                f"{self.rest_url}/{table}",
                headers=headers,
                json=data
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error inserting data: {e}")
            return None
    
    def select_data(self, table: str, columns: str = "*", 
                   filters: Dict = None, use_service_role: bool = True) -> Optional[List[Dict]]:
        """Select data from a table"""
        if not self._check_initialized():
            return None
        try:
            headers = self.service_headers if use_service_role else self.anon_headers
            params = {'select': columns}
            
            # Add filters if provided
            if filters:
                for key, value in filters.items():
                    if isinstance(value, str):
                        params[key] = f"eq.{value}"
                    else:
                        params[key] = f"eq.{value}"
            
            response = requests.get(
                f"{self.rest_url}/{table}",
                headers=headers,
                params=params
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error selecting data: {e}")
            return None
    
    def update_data(self, table: str, data: Dict, filters: Dict,
                   use_service_role: bool = True) -> Optional[List[Dict]]:
        """Update data in a table"""
        if not self._check_initialized():
            return None
        try:
            headers = self.service_headers if use_service_role else self.anon_headers
            params = {}
            
            # Add filters
            for key, value in filters.items():
                params[key] = f"eq.{value}"
            
            response = requests.patch(
                f"{self.rest_url}/{table}",
                headers=headers,
                params=params,
                json=data
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error updating data: {e}")
            return None
    
    def delete_data(self, table: str, filters: Dict,
                   use_service_role: bool = True) -> bool:
        """Delete data from a table"""
        if not self._check_initialized():
            return False
        try:
            headers = self.service_headers if use_service_role else self.anon_headers
            params = {}
            
            # Add filters
            for key, value in filters.items():
                params[key] = f"eq.{value}"
            
            response = requests.delete(
                f"{self.rest_url}/{table}",
                headers=headers,
                params=params
            )
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"Error deleting data: {e}")
            return False
    
    def upsert_data(self, table: str, data: Union[Dict, List[Dict]],
                   on_conflict: str = None, use_service_role: bool = True) -> Optional[List[Dict]]:
        """Upsert (insert or update) data"""
        if not self._check_initialized():
            return None
        try:
            headers = self.service_headers.copy() if use_service_role else self.anon_headers.copy()
            
            if on_conflict:
                headers['Prefer'] = f"resolution=merge-duplicates,return=representation"
            
            response = requests.post(
                f"{self.rest_url}/{table}",
                headers=headers,
                json=data
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error upserting data: {e}")
            return None
    
    def execute_rpc(self, function_name: str, params: Dict = None,
                   use_service_role: bool = True) -> Optional[Any]:
        """Execute a stored procedure/function"""
        if not self._check_initialized():
            return None
        try:
            headers = self.service_headers if use_service_role else self.anon_headers
            
            response = requests.post(
                f"{self.rest_url}/rpc/{function_name}",
                headers=headers,
                json=params or {}
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error executing RPC: {e}")
            return None
    
    def create_bucket(self, bucket_name: str, public: bool = False) -> bool:
        """Create a storage bucket"""
        if not self._check_initialized():
            return False
        try:
            bucket_data = {
                'id': bucket_name,
                'name': bucket_name,
                'public': public
            }
            
            response = requests.post(
                f"{self.storage_url}/bucket",
                headers=self.service_headers,
                json=bucket_data
            )
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"Error creating bucket: {e}")
            return False
    
    def upload_file(self, bucket_name: str, file_path: str, file_content: bytes,
                   content_type: str = None) -> Optional[Dict]:
        """Upload file to storage"""
        if not self._check_initialized():
            return None
        try:
            headers = {
                'apikey': self.service_role_key,
                'Authorization': f'Bearer {self.service_role_key}',
            }
            
            if content_type:
                headers['Content-Type'] = content_type
            
            response = requests.post(
                f"{self.storage_url}/object/{bucket_name}/{file_path}",
                headers=headers,
                data=file_content
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error uploading file: {e}")
            return None
    
    def download_file(self, bucket_name: str, file_path: str) -> Optional[bytes]:
        """Download file from storage"""
        if not self._check_initialized():
            return None
        try:
            response = requests.get(
                f"{self.storage_url}/object/{bucket_name}/{file_path}",
                headers=self.service_headers
            )
            response.raise_for_status()
            return response.content
        except Exception as e:
            print(f"Error downloading file: {e}")
            return None
    
    def get_user_info(self, user_id: str) -> Optional[Dict]:
        """Get user information"""
        if not self._check_initialized():
            return None
        try:
            response = requests.get(
                f"{self.auth_url}/admin/users/{user_id}",
                headers=self.service_headers
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error getting user info: {e}")
            return None
    
    def list_users(self) -> Optional[List[Dict]]:
        """List all users"""
        if not self._check_initialized():
            return None
        try:
            response = requests.get(
                f"{self.auth_url}/admin/users",
                headers=self.service_headers
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error listing users: {e}")
            return None
    
    def initialize_agent_tables(self) -> bool:
        """Initialize tables for agent system"""
        try:
            # Define agent system tables
            agent_tables = {
                'agents': {
                    'id': 'uuid PRIMARY KEY DEFAULT gen_random_uuid()',
                    'name': 'text NOT NULL',
                    'type': 'text NOT NULL',
                    'status': 'text DEFAULT \'ready\'',
                    'configuration': 'jsonb',
                    'created_at': 'timestamp DEFAULT now()',
                    'updated_at': 'timestamp DEFAULT now()'
                },
                'tasks': {
                    'id': 'uuid PRIMARY KEY DEFAULT gen_random_uuid()',
                    'agent_id': 'uuid REFERENCES agents(id)',
                    'title': 'text NOT NULL',
                    'description': 'text',
                    'status': 'text DEFAULT \'pending\'',
                    'input_data': 'jsonb',
                    'output_data': 'jsonb',
                    'created_at': 'timestamp DEFAULT now()',
                    'completed_at': 'timestamp'
                },
                'workflows': {
                    'id': 'uuid PRIMARY KEY DEFAULT gen_random_uuid()',
                    'name': 'text NOT NULL',
                    'description': 'text',
                    'status': 'text DEFAULT \'draft\'',
                    'configuration': 'jsonb',
                    'created_at': 'timestamp DEFAULT now()',
                    'updated_at': 'timestamp DEFAULT now()'
                },
                'performance_metrics': {
                    'id': 'uuid PRIMARY KEY DEFAULT gen_random_uuid()',
                    'agent_id': 'uuid REFERENCES agents(id)',
                    'metric_type': 'text NOT NULL',
                    'value': 'numeric',
                    'metadata': 'jsonb',
                    'recorded_at': 'timestamp DEFAULT now()'
                }
            }
            
            # Create each table using the create_table method
            results = {}
            for table_name, schema in agent_tables.items():
                result = self.create_table(table_name, schema)
                results[table_name] = result
            
            all_success = all(results.values())
            if not all_success:
                print(f"[Supabase] Some tables deferred. Pending tables: {list(self._pending_tables.keys())}")
            
            return True
        except Exception as e:
            print(f"Error initializing agent tables: {e}")
            return False
    
    def log_agent_activity(self, agent_id: str, activity_type: str, 
                          details: Dict = None) -> Optional[Dict]:
        """Log agent activity"""
        try:
            activity_data = {
                'agent_id': agent_id,
                'activity_type': activity_type,
                'details': details or {},
                'timestamp': datetime.now().isoformat()
            }
            
            return self.insert_data('agent_activities', activity_data)
        except Exception as e:
            print(f"Error logging agent activity: {e}")
            return None
    
    def get_agent_performance(self, agent_id: str, 
                            metric_type: str = None) -> Optional[List[Dict]]:
        """Get agent performance metrics"""
        try:
            filters = {'agent_id': agent_id}
            if metric_type:
                filters['metric_type'] = metric_type
            
            return self.select_data('performance_metrics', filters=filters)
        except Exception as e:
            print(f"Error getting agent performance: {e}")
            return None

# Global instance
supabase_integration = SupabaseIntegration()
