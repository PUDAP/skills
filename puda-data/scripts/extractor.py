"""
puda-data Phase 1: Data Extractor

Extract experimental data from PUDA database.
Supports CV, OCV, CA, PEIS, GEIS and other measurement types.
"""

import sqlite3
import json
import pandas as pd
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any

# Database path
DB_PATH = Path("/home/bears/.openclaw/workspace/puda.db")

# Column names for different measurement types
COLUMN_MAPPING = {
    "CV": ["potential", "current", "time", "extra", "flag"],
    "OCV": ["potential", "current", "time", "extra", "flag"],
    "CA": ["time", "current", "voltage", "extra", "flag"],
    "PEIS": ["frequency", "Z_real", "Z_imag", "phase", "flag"],
    "GEIS": ["frequency", "Z_real", "Z_imag", "phase", "flag"],
    "CP": ["time", "current", "voltage", "extra", "flag"],
}


def _get_connection():
    """Get database connection."""
    return sqlite3.connect(DB_PATH)


def extract_measurement_data(run_id: str, command_name: str) -> pd.DataFrame:
    """
    Extract measurement data for a given run and command type.
    
    Args:
        run_id: The run identifier
        command_name: Command type (CV, OCV, CA, PEIS, etc.)
    
    Returns:
        DataFrame with measurement data
    """
    conn = _get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT payload FROM command_log WHERE run_id=? AND command_name=?",
            (run_id, command_name)
        )
        row = cursor.fetchone()
        
        if not row:
            return pd.DataFrame()
        
        payload = json.loads(row[0])
        data = payload.get("response", {}).get("data", {})
        
        if not data or "0" not in data:
            return pd.DataFrame()
        
        cv_data = data["0"]
        
        # Get column names for this command type
        columns = COLUMN_MAPPING.get(command_name, [f"col_{i}" for i in range(len(cv_data[0]))])
        
        df = pd.DataFrame(cv_data, columns=columns)
        return df
    
    finally:
        conn.close()


def get_runs_by_type(command_name: str, limit: int = 10) -> List[Tuple[str, int, str]]:
    """
    List runs containing a specific command type.
    
    Args:
        command_name: Command type to search for
        limit: Maximum number of results
    
    Returns:
        List of (run_id, step_number, created_at) tuples
    """
    conn = _get_connection()
    try:
        query = """
            SELECT run_id, step_number, created_at 
            FROM command_log 
            WHERE command_name=? 
            ORDER BY created_at DESC 
            LIMIT ?
        """
        cursor = conn.cursor()
        cursor.execute(query, (command_name, limit))
        return cursor.fetchall()
    finally:
        conn.close()


def get_latest_measurements(command_name: str, limit: int = 5) -> List[Tuple[str, pd.DataFrame]]:
    """
    Get most recent measurement data.
    
    Args:
        command_name: Command type (CV, OCV, etc.)
        limit: Number of recent measurements to retrieve
    
    Returns:
        List of (run_id, DataFrame) tuples
    """
    runs = get_runs_by_type(command_name, limit)
    results = []
    
    for run_id, step, created in runs:
        df = extract_measurement_data(run_id, command_name)
        if not df.empty:
            results.append((run_id, df))
    
    return results


def get_run_info(run_id: str) -> Dict[str, Any]:
    """
    Get experiment metadata for a run.
    
    Args:
        run_id: The run identifier
    
    Returns:
        Dictionary with run information
    """
    conn = _get_connection()
    try:
        # Get run info
        cursor = conn.cursor()
        cursor.execute("SELECT run_id, protocol_id, created_at FROM run WHERE run_id=?", (run_id,))
        run_row = cursor.fetchone()
        
        if not run_row:
            return {}
        
        # Get all commands in this run
        cursor.execute(
            "SELECT step_number, command_name FROM command_log WHERE run_id=? ORDER BY step_number",
            (run_id,)
        )
        commands = cursor.fetchall()
        
        return {
            "run_id": run_row[0],
            "protocol_id": run_row[1],
            "created_at": run_row[2],
            "commands": [{"step": c[0], "name": c[1]} for c in commands]
        }
    finally:
        conn.close()


def get_protocol(protocol_id: str) -> Dict[str, Any]:
    """
    Get protocol definition.
    
    Args:
        protocol_id: The protocol identifier
    
    Returns:
        Dictionary with protocol information
    """
    conn = _get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT protocol_id, user_id, username, description, commands, created_at FROM protocol WHERE protocol_id=?",
            (protocol_id,)
        )
        row = cursor.fetchone()
        
        if not row:
            return {}
        
        return {
            "protocol_id": row[0],
            "user_id": row[1],
            "username": row[2],
            "description": row[3],
            "commands": json.loads(row[4]) if row[4] else [],
            "created_at": row[5]
        }
    finally:
        conn.close()


def list_all_runs(limit: int = 20) -> List[Dict[str, Any]]:
    """
    List all runs with summary info.
    
    Args:
        limit: Maximum number of results
    
    Returns:
        List of run summaries
    """
    conn = _get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT r.run_id, r.protocol_id, r.created_at, 
                   GROUP_CONCAT(cl.command_name) as commands
            FROM run r
            LEFT JOIN command_log cl ON r.run_id = cl.run_id
            GROUP BY r.run_id
            ORDER BY r.created_at DESC
            LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        results = []
        
        for row in rows:
            results.append({
                "run_id": row[0],
                "protocol_id": row[1],
                "created_at": row[2],
                "commands": row[3].split(",") if row[3] else []
            })
        
        return results
    finally:
        conn.close()


# Quick test
if __name__ == "__main__":
    print("=== Testing Extractor ===\n")
    
    # Get latest CV
    print("1. Latest CV runs:")
    runs = get_runs_by_type("CV", 3)
    for run_id, step, created in runs:
        print(f"   {run_id} (step {step}) - {created}")
    
    # Get latest measurement
    print("\n2. Latest CV data:")
    measurements = get_latest_measurements("CV", 1)
    if measurements:
        run_id, df = measurements[0]
        print(f"   Run: {run_id}")
        print(f"   Points: {len(df)}")
        print(f"   Columns: {list(df.columns)}")
        print(f"   Potential range: {df['potential'].min():.3f}V to {df['potential'].max():.3f}V")
        print(f"   Current range: {df['current'].min():.6f}A to {df['current'].max():.6f}A")
        print(f"\n   First 3 rows:")
        print(df.head(3).to_string())
    
    # Get run info
    print("\n3. Run info:")
    if runs:
        info = get_run_info(runs[0][0])
        print(f"   Run: {info.get('run_id')}")
        print(f"   Protocol: {info.get('protocol_id')}")
        print(f"   Commands: {[c['name'] for c in info.get('commands', [])]}")
