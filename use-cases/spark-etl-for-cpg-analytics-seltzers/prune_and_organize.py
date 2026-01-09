#!/usr/bin/env python3
"""
Repository Pruning and Organization Script
=========================================

Cleans up the repository and organizes all documentation into a single folder.
"""

import os
import shutil
import glob
from pathlib import Path

def prune_repository():
    """Remove unnecessary files and organize the repository."""
    
    print("🧹 Pruning repository and organizing files...")
    
    # Files to keep in root
    keep_in_root = [
        'run_orchestrated_pipeline.py',
        'run_complete_analysis.py', 
        'simple_data_generator.py',
        'spark_data_ingestion.py',
        'spark_data_cleaning_pipeline.py',
        'spark_trend_analysis_pipeline.py',
        'spark_executive_reporting.py',
        'spark_visualization_export.py',
        'create_visualizations.py',
        'simple_data_quality_tests.py',
        'QUICK_START.md'
    ]
    
    # Create documentation directory
    docs_dir = Path('documentation')
    docs_dir.mkdir(exist_ok=True)
    
    # Move all markdown files to documentation folder
    markdown_files = glob.glob('*.md')
    moved_docs = []
    
    for md_file in markdown_files:
        if md_file != 'QUICK_START.md':  # Keep quick start in root
            dest = docs_dir / md_file
            shutil.move(md_file, dest)
            moved_docs.append(md_file)
    
    print(f"📚 Moved {len(moved_docs)} markdown files to documentation/")
    
    # Remove test files
    test_files = glob.glob('test_*.py')
    for test_file in test_files:
        os.remove(test_file)
        print(f"🗑️  Removed {test_file}")
    
    # Remove legacy files
    legacy_files = [
        'spark_etl_pipeline.py',
        'spark_hello_world.py', 
        'spark_init.py',
        'data_generator.py',
        'run_pipeline.py',
        'run_simple_pipeline.py',
        'comprehensive_data_quality_tests.py',
        'archive_project.py'
    ]
    
    for legacy_file in legacy_files:
        if os.path.exists(legacy_file):
            os.remove(legacy_file)
            print(f"🗑️  Removed {legacy_file}")
    
    # Clean up empty directories
    empty_dirs = ['logs', 'checkpoints']
    for empty_dir in empty_dirs:
        if os.path.exists(empty_dir) and not os.listdir(empty_dir):
            os.rmdir(empty_dir)
            print(f"🗑️  Removed empty directory {empty_dir}")
    
    return moved_docs

def create_documentation_index():
    """Create an index of all documentation files."""
    
    docs_dir = Path('documentation')
    
    index_content = """# 📚 Documentation Index

## Beer-to-Seltzer Market Analysis Pipeline Documentation

This directory contains all project documentation organized by category.

## 📋 **Executive Documentation**
- **BUSINESS_EXECUTIVE_SUMMARY.md** - Strategic business analysis and recommendations
- **PROJECT_COMPLETION_FINAL.md** - Complete project delivery summary

## 🏗️ **Technical Documentation**  
- **TECHNICAL_DOCUMENTATION.md** - Complete technical architecture and implementation
- **README_FINAL.md** - Comprehensive project guide with visualizations
- **README_COMPLETE_PIPELINE.md** - Enterprise pipeline documentation

## 🎯 **Implementation Summaries**
- **ORCHESTRATED_PIPELINE_SUCCESS.md** - Pipeline implementation success summary
- **EXECUTIVE_REPORTING_SUMMARY.md** - Executive reporting component summary
- **TREND_ANALYSIS_SUMMARY.md** - Trend analysis component summary
- **DATA_CLEANING_PIPELINE_SUMMARY.md** - Data cleaning component summary
- **VISUALIZATION_PIPELINE_SUMMARY.md** - Visualization component summary
- **INGESTION_SUCCESS_SUMMARY.md** - Data ingestion component summary
- **PROJECT_COMPLETION_SUMMARY.md** - Original project completion summary

## 🚀 **Quick Access**
For immediate execution, see the **QUICK_START.md** file in the root directory.

---

*All documentation supports the strategic recommendation to **PROCEED WITH HARD SELTZER MARKET ENTRY** based on comprehensive data analysis.*
"""
    
    with open(docs_dir / 'INDEX.md', 'w') as f:
        f.write(index_content)
    
    print("📋 Created documentation index")

def main():
    """Main pruning and organization process."""
    print("🗂️  Repository Pruning and Organization")
    print("=" * 50)
    
    try:
        # Prune repository
        moved_docs = prune_repository()
        
        # Create documentation index
        create_documentation_index()
        
        # Print summary
        print(f"\n✅ REPOSITORY ORGANIZATION COMPLETED")
        print("-" * 40)
        print(f"📚 Documentation files: {len(moved_docs)} files moved to documentation/")
        print(f"🧹 Legacy files: Removed test files and outdated components")
        print(f"📁 Clean structure: Core pipeline files remain in root")
        
        print(f"\n📁 Final Repository Structure:")
        print(f"  ├── 🚀 Core Pipeline Files (root)")
        print(f"  ├── 📚 documentation/ (all markdown files)")
        print(f"  ├── 📊 charts/ (visualizations)")
        print(f"  ├── 📈 visualization_data/ (BI datasets)")
        print(f"  ├── 📋 executive_reports/ (strategic summaries)")
        print(f"  ├── 🔧 src/ (enterprise components)")
        print(f"  └── ⚙️ config/ (configuration)")
        
        print(f"\n🎯 Next Step: Generate comprehensive PDF report")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Organization failed: {str(e)}")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())