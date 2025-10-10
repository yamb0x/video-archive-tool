# Database Schema Design
## Video Archive Tool - State Management & Configuration

---

## 1. DATABASE OVERVIEW

### Purpose
SQLite database for managing application state, user presets, and processing history to enable resume capability and configuration persistence.

### Database File
`App/config/state.db`

---

## 2. SCHEMA DEFINITION

### 2.1 Processing State Table
Tracks active and completed processing sessions for resume capability.

```sql
CREATE TABLE processing_state (
    -- Primary identification
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT UNIQUE NOT NULL,

    -- Project information
    artwork_name TEXT NOT NULL,
    project_date TEXT NOT NULL,  -- Format: YY-MM-DD

    -- File paths
    master_path TEXT NOT NULL,
    rd_folder_path TEXT,  -- Optional
    output_path TEXT NOT NULL,

    -- Processing configuration
    preset_id TEXT NOT NULL,
    custom_settings TEXT,  -- JSON for custom preset overrides
    encoder_type TEXT DEFAULT 'x264',  -- x264 or nvenc
    scene_threshold REAL DEFAULT 30.0,
    min_scene_length INTEGER DEFAULT 15,

    -- Progress tracking
    total_operations INTEGER NOT NULL,
    completed_operations INTEGER DEFAULT 0,
    current_operation TEXT,
    operation_details TEXT,  -- JSON with detailed progress

    -- Scene data
    scenes_data TEXT,  -- JSON array of detected scenes
    selected_scenes TEXT,  -- JSON array of user selections
    grouped_scenes TEXT,  -- JSON object of grouped scenes

    -- Status
    status TEXT DEFAULT 'initialized',  -- initialized, processing, paused, completed, failed
    error_message TEXT,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,

    -- Metadata
    process_metadata TEXT  -- JSON for additional data
);

CREATE INDEX idx_session_status ON processing_state(status);
CREATE INDEX idx_session_date ON processing_state(created_at);
```

### 2.2 Operation Log Table
Detailed logging of each processing operation for debugging and history.

```sql
CREATE TABLE operation_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,

    -- Operation details
    operation_type TEXT NOT NULL,  -- scene_detection, optimization, still_extraction, etc.
    operation_name TEXT NOT NULL,
    sequence_number INTEGER NOT NULL,

    -- Status tracking
    status TEXT NOT NULL,  -- pending, processing, completed, failed, skipped
    progress REAL DEFAULT 0.0,  -- 0.0 to 1.0

    -- Performance metrics
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    duration_seconds REAL,

    -- File information
    input_file TEXT,
    output_files TEXT,  -- JSON array
    file_sizes TEXT,  -- JSON object with size information

    -- Technical details
    settings_used TEXT,  -- JSON with operation-specific settings
    error_details TEXT,
    warning_messages TEXT,  -- JSON array

    -- Resource usage
    cpu_usage REAL,
    gpu_usage REAL,
    memory_usage INTEGER,  -- in MB

    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (session_id) REFERENCES processing_state(session_id)
);

CREATE INDEX idx_operation_session ON operation_log(session_id);
CREATE INDEX idx_operation_status ON operation_log(status);
```

### 2.3 User Presets Table
Stores custom compression presets created by users.

```sql
CREATE TABLE user_presets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    preset_id TEXT UNIQUE NOT NULL,
    preset_name TEXT NOT NULL,

    -- Preset configuration
    base_preset TEXT,  -- ID of built-in preset this is based on
    is_default BOOLEAN DEFAULT 0,

    -- Settings (all stored as JSON)
    stills_hq_settings TEXT NOT NULL,
    stills_web_settings TEXT NOT NULL,
    video_settings TEXT NOT NULL,
    thumbnail_settings TEXT,

    -- Advanced options
    advanced_settings TEXT,  -- JSON with encoding options, filters, etc.

    -- Metadata
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_used_at TIMESTAMP,
    usage_count INTEGER DEFAULT 0
);

CREATE INDEX idx_preset_name ON user_presets(preset_name);
CREATE INDEX idx_preset_default ON user_presets(is_default);
```

### 2.4 Project History Table
Maintains history of all processed projects for reference and statistics.

```sql
CREATE TABLE project_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT UNIQUE NOT NULL,

    -- Project identification
    artwork_name TEXT NOT NULL,
    project_date TEXT NOT NULL,
    output_path TEXT NOT NULL,

    -- Source information
    master_filename TEXT NOT NULL,
    master_duration REAL,
    master_resolution TEXT,
    master_fps REAL,
    master_codec TEXT,
    master_size_mb REAL,

    -- Processing summary
    scenes_detected INTEGER,
    scenes_exported INTEGER,
    stills_created INTEGER,
    clips_created INTEGER,
    rd_files_processed INTEGER,

    -- Output statistics
    total_files_created INTEGER,
    total_output_size_mb REAL,
    compression_ratio REAL,

    -- Performance metrics
    total_processing_time_seconds REAL,
    gpu_accelerated BOOLEAN,
    average_fps_processed REAL,

    -- Quality metrics
    preset_used TEXT,
    encoder_used TEXT,

    -- Completion status
    completed_successfully BOOLEAN,
    completion_notes TEXT,

    -- Timestamps
    started_at TIMESTAMP,
    completed_at TIMESTAMP,

    -- Additional data
    metadata TEXT,  -- JSON for extensibility

    FOREIGN KEY (session_id) REFERENCES processing_state(session_id)
);

CREATE INDEX idx_history_artwork ON project_history(artwork_name);
CREATE INDEX idx_history_date ON project_history(completed_at);
```

### 2.5 File Registry Table
Tracks all files created during processing for cleanup and management.

```sql
CREATE TABLE file_registry (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,

    -- File information
    file_path TEXT NOT NULL,
    file_type TEXT NOT NULL,  -- master, still_hq, still_web, clip, rd_image, rd_video
    file_category TEXT NOT NULL,  -- masters, stills, clips, rd

    -- File properties
    file_size_bytes INTEGER,
    file_format TEXT,
    resolution TEXT,
    aspect_ratio TEXT,
    duration_seconds REAL,  -- For videos
    frame_number INTEGER,  -- For stills extracted from video

    -- Processing information
    source_file TEXT,
    compression_settings TEXT,  -- JSON
    processing_time_ms INTEGER,

    -- Metadata
    has_metadata BOOLEAN DEFAULT 1,
    metadata_embedded TEXT,  -- JSON of embedded metadata

    -- Status
    file_exists BOOLEAN DEFAULT 1,
    verified BOOLEAN DEFAULT 0,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (session_id) REFERENCES processing_state(session_id)
);

CREATE INDEX idx_file_session ON file_registry(session_id);
CREATE INDEX idx_file_type ON file_registry(file_type);
CREATE INDEX idx_file_path ON file_registry(file_path);
```

### 2.6 Application Settings Table
Global application configuration and preferences.

```sql
CREATE TABLE app_settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    value_type TEXT DEFAULT 'string',  -- string, integer, real, boolean, json
    category TEXT DEFAULT 'general',
    description TEXT,
    modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert default settings
INSERT INTO app_settings (key, value, value_type, category, description) VALUES
    ('app_version', '1.0.0', 'string', 'system', 'Application version'),
    ('last_output_directory', '', 'string', 'paths', 'Last used output directory'),
    ('last_master_directory', '', 'string', 'paths', 'Last directory for master files'),
    ('last_rd_directory', '', 'string', 'paths', 'Last directory for R&D files'),
    ('default_preset', 'webflow_standard', 'string', 'presets', 'Default compression preset'),
    ('scene_threshold_default', '30', 'real', 'processing', 'Default scene detection threshold'),
    ('min_scene_length_default', '15', 'integer', 'processing', 'Default minimum scene length in frames'),
    ('encoder_preference', 'x264', 'string', 'encoding', 'Preferred encoder (x264 or nvenc)'),
    ('auto_open_output', '1', 'boolean', 'behavior', 'Automatically open output folder on completion'),
    ('generate_log', '1', 'boolean', 'behavior', 'Generate process log file'),
    ('extract_midpoint_stills', '1', 'boolean', 'processing', 'Extract stills from scene midpoints'),
    ('copyright_text', '© Yambo Studio', 'string', 'metadata', 'Copyright text for metadata'),
    ('parallel_workers', '4', 'integer', 'performance', 'Number of parallel processing workers'),
    ('gpu_enabled', '1', 'boolean', 'performance', 'Enable GPU acceleration when available'),
    ('cache_thumbnails', '1', 'boolean', 'performance', 'Cache scene thumbnails'),
    ('max_resume_age_days', '7', 'integer', 'behavior', 'Maximum age for resumable sessions'),
    ('log_level', 'INFO', 'string', 'system', 'Logging level (DEBUG, INFO, WARNING, ERROR)'),
    ('ui_theme', 'default', 'string', 'interface', 'User interface theme'),
    ('window_geometry', '', 'json', 'interface', 'Main window size and position');
```

---

## 3. HELPER VIEWS

### 3.1 Active Sessions View
```sql
CREATE VIEW active_sessions AS
SELECT
    session_id,
    artwork_name,
    status,
    ROUND(CAST(completed_operations AS REAL) / total_operations * 100, 1) as progress_percent,
    current_operation,
    updated_at
FROM processing_state
WHERE status IN ('initialized', 'processing', 'paused')
ORDER BY updated_at DESC;
```

### 3.2 Project Statistics View
```sql
CREATE VIEW project_statistics AS
SELECT
    COUNT(*) as total_projects,
    COUNT(CASE WHEN completed_successfully = 1 THEN 1 END) as successful_projects,
    AVG(total_processing_time_seconds) as avg_processing_time,
    SUM(total_files_created) as total_files_created,
    SUM(total_output_size_mb) as total_output_size_mb,
    AVG(compression_ratio) as avg_compression_ratio
FROM project_history
WHERE completed_at >= datetime('now', '-30 days');
```

---

## 4. TRIGGERS

### 4.1 Update Timestamp Trigger
```sql
CREATE TRIGGER update_processing_state_timestamp
AFTER UPDATE ON processing_state
BEGIN
    UPDATE processing_state
    SET updated_at = CURRENT_TIMESTAMP
    WHERE id = NEW.id;
END;
```

### 4.2 Preset Usage Tracking Trigger
```sql
CREATE TRIGGER track_preset_usage
AFTER INSERT ON processing_state
BEGIN
    UPDATE user_presets
    SET usage_count = usage_count + 1,
        last_used_at = CURRENT_TIMESTAMP
    WHERE preset_id = NEW.preset_id;
END;
```

### 4.3 Session Completion Trigger
```sql
CREATE TRIGGER complete_session
AFTER UPDATE OF status ON processing_state
WHEN NEW.status = 'completed'
BEGIN
    UPDATE processing_state
    SET completed_at = CURRENT_TIMESTAMP
    WHERE id = NEW.id;
END;
```

---

## 5. DATA ACCESS PATTERNS

### 5.1 Resume Session Query
```python
def get_resumable_session():
    return db.execute("""
        SELECT
            ps.*,
            COUNT(ol.id) as completed_operations_verified,
            MAX(ol.timestamp) as last_operation_time
        FROM processing_state ps
        LEFT JOIN operation_log ol ON ps.session_id = ol.session_id
        WHERE ps.status IN ('processing', 'paused')
            AND ps.updated_at > datetime('now', '-7 days')
        GROUP BY ps.session_id
        ORDER BY ps.updated_at DESC
        LIMIT 1
    """).fetchone()
```

### 5.2 Save Processing State
```python
def save_state(session_id, operation, progress):
    with db.transaction():
        # Update main state
        db.execute("""
            UPDATE processing_state
            SET current_operation = ?,
                completed_operations = ?,
                operation_details = ?
            WHERE session_id = ?
        """, (operation, progress, details_json, session_id))

        # Log operation
        db.execute("""
            INSERT INTO operation_log
            (session_id, operation_type, operation_name, status, progress)
            VALUES (?, ?, ?, ?, ?)
        """, (session_id, op_type, op_name, 'completed', 1.0))
```

### 5.3 Load User Presets
```python
def get_user_presets():
    return db.execute("""
        SELECT
            preset_id,
            preset_name,
            is_default,
            description,
            usage_count,
            last_used_at
        FROM user_presets
        ORDER BY is_default DESC, usage_count DESC
    """).fetchall()
```

---

## 6. MAINTENANCE PROCEDURES

### 6.1 Cleanup Old Sessions
```sql
-- Remove incomplete sessions older than 30 days
DELETE FROM processing_state
WHERE status != 'completed'
    AND updated_at < datetime('now', '-30 days');

-- Archive completed projects older than 90 days
INSERT INTO project_history_archive
SELECT * FROM project_history
WHERE completed_at < datetime('now', '-90 days');

DELETE FROM project_history
WHERE completed_at < datetime('now', '-90 days');
```

### 6.2 Database Optimization
```sql
-- Vacuum and analyze periodically
VACUUM;
ANALYZE;

-- Rebuild indexes if fragmented
REINDEX;
```

### 6.3 Statistics Reset
```sql
-- Reset usage counters (optional, for testing)
UPDATE user_presets SET usage_count = 0, last_used_at = NULL;

-- Clear operation logs older than 30 days
DELETE FROM operation_log
WHERE timestamp < datetime('now', '-30 days');
```

---

## 7. MIGRATION STRATEGY

### Version Migration Example
```python
def migrate_to_version_2():
    """Example migration from v1 to v2"""

    # Check current version
    current_version = db.execute(
        "SELECT value FROM app_settings WHERE key = 'db_version'"
    ).fetchone()

    if current_version['value'] == '1.0':
        # Add new columns
        db.execute("""
            ALTER TABLE processing_state
            ADD COLUMN ai_scene_grouping TEXT
        """)

        # Update version
        db.execute("""
            UPDATE app_settings
            SET value = '2.0'
            WHERE key = 'db_version'
        """)

        print("Migration to v2.0 completed")
```

---

## 8. BACKUP STRATEGY

### Automatic Backup
```python
def create_backup():
    """Create timestamped backup of database"""
    import shutil
    from datetime import datetime

    backup_name = f"state_backup_{datetime.now():%Y%m%d_%H%M%S}.db"
    backup_path = os.path.join("App/config/backups", backup_name)

    shutil.copy2("App/config/state.db", backup_path)

    # Keep only last 10 backups
    cleanup_old_backups(keep=10)
```

---

*Schema Version: 1.0*
*Last Updated: December 2024*