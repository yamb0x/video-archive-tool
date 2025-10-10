"""State management for resume capability"""

import sqlite3
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid


class StateManager:
    """Manage processing state and resume capability using SQLite"""

    def __init__(self, db_path: str = "config/state.db"):
        """
        Initialize state manager

        Args:
            db_path: Path to SQLite database file
        """
        self.logger = logging.getLogger(__name__)
        self.db_path = Path(db_path)

        # Ensure config directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self.conn = None
        self.session_id = None

        self._init_database()

    def _init_database(self):
        """Initialize database with schema"""
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row  # Enable column access by name

        # Create tables
        self._create_tables()

        self.logger.info(f"Database initialized: {self.db_path}")

    def _create_tables(self):
        """Create all required database tables"""
        cursor = self.conn.cursor()

        # Processing state table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS processing_state (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE NOT NULL,
                artwork_name TEXT NOT NULL,
                project_date TEXT NOT NULL,
                master_path TEXT NOT NULL,
                rd_folder_path TEXT,
                output_path TEXT NOT NULL,
                preset_id TEXT NOT NULL,
                custom_settings TEXT,
                encoder_type TEXT DEFAULT 'x264',
                scene_threshold REAL DEFAULT 30.0,
                min_scene_length INTEGER DEFAULT 15,
                total_operations INTEGER NOT NULL,
                completed_operations INTEGER DEFAULT 0,
                current_operation TEXT,
                operation_details TEXT,
                scenes_data TEXT,
                selected_scenes TEXT,
                grouped_scenes TEXT,
                status TEXT DEFAULT 'initialized',
                error_message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                process_metadata TEXT
            )
        """)

        # Operation log table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS operation_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                operation_type TEXT NOT NULL,
                operation_name TEXT NOT NULL,
                sequence_number INTEGER NOT NULL,
                status TEXT NOT NULL,
                progress REAL DEFAULT 0.0,
                start_time TIMESTAMP,
                end_time TIMESTAMP,
                duration_seconds REAL,
                input_file TEXT,
                output_files TEXT,
                file_sizes TEXT,
                settings_used TEXT,
                error_details TEXT,
                warning_messages TEXT,
                cpu_usage REAL,
                gpu_usage REAL,
                memory_usage INTEGER,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES processing_state(session_id)
            )
        """)

        # File registry table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS file_registry (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                file_path TEXT NOT NULL,
                file_type TEXT NOT NULL,
                file_category TEXT NOT NULL,
                file_size_bytes INTEGER,
                file_format TEXT,
                resolution TEXT,
                aspect_ratio TEXT,
                duration_seconds REAL,
                frame_number INTEGER,
                source_file TEXT,
                compression_settings TEXT,
                processing_time_ms INTEGER,
                has_metadata BOOLEAN DEFAULT 1,
                metadata_embedded TEXT,
                file_exists BOOLEAN DEFAULT 1,
                verified BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES processing_state(session_id)
            )
        """)

        # App settings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS app_settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                value_type TEXT DEFAULT 'string',
                category TEXT DEFAULT 'general',
                description TEXT,
                modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_session_status ON processing_state(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_operation_session ON operation_log(session_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_file_session ON file_registry(session_id)")

        # Create triggers
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS update_processing_state_timestamp
            AFTER UPDATE ON processing_state
            BEGIN
                UPDATE processing_state
                SET updated_at = CURRENT_TIMESTAMP
                WHERE id = NEW.id;
            END
        """)

        self.conn.commit()
        self.logger.info("Database tables created")

    def create_session(
        self,
        artwork_name: str,
        project_date: str,
        master_path: str,
        output_path: str,
        preset_id: str,
        total_operations: int,
        **kwargs
    ) -> str:
        """
        Create new processing session

        Args:
            artwork_name: Artwork/project name
            project_date: Project date (YY-MM-DD)
            master_path: Path to master video
            output_path: Output root directory
            preset_id: Compression preset ID
            total_operations: Total number of operations to perform
            **kwargs: Additional session parameters

        Returns:
            Session ID (UUID)
        """
        session_id = f"vat_{datetime.now():%Y%m%d_%H%M%S}_{uuid.uuid4().hex[:8]}"

        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO processing_state (
                session_id, artwork_name, project_date, master_path, output_path,
                preset_id, total_operations, rd_folder_path, encoder_type,
                scene_threshold, min_scene_length
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            session_id,
            artwork_name,
            project_date,
            master_path,
            output_path,
            preset_id,
            total_operations,
            kwargs.get('rd_folder_path'),
            kwargs.get('encoder_type', 'x264'),
            kwargs.get('scene_threshold', 30.0),
            kwargs.get('min_scene_length', 15)
        ))

        self.conn.commit()
        self.session_id = session_id

        self.logger.info(f"Created session: {session_id}")
        return session_id

    def update_progress(self, operation: str, details: Optional[Dict] = None):
        """
        Update current operation and progress

        Args:
            operation: Current operation name
            details: Optional detailed progress information
        """
        if not self.session_id:
            raise RuntimeError("No active session")

        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE processing_state
            SET current_operation = ?,
                operation_details = ?,
                completed_operations = completed_operations + 1
            WHERE session_id = ?
        """, (operation, json.dumps(details) if details else None, self.session_id))

        self.conn.commit()

    def log_operation(
        self,
        operation_type: str,
        operation_name: str,
        status: str,
        **kwargs
    ):
        """
        Log an operation to the operation log

        Args:
            operation_type: Type of operation
            operation_name: Name of operation
            status: Operation status (pending, processing, completed, failed)
            **kwargs: Additional operation details
        """
        if not self.session_id:
            raise RuntimeError("No active session")

        cursor = self.conn.cursor()

        # Get next sequence number
        cursor.execute("""
            SELECT COALESCE(MAX(sequence_number), 0) + 1
            FROM operation_log
            WHERE session_id = ?
        """, (self.session_id,))
        sequence = cursor.fetchone()[0]

        cursor.execute("""
            INSERT INTO operation_log (
                session_id, operation_type, operation_name, sequence_number,
                status, progress, input_file, output_files, error_details
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            self.session_id,
            operation_type,
            operation_name,
            sequence,
            status,
            kwargs.get('progress', 0.0),
            kwargs.get('input_file'),
            json.dumps(kwargs.get('output_files', [])),
            kwargs.get('error_details')
        ))

        self.conn.commit()

    def register_file(
        self,
        file_path: str,
        file_type: str,
        file_category: str,
        **kwargs
    ):
        """
        Register a created file in the file registry

        Args:
            file_path: Path to file
            file_type: Type of file
            file_category: Category (masters, stills, clips, rd)
            **kwargs: Additional file properties
        """
        if not self.session_id:
            raise RuntimeError("No active session")

        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO file_registry (
                session_id, file_path, file_type, file_category,
                file_size_bytes, resolution, aspect_ratio, source_file
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            self.session_id,
            file_path,
            file_type,
            file_category,
            kwargs.get('file_size_bytes'),
            kwargs.get('resolution'),
            kwargs.get('aspect_ratio'),
            kwargs.get('source_file')
        ))

        self.conn.commit()

    def update_status(self, status: str, error_message: Optional[str] = None):
        """
        Update session status

        Args:
            status: New status (initialized, processing, paused, completed, failed)
            error_message: Optional error message
        """
        if not self.session_id:
            raise RuntimeError("No active session")

        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE processing_state
            SET status = ?, error_message = ?
            WHERE session_id = ?
        """, (status, error_message, self.session_id))

        if status == 'completed':
            cursor.execute("""
                UPDATE processing_state
                SET completed_at = CURRENT_TIMESTAMP
                WHERE session_id = ?
            """, (self.session_id,))

        self.conn.commit()

    def get_resumable_session(self) -> Optional[Dict[str, Any]]:
        """
        Get most recent resumable session

        Returns:
            Session data dict or None if no resumable session
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT *
            FROM processing_state
            WHERE status IN ('processing', 'paused')
                AND updated_at > datetime('now', '-7 days')
            ORDER BY updated_at DESC
            LIMIT 1
        """)

        row = cursor.fetchone()
        if row:
            return dict(row)
        return None

    def load_session(self, session_id: str) -> Dict[str, Any]:
        """
        Load session data

        Args:
            session_id: Session ID to load

        Returns:
            Session data dictionary
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM processing_state WHERE session_id = ?
        """, (session_id,))

        row = cursor.fetchone()
        if not row:
            raise ValueError(f"Session not found: {session_id}")

        self.session_id = session_id
        return dict(row)

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            self.logger.info("Database connection closed")

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
