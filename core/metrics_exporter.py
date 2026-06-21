#!/usr/bin/env python3
"""
📤 METRICS EXPORTER
Export metrics in multiple formats (CSV, JSON, Parquet)

"Where metrics become actionable insights through versatile export"
"""

import os
import json
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class MetricsExporter:
    """
    Exports metrics to various formats
    
    Supported formats:
    - CSV: Comma-separated values for spreadsheet analysis
    - JSON: JSON format for API integration
    - Parquet: Columnar format for big data pipelines
    """
    
    def __init__(
        self,
        output_directory: str = "exports",
        timestamp_format: str = "%Y%m%d_%H%M%S",
        compression: bool = False,
        include_metadata: bool = True
    ):
        """
        Initialize metrics exporter
        
        Args:
            output_directory: Directory for export files
            timestamp_format: Format for timestamp in filenames
            compression: Enable compression for exports
            include_metadata: Include metadata in exports
        """
        self.output_directory = Path(output_directory)
        self.timestamp_format = timestamp_format
        self.compression = compression
        self.include_metadata = include_metadata
        
        # Create output directory if it doesn't exist
        self.output_directory.mkdir(parents=True, exist_ok=True)
        
        logger.info(
            f"Metrics Exporter initialized: "
            f"output_dir={output_directory}, "
            f"compression={compression}"
        )
    
    def export_metrics(
        self,
        metrics: List[Dict[str, Any]],
        format: str = "csv",
        filename: Optional[str] = None
    ) -> str:
        """
        Export metrics to specified format
        
        Args:
            metrics: List of metric dictionaries
            format: Export format ('csv', 'json', 'parquet')
            filename: Custom filename (without extension)
            
        Returns:
            Path to exported file
        """
        if not metrics:
            logger.warning("No metrics to export")
            return ""
        
        # Generate filename with timestamp
        if filename is None:
            timestamp = datetime.now().strftime(self.timestamp_format)
            filename = f"metrics_{timestamp}"
        
        format = format.lower()
        
        if format == "csv":
            return self._export_csv(metrics, filename)
        elif format == "json":
            return self._export_json(metrics, filename)
        elif format == "parquet":
            return self._export_parquet(metrics, filename)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def _export_csv(self, metrics: List[Dict[str, Any]], filename: str) -> str:
        """Export metrics to CSV format"""
        try:
            import pandas as pd
            
            # Convert metrics to DataFrame
            df = pd.DataFrame(metrics)
            
            # Convert datetime objects to strings
            for col in df.columns:
                if df[col].dtype == 'object':
                    df[col] = df[col].apply(
                        lambda x: x.isoformat() if isinstance(x, datetime) else x
                    )
            
            # Build file path
            file_path = self.output_directory / f"{filename}.csv"
            
            # Export to CSV
            df.to_csv(file_path, index=False)
            
            logger.info(f"Metrics exported to CSV: {file_path}")
            return str(file_path)
            
        except ImportError:
            logger.error("pandas not installed. Cannot export to CSV.")
            raise
    
    def _export_json(self, metrics: List[Dict[str, Any]], filename: str) -> str:
        """Export metrics to JSON format"""
        # Convert datetime objects to strings
        def serialize_datetime(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            elif isinstance(obj, list):
                return [serialize_datetime(item) for item in obj]
            elif isinstance(obj, dict):
                return {k: serialize_datetime(v) for k, v in obj.items()}
            return obj
        
        serialized_metrics = serialize_datetime(metrics)
        
        # Add metadata if enabled
        if self.include_metadata:
            output = {
                'metadata': {
                    'export_timestamp': datetime.now().isoformat(),
                    'metric_count': len(metrics),
                    'format': 'json',
                    'version': '2.0'
                },
                'metrics': serialized_metrics
            }
        else:
            output = serialized_metrics
        
        # Build file path
        file_path = self.output_directory / f"{filename}.json"
        
        # Export to JSON
        with open(file_path, 'w') as f:
            json.dump(output, f, indent=2)
        
        logger.info(f"Metrics exported to JSON: {file_path}")
        return str(file_path)
    
    def _export_parquet(self, metrics: List[Dict[str, Any]], filename: str) -> str:
        """Export metrics to Parquet format"""
        try:
            import pandas as pd
            
            # Convert metrics to DataFrame
            df = pd.DataFrame(metrics)
            
            # Build file path
            file_path = self.output_directory / f"{filename}.parquet"
            
            # Export to Parquet
            compression_type = 'gzip' if self.compression else None
            df.to_parquet(file_path, compression=compression_type, index=False)
            
            logger.info(f"Metrics exported to Parquet: {file_path}")
            return str(file_path)
            
        except ImportError:
            logger.error("pandas and pyarrow not installed. Cannot export to Parquet.")
            raise
    
    def export_multiple_formats(
        self,
        metrics: List[Dict[str, Any]],
        formats: List[str],
        filename: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Export metrics to multiple formats
        
        Args:
            metrics: List of metric dictionaries
            formats: List of export formats
            filename: Custom filename (without extension)
            
        Returns:
            Dictionary mapping format to file path
        """
        results = {}
        
        for format in formats:
            try:
                file_path = self.export_metrics(metrics, format, filename)
                results[format] = file_path
            except Exception as e:
                logger.error(f"Failed to export to {format}: {e}")
                results[format] = f"ERROR: {str(e)}"
        
        return results
    
    def export_portfolio_metrics(
        self,
        portfolio_metrics: Any,
        formats: List[str] = None
    ) -> Dict[str, str]:
        """
        Export PortfolioMetrics objects
        
        Args:
            portfolio_metrics: Single or list of PortfolioMetrics
            formats: List of export formats (defaults to ['csv', 'json'])
            
        Returns:
            Dictionary mapping format to file path
        """
        if formats is None:
            formats = ['csv', 'json']
        
        # Convert to list if single metric
        if not isinstance(portfolio_metrics, list):
            portfolio_metrics = [portfolio_metrics]
        
        # Convert PortfolioMetrics to dictionaries
        from dataclasses import asdict
        
        metrics_dicts = []
        for pm in portfolio_metrics:
            metric_dict = asdict(pm)
            
            # Convert timestamp to string
            if 'timestamp' in metric_dict and isinstance(metric_dict['timestamp'], datetime):
                metric_dict['timestamp'] = metric_dict['timestamp'].isoformat()
            
            metrics_dicts.append(metric_dict)
        
        return self.export_multiple_formats(metrics_dicts, formats)
    
    def get_export_summary(self) -> Dict[str, Any]:
        """Get summary of exports in output directory"""
        if not self.output_directory.exists():
            return {
                'directory': str(self.output_directory),
                'exists': False,
                'files': []
            }
        
        files = []
        for file_path in self.output_directory.iterdir():
            if file_path.is_file():
                files.append({
                    'name': file_path.name,
                    'size': file_path.stat().st_size,
                    'modified': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                    'extension': file_path.suffix
                })
        
        return {
            'directory': str(self.output_directory),
            'exists': True,
            'file_count': len(files),
            'files': files,
            'timestamp': datetime.now().isoformat()
        }
    
    def cleanup_old_exports(self, days_old: int = 30) -> int:
        """
        Delete export files older than specified days
        
        Args:
            days_old: Delete files older than this many days
            
        Returns:
            Number of files deleted
        """
        if not self.output_directory.exists():
            return 0
        
        deleted_count = 0
        cutoff_time = datetime.now().timestamp() - (days_old * 24 * 60 * 60)
        
        for file_path in self.output_directory.iterdir():
            if file_path.is_file():
                if file_path.stat().st_mtime < cutoff_time:
                    file_path.unlink()
                    deleted_count += 1
                    logger.info(f"Deleted old export: {file_path.name}")
        
        logger.info(f"Cleaned up {deleted_count} old export files")
        return deleted_count
