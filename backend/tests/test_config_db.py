"""Tests for multi-database configuration support."""
import os
import unittest


class TestDatabaseConfig(unittest.TestCase):
    """Test cases for database configuration."""
    
    def setUp(self):
        """Clear environment variables before each test."""
        self.env_vars_to_clear = [
            'DATABASE_URL',
            'DATABASE_TYPE',
            'POSTGRES_USER',
            'POSTGRES_PASSWORD',
            'POSTGRES_HOST',
            'POSTGRES_PORT',
            'POSTGRES_DB'
        ]
        # Store original values
        self.original_env = {}
        for var in self.env_vars_to_clear:
            self.original_env[var] = os.environ.get(var)
    
    def tearDown(self):
        """Restore environment variables after each test."""
        for var, value in self.original_env.items():
            if value is None:
                os.environ.pop(var, None)
            else:
                os.environ[var] = value
    
    def test_default_database_url_is_sqlite(self):
        """Test that default DATABASE_URL is SQLite when no environment variables are set."""
        # Clear all database-related env vars
        for var in self.env_vars_to_clear:
            os.environ.pop(var, None)
        
        # Re-import to get fresh settings
        from importlib import reload
        from app import config
        reload(config)
        
        self.assertEqual(config.settings.DATABASE_URL, "sqlite:///./data/home_assets.db")
    
    def test_database_url_with_explicit_url(self):
        """Test that explicit DATABASE_URL takes precedence."""
        test_url = "sqlite:///./custom/path/test.db"
        os.environ['DATABASE_URL'] = test_url
        
        from importlib import reload
        from app import config
        reload(config)
        
        self.assertEqual(config.settings.DATABASE_URL, test_url)
    
    def test_database_url_with_postgresql_type(self):
        """Test that DATABASE_TYPE=postgresql builds correct PostgreSQL URL."""
        os.environ.update({
            'DATABASE_TYPE': 'postgresql',
            'POSTGRES_USER': 'testuser',
            'POSTGRES_PASSWORD': 'testpass',
            'POSTGRES_HOST': 'testhost',
            'POSTGRES_PORT': '5433',
            'POSTGRES_DB': 'testdb'
        })
        
        from importlib import reload
        from app import config
        reload(config)
        
        expected_url = "postgresql://testuser:testpass@testhost:5433/testdb"
        self.assertEqual(config.settings.DATABASE_URL, expected_url)
    
    def test_database_url_with_postgresql_defaults(self):
        """Test that DATABASE_TYPE=postgresql uses default values when env vars not set."""
        # Clear postgres-specific vars but set DATABASE_TYPE
        for var in self.env_vars_to_clear:
            os.environ.pop(var, None)
        
        os.environ['DATABASE_TYPE'] = 'postgresql'
        
        from importlib import reload
        from app import config
        reload(config)
        
        expected_url = "postgresql://postgres:postgres@localhost:5432/home_assets"
        self.assertEqual(config.settings.DATABASE_URL, expected_url)
    
    def test_explicit_url_overrides_type(self):
        """Test that explicit DATABASE_URL overrides DATABASE_TYPE."""
        explicit_url = "sqlite:///./explicit.db"
        os.environ.update({
            'DATABASE_URL': explicit_url,
            'DATABASE_TYPE': 'postgresql',
            'POSTGRES_HOST': 'ignored'
        })
        
        from importlib import reload
        from app import config
        reload(config)
        
        # Explicit URL should take precedence
        self.assertEqual(config.settings.DATABASE_URL, explicit_url)
    
    def test_case_insensitive_database_type(self):
        """Test that DATABASE_TYPE is case-insensitive."""
        test_cases = ['postgresql', 'POSTGRESQL', 'PostgreSQL']
        
        for db_type in test_cases:
            # Clear DATABASE_URL but set DATABASE_TYPE
            os.environ.pop('DATABASE_URL', None)
            os.environ['DATABASE_TYPE'] = db_type
            
            from importlib import reload
            from app import config
            reload(config)
            
            # Should build PostgreSQL URL regardless of case
            self.assertTrue(
                config.settings.DATABASE_URL.startswith("postgresql://"),
                f"Failed for DATABASE_TYPE={db_type}"
            )
    
    def test_unknown_database_type_defaults_to_sqlite(self):
        """Test that unknown DATABASE_TYPE defaults to SQLite."""
        # Clear DATABASE_URL but set unknown DATABASE_TYPE
        os.environ.pop('DATABASE_URL', None)
        os.environ['DATABASE_TYPE'] = 'mysql'
        
        from importlib import reload
        from app import config
        reload(config)
        
        self.assertEqual(config.settings.DATABASE_URL, "sqlite:///./data/home_assets.db")


if __name__ == '__main__':
    unittest.main()
