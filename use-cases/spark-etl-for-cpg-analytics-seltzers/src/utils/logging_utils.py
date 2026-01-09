#!/usr/bin/env python3
"""
Logging and Monitoring Utilities
===============================

Comprehensive logging, performance monitoring, and error handling utilities.
"""

import logging
import logging.handlers
import time
import psutil
import os
import json
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path
from functools import wraps
import traceback

class PipelineLogger:
    """
    Enhanced logging system for the pipeline with performance monitoring.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize pipeline logger."""
        self.config = config
        self.log_dir = config.get('log_directory', 'logs')
        self.metrics = {}
        self.start_times = {}
        
        # Create log directory
        Path(self.log_dir).mkdir(parents=True, exist_ok=True)
        
        # Setup loggers
        self.logger = self._setup_logger()
        self.performance_logger = self._setup_performance_logger()
        
    def _setup_logger(self) -> logging.Logger:
        """Setup main application logger."""
        logger = logging.getLogger('pipeline')
        logger.setLevel(getattr(logging, self.config.get('level', 'INFO')))
        
        # Clear existing handlers
        logger.handlers.clear()
        
        # Console handler
        if self.config.get('console_enabled', True):
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            console_formatter = logging.Formatter(
                self.config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            )
            console_handler.setFormatter(console_formatter)
            logger.addHandler(console_handler)
        
        # File handler with rotation
        if self.config.get('file_enabled', True):
            log_file = os.path.join(self.log_dir, 'pipeline.log')
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=self._parse_size(self.config.get('max_file_size', '10MB')),
                backupCount=self.config.get('backup_count', 5)
            )
            file_handler.setLevel(logging.DEBUG)
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
            )
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)
        
        return logger
    
    def _setup_performance_logger(self) -> logging.Logger:
        """Setup performance metrics logger."""
        perf_logger = logging.getLogger('performance')
        perf_logger.setLevel(logging.INFO)
        
        # Performance log file
        perf_file = os.path.join(self.log_dir, 'performance.log')
        perf_handler = logging.FileHandler(perf_file)
        perf_formatter = logging.Formatter('%(asctime)s - %(message)s')
        perf_handler.setFormatter(perf_formatter)
        perf_logger.addHandler(perf_handler)
        
        return perf_logger
    
    def _parse_size(self, size_str: str) -> int:
        """Parse size string (e.g., '10MB') to bytes."""
        size_str = size_str.upper()
        if size_str.endswith('KB'):
            return int(size_str[:-2]) * 1024
        elif size_str.endswith('MB'):
            return int(size_str[:-2]) * 1024 * 1024
        elif size_str.endswith('GB'):
            return int(size_str[:-2]) * 1024 * 1024 * 1024
        else:
            return int(size_str)
    
    def start_stage(self, stage_name: str):
        """Start timing a pipeline stage."""
        self.start_times[stage_name] = time.time()
        self.logger.info(f"🚀 Starting stage: {stage_name}")
        
        # Log system metrics at stage start
        self._log_system_metrics(f"stage_start_{stage_name}")
    
    def end_stage(self, stage_name: str, success: bool = True, **kwargs):
        """End timing a pipeline stage."""
        if stage_name not in self.start_times:
            self.logger.warning(f"No start time recorded for stage: {stage_name}")
            return
        
        duration = time.time() - self.start_times[stage_name]
        status = "✅ Completed" if success else "❌ Failed"
        
        self.logger.info(f"{status} stage: {stage_name} (Duration: {duration:.2f}s)")
        
        # Record performance metrics
        self.metrics[stage_name] = {
            'duration': duration,
            'success': success,
            'timestamp': datetime.now().isoformat(),
            **kwargs
        }
        
        # Log performance data
        perf_data = {
            'stage': stage_name,
            'duration': duration,
            'success': success,
            'system_metrics': self._get_system_metrics(),
            **kwargs
        }
        
        self.performance_logger.info(json.dumps(perf_data))
        
        # Log system metrics at stage end
        self._log_system_metrics(f"stage_end_{stage_name}")
        
        del self.start_times[stage_name]
    
    def _get_system_metrics(self) -> Dict[str, Any]:
        """Get current system metrics."""
        try:
            return {
                'cpu_percent': psutil.cpu_percent(),
                'memory_percent': psutil.virtual_memory().percent,
                'memory_available_gb': psutil.virtual_memory().available / (1024**3),
                'disk_usage_percent': psutil.disk_usage('/').percent
            }
        except Exception as e:
            self.logger.warning(f"Failed to get system metrics: {e}")
            return {}
    
    def _log_system_metrics(self, context: str):
        """Log system metrics with context."""
        metrics = self._get_system_metrics()
        if metrics:
            self.logger.debug(f"System metrics ({context}): {metrics}")
    
    def log_data_quality(self, stage: str, metrics: Dict[str, Any]):
        """Log data quality metrics."""
        self.logger.info(f"📊 Data Quality - {stage}: {metrics}")
        
        # Store in performance metrics
        if stage not in self.metrics:
            self.metrics[stage] = {}
        self.metrics[stage]['data_quality'] = metrics
    
    def log_record_count(self, stage: str, dataset: str, count: int):
        """Log record count for a dataset."""
        self.logger.info(f"📈 Record Count - {stage}.{dataset}: {count:,}")
        
        # Store in performance metrics
        if stage not in self.metrics:
            self.metrics[stage] = {}
        if 'record_counts' not in self.metrics[stage]:
            self.metrics[stage]['record_counts'] = {}
        self.metrics[stage]['record_counts'][dataset] = count
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get complete performance summary."""
        total_duration = sum(
            stage_metrics.get('duration', 0) 
            for stage_metrics in self.metrics.values()
        )
        
        return {
            'total_duration': total_duration,
            'stages': self.metrics,
            'system_metrics': self._get_system_metrics(),
            'timestamp': datetime.now().isoformat()
        }
    
    def save_performance_report(self, output_path: str):
        """Save performance report to file."""
        summary = self.get_performance_summary()
        
        with open(output_path, 'w') as f:
            json.dump(summary, f, indent=2)
        
        self.logger.info(f"Performance report saved to {output_path}")

class PerformanceMonitor:
    """
    Decorator-based performance monitoring.
    """
    
    def __init__(self, logger: PipelineLogger):
        """Initialize performance monitor."""
        self.logger = logger
    
    def monitor_stage(self, stage_name: str):
        """Decorator to monitor pipeline stage performance."""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                self.logger.start_stage(stage_name)
                try:
                    result = func(*args, **kwargs)
                    self.logger.end_stage(stage_name, success=True)
                    return result
                except Exception as e:
                    self.logger.end_stage(stage_name, success=False, error=str(e))
                    self.logger.logger.error(f"Stage {stage_name} failed: {str(e)}")
                    self.logger.logger.error(traceback.format_exc())
                    raise
            return wrapper
        return decorator
    
    def monitor_function(self, func_name: Optional[str] = None):
        """Decorator to monitor individual function performance."""
        def decorator(func):
            name = func_name or func.__name__
            
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    duration = time.time() - start_time
                    self.logger.logger.debug(f"Function {name} completed in {duration:.3f}s")
                    return result
                except Exception as e:
                    duration = time.time() - start_time
                    self.logger.logger.error(f"Function {name} failed after {duration:.3f}s: {str(e)}")
                    raise
            return wrapper
        return decorator

class ErrorHandler:
    """
    Centralized error handling and recovery.
    """
    
    def __init__(self, logger: PipelineLogger, config: Dict[str, Any]):
        """Initialize error handler."""
        self.logger = logger
        self.config = config
        self.error_count = 0
        self.warning_count = 0
    
    def handle_error(self, error: Exception, context: str, critical: bool = False) -> bool:
        """
        Handle pipeline errors with appropriate logging and recovery.
        
        Returns:
            bool: True if pipeline should continue, False if it should stop
        """
        self.error_count += 1
        
        error_msg = f"Error in {context}: {str(error)}"
        
        if critical or not self.config.get('continue_on_warning', True):
            self.logger.logger.critical(error_msg)
            self.logger.logger.critical(traceback.format_exc())
            
            if self.config.get('fail_on_critical_error', True):
                return False
        else:
            self.logger.logger.error(error_msg)
            self.logger.logger.debug(traceback.format_exc())
        
        return True
    
    def handle_warning(self, message: str, context: str):
        """Handle pipeline warnings."""
        self.warning_count += 1
        self.logger.logger.warning(f"Warning in {context}: {message}")
    
    def get_error_summary(self) -> Dict[str, int]:
        """Get error and warning counts."""
        return {
            'errors': self.error_count,
            'warnings': self.warning_count
        }

# Custom logging handler for rotating by size
class RotatingMaxBytes(logging.handlers.RotatingFileHandler):
    """Custom rotating file handler that handles maxBytes properly."""
    pass