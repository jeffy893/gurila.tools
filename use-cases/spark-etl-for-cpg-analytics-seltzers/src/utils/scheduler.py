#!/usr/bin/env python3
"""
Pipeline Scheduler
=================

Handles scheduled execution of the pipeline with cron-like functionality.
"""

import os
import sys
import time
import threading
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Callable
from pathlib import Path
import subprocess
import json

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))

try:
    import schedule
    SCHEDULE_AVAILABLE = True
except ImportError:
    SCHEDULE_AVAILABLE = False
    print("⚠️  Schedule library not available. Installing...")
    os.system("pip3.10 install schedule")
    try:
        import schedule
        SCHEDULE_AVAILABLE = True
    except ImportError:
        SCHEDULE_AVAILABLE = False

class PipelineScheduler:
    """
    Scheduler for automated pipeline execution.
    """
    
    def __init__(self, config: Dict[str, Any], pipeline_script: str = "src/pipelines/master_pipeline.py"):
        """Initialize pipeline scheduler."""
        self.config = config
        self.pipeline_script = pipeline_script
        self.logger = logging.getLogger(__name__)
        
        # Scheduling configuration
        self.schedule_config = config.get('scheduling', {})
        self.enabled = self.schedule_config.get('enabled', False)
        self.cron_expression = self.schedule_config.get('cron_expression', '0 2 * * 1')  # Weekly Monday 2 AM
        self.timezone = self.schedule_config.get('timezone', 'UTC')
        self.retry_attempts = self.schedule_config.get('retry_attempts', 3)
        self.retry_delay = self.schedule_config.get('retry_delay', 300)  # 5 minutes
        
        # Execution tracking
        self.execution_history = []
        self.is_running = False
        self.current_execution = None
        
        # Setup logging
        self._setup_scheduler_logging()
        
        if not SCHEDULE_AVAILABLE:
            self.logger.warning("Schedule library not available. Scheduler functionality disabled.")
    
    def _setup_scheduler_logging(self):
        """Setup scheduler-specific logging."""
        log_dir = Path(self.config.get('logging', {}).get('log_directory', 'logs'))
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # Scheduler log file
        scheduler_log = log_dir / 'scheduler.log'
        
        # Create file handler
        file_handler = logging.FileHandler(scheduler_log)
        file_handler.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        
        # Add handler to logger
        self.logger.addHandler(file_handler)
        self.logger.setLevel(logging.INFO)
    
    def _parse_cron_expression(self, cron_expr: str) -> Dict[str, Any]:
        """
        Parse cron expression into schedule parameters.
        
        Format: minute hour day_of_month month day_of_week
        Example: "0 2 * * 1" = Every Monday at 2:00 AM
        """
        parts = cron_expr.split()
        if len(parts) != 5:
            raise ValueError(f"Invalid cron expression: {cron_expr}")
        
        minute, hour, day_of_month, month, day_of_week = parts
        
        return {
            'minute': minute,
            'hour': hour,
            'day_of_month': day_of_month,
            'month': month,
            'day_of_week': day_of_week
        }
    
    def _setup_schedule(self):
        """Setup schedule based on cron expression."""
        if not SCHEDULE_AVAILABLE:
            self.logger.error("Schedule library not available")
            return False
        
        try:
            cron_parts = self._parse_cron_expression(self.cron_expression)
            
            # Convert cron to schedule format
            if cron_parts['day_of_week'] != '*':
                # Weekly schedule
                day_map = {
                    '0': 'sunday', '1': 'monday', '2': 'tuesday', '3': 'wednesday',
                    '4': 'thursday', '5': 'friday', '6': 'saturday'
                }
                
                day_name = day_map.get(cron_parts['day_of_week'], 'monday')
                time_str = f"{cron_parts['hour'].zfill(2)}:{cron_parts['minute'].zfill(2)}"
                
                getattr(schedule.every(), day_name).at(time_str).do(self._execute_pipeline)
                self.logger.info(f"Scheduled pipeline for every {day_name} at {time_str}")
                
            elif cron_parts['day_of_month'] != '*':
                # Monthly schedule (simplified - runs on specified day each month)
                time_str = f"{cron_parts['hour'].zfill(2)}:{cron_parts['minute'].zfill(2)}"
                schedule.every().day.at(time_str).do(self._check_monthly_execution, cron_parts['day_of_month'])
                self.logger.info(f"Scheduled pipeline for day {cron_parts['day_of_month']} of each month at {time_str}")
                
            elif cron_parts['hour'] != '*':
                # Daily schedule
                time_str = f"{cron_parts['hour'].zfill(2)}:{cron_parts['minute'].zfill(2)}"
                schedule.every().day.at(time_str).do(self._execute_pipeline)
                self.logger.info(f"Scheduled pipeline daily at {time_str}")
                
            else:
                # Hourly schedule
                schedule.every().hour.at(f":{cron_parts['minute'].zfill(2)}").do(self._execute_pipeline)
                self.logger.info(f"Scheduled pipeline every hour at minute {cron_parts['minute']}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to setup schedule: {e}")
            return False
    
    def _check_monthly_execution(self, target_day: str):
        """Check if today matches the target day for monthly execution."""
        if datetime.now().day == int(target_day):
            self._execute_pipeline()
    
    def _execute_pipeline(self):
        """Execute the pipeline with error handling and retry logic."""
        if self.is_running:
            self.logger.warning("Pipeline already running, skipping execution")
            return
        
        execution_id = f"scheduled_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.current_execution = {
            'id': execution_id,
            'start_time': datetime.now(),
            'status': 'running',
            'attempts': 0,
            'error_message': None
        }
        
        self.is_running = True
        self.logger.info(f"🚀 Starting scheduled pipeline execution: {execution_id}")
        
        for attempt in range(1, self.retry_attempts + 1):
            try:
                self.current_execution['attempts'] = attempt
                
                if attempt > 1:
                    self.logger.info(f"Retry attempt {attempt}/{self.retry_attempts}")
                    time.sleep(self.retry_delay)
                
                # Execute pipeline
                result = self._run_pipeline_subprocess()
                
                if result['success']:
                    self.current_execution['status'] = 'success'
                    self.current_execution['end_time'] = datetime.now()
                    self.logger.info(f"✅ Pipeline execution completed successfully: {execution_id}")
                    break
                else:
                    raise Exception(result['error'])
                    
            except Exception as e:
                error_msg = str(e)
                self.logger.error(f"❌ Pipeline execution failed (attempt {attempt}): {error_msg}")
                
                if attempt == self.retry_attempts:
                    # Final attempt failed
                    self.current_execution['status'] = 'failed'
                    self.current_execution['error_message'] = error_msg
                    self.current_execution['end_time'] = datetime.now()
                    
                    # Send notification if configured
                    self._send_failure_notification(execution_id, error_msg)
        
        # Record execution history
        self.execution_history.append(self.current_execution.copy())
        
        # Keep only last 50 executions
        if len(self.execution_history) > 50:
            self.execution_history = self.execution_history[-50:]
        
        # Save execution history
        self._save_execution_history()
        
        self.is_running = False
        self.current_execution = None
    
    def _run_pipeline_subprocess(self) -> Dict[str, Any]:
        """Run pipeline as subprocess."""
        try:
            # Prepare command
            cmd = [
                'python3.10',
                self.pipeline_script,
                '--config', 'config/pipeline_config.yaml'
            ]
            
            # Execute subprocess
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=3600  # 1 hour timeout
            )
            
            if result.returncode == 0:
                return {'success': True, 'output': result.stdout}
            else:
                return {'success': False, 'error': result.stderr}
                
        except subprocess.TimeoutExpired:
            return {'success': False, 'error': 'Pipeline execution timed out'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _send_failure_notification(self, execution_id: str, error_message: str):
        """Send failure notification if configured."""
        error_config = self.config.get('error_handling', {})
        
        if error_config.get('notification_enabled', False):
            email = error_config.get('notification_email')
            
            if email:
                # Simple notification (would need email setup in production)
                self.logger.info(f"Notification would be sent to {email} for failed execution {execution_id}")
                
                # In production, implement actual email sending
                # self._send_email_notification(email, execution_id, error_message)
    
    def _save_execution_history(self):
        """Save execution history to file."""
        try:
            history_file = Path('logs/execution_history.json')
            
            # Convert datetime objects to strings for JSON serialization
            serializable_history = []
            for execution in self.execution_history:
                exec_copy = execution.copy()
                for key in ['start_time', 'end_time']:
                    if key in exec_copy and exec_copy[key]:
                        exec_copy[key] = exec_copy[key].isoformat()
                serializable_history.append(exec_copy)
            
            with open(history_file, 'w') as f:
                json.dump(serializable_history, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Failed to save execution history: {e}")
    
    def start_scheduler(self):
        """Start the scheduler in a separate thread."""
        if not self.enabled:
            self.logger.info("Scheduler disabled in configuration")
            return False
        
        if not SCHEDULE_AVAILABLE:
            self.logger.error("Schedule library not available")
            return False
        
        if not self._setup_schedule():
            return False
        
        self.logger.info("🕐 Starting pipeline scheduler...")
        
        # Run scheduler in separate thread
        def run_scheduler():
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        
        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()
        
        self.logger.info("✅ Pipeline scheduler started successfully")
        return True
    
    def execute_now(self) -> bool:
        """Execute pipeline immediately (manual trigger)."""
        if self.is_running:
            self.logger.warning("Pipeline already running")
            return False
        
        self.logger.info("🚀 Manual pipeline execution triggered")
        
        # Run in separate thread to avoid blocking
        execution_thread = threading.Thread(target=self._execute_pipeline, daemon=True)
        execution_thread.start()
        
        return True
    
    def get_status(self) -> Dict[str, Any]:
        """Get current scheduler status."""
        return {
            'enabled': self.enabled,
            'is_running': self.is_running,
            'current_execution': self.current_execution,
            'next_run': self._get_next_run_time(),
            'execution_count': len(self.execution_history),
            'last_execution': self.execution_history[-1] if self.execution_history else None
        }
    
    def _get_next_run_time(self) -> Optional[str]:
        """Get next scheduled run time."""
        if not SCHEDULE_AVAILABLE or not self.enabled:
            return None
        
        try:
            next_run = schedule.next_run()
            return next_run.isoformat() if next_run else None
        except:
            return None
    
    def get_execution_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent execution history."""
        return self.execution_history[-limit:] if self.execution_history else []
    
    def stop_scheduler(self):
        """Stop the scheduler."""
        if SCHEDULE_AVAILABLE:
            schedule.clear()
        self.logger.info("🛑 Pipeline scheduler stopped")

class SchedulerCLI:
    """
    Command-line interface for scheduler management.
    """
    
    def __init__(self, config_path: str = "config/pipeline_config.yaml"):
        """Initialize scheduler CLI."""
        from utils.config_manager import get_config_manager
        
        self.config_manager = get_config_manager(config_path)
        self.config = self.config_manager.config
        self.scheduler = PipelineScheduler(self.config)
    
    def start(self):
        """Start scheduler daemon."""
        print("🕐 Starting pipeline scheduler...")
        
        if self.scheduler.start_scheduler():
            print("✅ Scheduler started successfully")
            print(f"📅 Schedule: {self.scheduler.cron_expression}")
            print(f"🔄 Retry attempts: {self.scheduler.retry_attempts}")
            
            try:
                # Keep main thread alive
                while True:
                    time.sleep(10)
                    status = self.scheduler.get_status()
                    if status['is_running']:
                        print(f"⏳ Pipeline running: {status['current_execution']['id']}")
            except KeyboardInterrupt:
                print("\n🛑 Stopping scheduler...")
                self.scheduler.stop_scheduler()
        else:
            print("❌ Failed to start scheduler")
    
    def status(self):
        """Show scheduler status."""
        status = self.scheduler.get_status()
        
        print("📊 SCHEDULER STATUS")
        print("=" * 50)
        print(f"Enabled: {status['enabled']}")
        print(f"Currently Running: {status['is_running']}")
        print(f"Next Run: {status['next_run'] or 'Not scheduled'}")
        print(f"Total Executions: {status['execution_count']}")
        
        if status['current_execution']:
            exec_info = status['current_execution']
            print(f"\nCurrent Execution:")
            print(f"  ID: {exec_info['id']}")
            print(f"  Status: {exec_info['status']}")
            print(f"  Attempts: {exec_info['attempts']}")
        
        if status['last_execution']:
            last_exec = status['last_execution']
            print(f"\nLast Execution:")
            print(f"  ID: {last_exec['id']}")
            print(f"  Status: {last_exec['status']}")
            print(f"  Attempts: {last_exec['attempts']}")
    
    def execute(self):
        """Execute pipeline now."""
        print("🚀 Triggering immediate pipeline execution...")
        
        if self.scheduler.execute_now():
            print("✅ Pipeline execution started")
        else:
            print("❌ Failed to start pipeline execution")
    
    def history(self, limit: int = 10):
        """Show execution history."""
        history = self.scheduler.get_execution_history(limit)
        
        print(f"📋 EXECUTION HISTORY (Last {len(history)} runs)")
        print("=" * 80)
        
        for execution in reversed(history):  # Show newest first
            status_icon = "✅" if execution['status'] == 'success' else "❌"
            print(f"{status_icon} {execution['id']} - {execution['status']} (Attempts: {execution['attempts']})")
            
            if execution.get('error_message'):
                print(f"    Error: {execution['error_message']}")

def main():
    """Main CLI function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Pipeline Scheduler Management')
    parser.add_argument('command', choices=['start', 'status', 'execute', 'history'],
                       help='Scheduler command')
    parser.add_argument('--config', default='config/pipeline_config.yaml',
                       help='Configuration file path')
    parser.add_argument('--limit', type=int, default=10,
                       help='Limit for history command')
    
    args = parser.parse_args()
    
    try:
        cli = SchedulerCLI(args.config)
        
        if args.command == 'start':
            cli.start()
        elif args.command == 'status':
            cli.status()
        elif args.command == 'execute':
            cli.execute()
        elif args.command == 'history':
            cli.history(args.limit)
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()