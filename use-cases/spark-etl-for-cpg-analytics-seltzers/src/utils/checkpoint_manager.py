#!/usr/bin/env python3
"""
Checkpoint Manager for Fault Tolerance
======================================

Handles checkpointing, recovery, and fault tolerance for the pipeline.
"""

import os
import json
import pickle
import shutil
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path
import logging
from pyspark.sql import DataFrame
import hashlib

class CheckpointManager:
    """
    Manages pipeline checkpoints for fault tolerance and recovery.
    """
    
    def __init__(self, checkpoint_dir: str, config: Dict[str, Any]):
        """Initialize checkpoint manager."""
        self.checkpoint_dir = Path(checkpoint_dir)
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Create checkpoint directory
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        
        # Checkpoint metadata
        self.metadata_file = self.checkpoint_dir / "checkpoint_metadata.json"
        self.metadata = self._load_metadata()
        
    def _load_metadata(self) -> Dict[str, Any]:
        """Load checkpoint metadata."""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"Failed to load checkpoint metadata: {e}")
        
        return {
            'checkpoints': {},
            'pipeline_runs': [],
            'last_successful_run': None
        }
    
    def _save_metadata(self):
        """Save checkpoint metadata."""
        try:
            with open(self.metadata_file, 'w') as f:
                json.dump(self.metadata, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save checkpoint metadata: {e}")
    
    def _generate_checkpoint_id(self, stage: str, data_hash: str = None) -> str:
        """Generate unique checkpoint ID."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if data_hash:
            return f"{stage}_{timestamp}_{data_hash[:8]}"
        return f"{stage}_{timestamp}"
    
    def _calculate_data_hash(self, df: DataFrame) -> str:
        """Calculate hash of DataFrame for change detection."""
        try:
            # Use DataFrame schema and count as a simple hash
            schema_str = str(df.schema)
            count = df.count()
            hash_input = f"{schema_str}_{count}".encode()
            return hashlib.md5(hash_input).hexdigest()
        except Exception as e:
            self.logger.warning(f"Failed to calculate data hash: {e}")
            return "unknown"
    
    def save_checkpoint(self, stage: str, data: Dict[str, Any], df: Optional[DataFrame] = None) -> str:
        """
        Save checkpoint for a pipeline stage.
        
        Args:
            stage: Pipeline stage name
            data: Dictionary of data to checkpoint
            df: Optional DataFrame to checkpoint
            
        Returns:
            str: Checkpoint ID
        """
        try:
            # Generate checkpoint ID
            data_hash = self._calculate_data_hash(df) if df is not None else None
            checkpoint_id = self._generate_checkpoint_id(stage, data_hash)
            
            # Create checkpoint directory
            checkpoint_path = self.checkpoint_dir / checkpoint_id
            checkpoint_path.mkdir(parents=True, exist_ok=True)
            
            # Save data
            data_file = checkpoint_path / "data.json"
            with open(data_file, 'w') as f:
                # Convert non-serializable objects to strings
                serializable_data = self._make_serializable(data)
                json.dump(serializable_data, f, indent=2)
            
            # Save DataFrame if provided
            if df is not None:
                df_path = checkpoint_path / "dataframe"
                df.write.mode("overwrite").parquet(str(df_path))
                self.logger.info(f"DataFrame checkpointed: {df.count():,} records")
            
            # Update metadata
            self.metadata['checkpoints'][checkpoint_id] = {
                'stage': stage,
                'timestamp': datetime.now().isoformat(),
                'data_hash': data_hash,
                'has_dataframe': df is not None,
                'path': str(checkpoint_path)
            }
            
            self._save_metadata()
            
            self.logger.info(f"✅ Checkpoint saved: {checkpoint_id}")
            return checkpoint_id
            
        except Exception as e:
            self.logger.error(f"Failed to save checkpoint for {stage}: {e}")
            raise
    
    def load_checkpoint(self, checkpoint_id: str) -> Dict[str, Any]:
        """
        Load checkpoint data.
        
        Args:
            checkpoint_id: Checkpoint ID to load
            
        Returns:
            Dict containing checkpoint data and optional DataFrame
        """
        try:
            if checkpoint_id not in self.metadata['checkpoints']:
                raise ValueError(f"Checkpoint not found: {checkpoint_id}")
            
            checkpoint_info = self.metadata['checkpoints'][checkpoint_id]
            checkpoint_path = Path(checkpoint_info['path'])
            
            if not checkpoint_path.exists():
                raise FileNotFoundError(f"Checkpoint directory not found: {checkpoint_path}")
            
            # Load data
            data_file = checkpoint_path / "data.json"
            with open(data_file, 'r') as f:
                data = json.load(f)
            
            result = {'data': data}
            
            # Load DataFrame if available
            if checkpoint_info['has_dataframe']:
                from pyspark.sql import SparkSession
                spark = SparkSession.getActiveSession()
                if spark:
                    df_path = checkpoint_path / "dataframe"
                    df = spark.read.parquet(str(df_path))
                    result['dataframe'] = df
                    self.logger.info(f"DataFrame loaded: {df.count():,} records")
                else:
                    self.logger.warning("No active Spark session for DataFrame loading")
            
            self.logger.info(f"✅ Checkpoint loaded: {checkpoint_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to load checkpoint {checkpoint_id}: {e}")
            raise
    
    def _make_serializable(self, obj: Any) -> Any:
        """Convert object to JSON-serializable format."""
        if isinstance(obj, dict):
            return {k: self._make_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._make_serializable(item) for item in obj]
        elif isinstance(obj, (str, int, float, bool, type(None))):
            return obj
        else:
            return str(obj)
    
    def list_checkpoints(self, stage: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List available checkpoints.
        
        Args:
            stage: Optional stage filter
            
        Returns:
            List of checkpoint information
        """
        checkpoints = []
        
        for checkpoint_id, info in self.metadata['checkpoints'].items():
            if stage is None or info['stage'] == stage:
                checkpoints.append({
                    'id': checkpoint_id,
                    'stage': info['stage'],
                    'timestamp': info['timestamp'],
                    'has_dataframe': info['has_dataframe']
                })
        
        # Sort by timestamp (newest first)
        checkpoints.sort(key=lambda x: x['timestamp'], reverse=True)
        return checkpoints
    
    def get_latest_checkpoint(self, stage: str) -> Optional[str]:
        """
        Get the latest checkpoint ID for a stage.
        
        Args:
            stage: Pipeline stage name
            
        Returns:
            Latest checkpoint ID or None if not found
        """
        stage_checkpoints = self.list_checkpoints(stage)
        return stage_checkpoints[0]['id'] if stage_checkpoints else None
    
    def cleanup_old_checkpoints(self, keep_count: int = 5):
        """
        Clean up old checkpoints, keeping only the most recent ones.
        
        Args:
            keep_count: Number of checkpoints to keep per stage
        """
        try:
            stages = set(info['stage'] for info in self.metadata['checkpoints'].values())
            
            for stage in stages:
                stage_checkpoints = self.list_checkpoints(stage)
                
                if len(stage_checkpoints) > keep_count:
                    to_delete = stage_checkpoints[keep_count:]
                    
                    for checkpoint in to_delete:
                        self.delete_checkpoint(checkpoint['id'])
                    
                    self.logger.info(f"Cleaned up {len(to_delete)} old checkpoints for stage {stage}")
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup checkpoints: {e}")
    
    def delete_checkpoint(self, checkpoint_id: str):
        """
        Delete a specific checkpoint.
        
        Args:
            checkpoint_id: Checkpoint ID to delete
        """
        try:
            if checkpoint_id not in self.metadata['checkpoints']:
                self.logger.warning(f"Checkpoint not found for deletion: {checkpoint_id}")
                return
            
            checkpoint_info = self.metadata['checkpoints'][checkpoint_id]
            checkpoint_path = Path(checkpoint_info['path'])
            
            # Remove directory
            if checkpoint_path.exists():
                shutil.rmtree(checkpoint_path)
            
            # Remove from metadata
            del self.metadata['checkpoints'][checkpoint_id]
            self._save_metadata()
            
            self.logger.info(f"✅ Checkpoint deleted: {checkpoint_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to delete checkpoint {checkpoint_id}: {e}")
    
    def record_pipeline_run(self, run_id: str, status: str, stages_completed: List[str], 
                          error_message: Optional[str] = None):
        """
        Record pipeline run information.
        
        Args:
            run_id: Unique run identifier
            status: Run status (success, failed, partial)
            stages_completed: List of completed stages
            error_message: Optional error message for failed runs
        """
        run_info = {
            'run_id': run_id,
            'timestamp': datetime.now().isoformat(),
            'status': status,
            'stages_completed': stages_completed,
            'error_message': error_message
        }
        
        self.metadata['pipeline_runs'].append(run_info)
        
        if status == 'success':
            self.metadata['last_successful_run'] = run_info
        
        # Keep only last 20 runs
        if len(self.metadata['pipeline_runs']) > 20:
            self.metadata['pipeline_runs'] = self.metadata['pipeline_runs'][-20:]
        
        self._save_metadata()
        self.logger.info(f"Pipeline run recorded: {run_id} ({status})")
    
    def get_recovery_point(self) -> Optional[Dict[str, str]]:
        """
        Get the best recovery point for pipeline restart.
        
        Returns:
            Dictionary mapping stage names to checkpoint IDs, or None
        """
        if not self.metadata['last_successful_run']:
            return None
        
        # Get latest checkpoint for each stage
        recovery_point = {}
        stages = set(info['stage'] for info in self.metadata['checkpoints'].values())
        
        for stage in stages:
            latest_checkpoint = self.get_latest_checkpoint(stage)
            if latest_checkpoint:
                recovery_point[stage] = latest_checkpoint
        
        return recovery_point if recovery_point else None
    
    def is_checkpoint_valid(self, checkpoint_id: str) -> bool:
        """
        Check if a checkpoint is valid and accessible.
        
        Args:
            checkpoint_id: Checkpoint ID to validate
            
        Returns:
            True if checkpoint is valid
        """
        try:
            if checkpoint_id not in self.metadata['checkpoints']:
                return False
            
            checkpoint_info = self.metadata['checkpoints'][checkpoint_id]
            checkpoint_path = Path(checkpoint_info['path'])
            
            # Check if directory exists and has required files
            if not checkpoint_path.exists():
                return False
            
            data_file = checkpoint_path / "data.json"
            if not data_file.exists():
                return False
            
            # If DataFrame checkpoint, check parquet files
            if checkpoint_info['has_dataframe']:
                df_path = checkpoint_path / "dataframe"
                if not df_path.exists():
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating checkpoint {checkpoint_id}: {e}")
            return False
    
    def get_checkpoint_summary(self) -> Dict[str, Any]:
        """Get summary of checkpoint status."""
        total_checkpoints = len(self.metadata['checkpoints'])
        valid_checkpoints = sum(1 for cp_id in self.metadata['checkpoints'] 
                              if self.is_checkpoint_valid(cp_id))
        
        stages = set(info['stage'] for info in self.metadata['checkpoints'].values())
        
        return {
            'total_checkpoints': total_checkpoints,
            'valid_checkpoints': valid_checkpoints,
            'stages_with_checkpoints': list(stages),
            'last_successful_run': self.metadata['last_successful_run'],
            'total_pipeline_runs': len(self.metadata['pipeline_runs'])
        }