#!/usr/bin/env python3
"""
Configuration Manager for PySpark Pipeline
==========================================

Handles configuration loading, validation, and environment setup.
"""

import yaml
import os
import logging
from typing import Dict, Any, Optional
from pathlib import Path

class ConfigManager:
    """
    Centralized configuration management for the pipeline.
    """
    
    def __init__(self, config_path: str = "config/pipeline_config.yaml"):
        """Initialize configuration manager."""
        self.config_path = config_path
        self.config = None
        self.logger = self._setup_logging()
        
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            config_file = Path(self.config_path)
            if not config_file.exists():
                raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
            
            with open(config_file, 'r') as f:
                self.config = yaml.safe_load(f)
            
            self.logger.info(f"Configuration loaded from {self.config_path}")
            self._validate_config()
            self._setup_environment()
            
            return self.config
            
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {str(e)}")
            raise
    
    def _validate_config(self):
        """Validate configuration structure and required fields."""
        required_sections = ['pipeline', 'environment', 'data', 'stages']
        
        for section in required_sections:
            if section not in self.config:
                raise ValueError(f"Missing required configuration section: {section}")
        
        # Validate data directories
        data_config = self.config['data']
        if 'input' not in data_config or 'output' not in data_config:
            raise ValueError("Missing input or output data configuration")
        
        self.logger.info("Configuration validation passed")
    
    def _setup_environment(self):
        """Setup environment variables from configuration."""
        env_vars = self.config.get('environment', {}).get('python', {}).get('environment_variables', {})
        
        for key, value in env_vars.items():
            os.environ[key] = str(value)
            self.logger.debug(f"Set environment variable: {key}")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup basic logging for configuration manager."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger(__name__)
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation.
        
        Args:
            key_path: Dot-separated path to configuration value (e.g., 'data.input.base_directory')
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        if not self.config:
            self.load_config()
        
        keys = key_path.split('.')
        value = self.config
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def get_spark_config(self) -> Dict[str, str]:
        """Get Spark configuration as dictionary."""
        spark_config = self.get('environment.spark', {})
        
        # Convert to Spark configuration format
        config_dict = {}
        for key, value in spark_config.items():
            if key in ['app_name', 'master', 'log_level']:
                continue  # These are handled separately
            
            # Convert snake_case to spark.config.format
            spark_key = f"spark.{key.replace('_', '.')}"
            config_dict[spark_key] = str(value)
        
        return config_dict
    
    def get_stage_config(self, stage_name: str) -> Dict[str, Any]:
        """Get configuration for a specific pipeline stage."""
        return self.get(f'stages.{stage_name}', {})
    
    def is_stage_enabled(self, stage_name: str) -> bool:
        """Check if a pipeline stage is enabled."""
        return self.get(f'stages.{stage_name}.enabled', True)
    
    def get_data_paths(self) -> Dict[str, str]:
        """Get all data paths from configuration."""
        base_input = self.get('data.input.base_directory', 'synthetic_data')
        base_output = self.get('data.output.base_directory', 'output')
        
        return {
            'input_base': base_input,
            'output_base': base_output,
            'products': os.path.join(base_input, self.get('data.input.files.products', 'products.csv')),
            'locations': os.path.join(base_input, self.get('data.input.files.locations', 'locations.csv')),
            'sales': os.path.join(base_input, self.get('data.input.files.sales_transactions', 'sales_transactions.csv')),
            'output_data': os.path.join(base_output, self.get('data.output.subdirectories.data', 'data')),
            'output_charts': os.path.join(base_output, self.get('data.output.subdirectories.charts', 'charts')),
            'output_reports': os.path.join(base_output, self.get('data.output.subdirectories.reports', 'reports')),
            'checkpoints': self.get('data.checkpoints.directory', 'checkpoints')
        }
    
    def create_directories(self):
        """Create all required directories."""
        paths = self.get_data_paths()
        
        directories_to_create = [
            paths['output_base'],
            paths['output_data'],
            paths['output_charts'],
            paths['output_reports'],
            paths['checkpoints'],
            self.get('logging.log_directory', 'logs')
        ]
        
        for directory in directories_to_create:
            Path(directory).mkdir(parents=True, exist_ok=True)
            self.logger.debug(f"Created directory: {directory}")
    
    def get_business_config(self) -> Dict[str, Any]:
        """Get business logic configuration."""
        return self.get('business', {})
    
    def get_monitoring_config(self) -> Dict[str, Any]:
        """Get monitoring configuration."""
        return self.get('monitoring', {})
    
    def save_runtime_config(self, runtime_data: Dict[str, Any], output_path: str):
        """Save runtime configuration and metadata."""
        runtime_config = {
            'pipeline_config': self.config,
            'runtime_data': runtime_data,
            'timestamp': runtime_data.get('start_time', 'unknown')
        }
        
        with open(output_path, 'w') as f:
            yaml.dump(runtime_config, f, default_flow_style=False)
        
        self.logger.info(f"Runtime configuration saved to {output_path}")

# Global configuration instance
_config_manager = None

def get_config_manager(config_path: str = "config/pipeline_config.yaml") -> ConfigManager:
    """Get global configuration manager instance."""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager(config_path)
        _config_manager.load_config()
    return _config_manager