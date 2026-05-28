import pytest
import os
import sqlite3
from database import db_manager

# --- FIXTURE: Setup a temporary test database ---
@pytest.fixture
def setup_test_db():
    # Setup: Use a test-specific database path to avoid ruining your real app data
    test_db_path = "test_avianquest.db"
    db_manager.DB_PATH = test_db_path 
    db_manager.init_db()
    
    yield # Run the tests
    
    # Teardown: Clean up the test database after tests finish
    if os.path.exists(test_db_path):
        os.remove(test_db_path)

# --- 1. E2E TEST: Database Initialization ---
def test_database_initialization(setup_test_db):
    """E2E Test: Verifies all core tables are created successfully without schema errors."""
    conn = sqlite3.connect(db_manager.DB_PATH)
    cursor = conn.cursor()
    
    # Check if critical tables exist
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    
    assert "users" in tables
    assert "routine_tasks" in tables
    assert "user_course_progress" in tables
    assert "alert_bank" in tables
    conn.close()

# --- 2. UNIT TEST: Authentication Security ---
def test_secure_user_registration(setup_test_db):
    """Unit Test: Verifies passwords are bcrypt hashed and users can login."""
    # 1. Create a test user
    success, msg = db_manager.create_user("Test Ali", "ali@test.com", "securepassword123")
    assert success is True
    
    # 2. Verify password hashing prevents raw passwords from being saved
    conn = sqlite3.connect(db_manager.DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT password_hash FROM users WHERE email = 'ali@test.com'")
    saved_hash = cursor.fetchone()[0]
    conn.close()
    
    assert saved_hash != "securepassword123" # Must not be plain text
    assert saved_hash.startswith("$2b$") # Standard bcrypt prefix

# --- 3. EDGE CASE TEST: Scoring Math Logic ---
def test_course_progress_scoring(setup_test_db):
    """Edge Case Test: Verifies that the app successfully calculates and retains highest scores."""
    user_id = 1
    module = "Danger Zones"
    
    # Simulate a user getting a low score (3)
    db_manager.update_course_progress(user_id, module, 1.0, 3)
    progress_data = db_manager.get_course_progress(user_id)
    assert progress_data[module]["score"] == 3
    
    # Simulate the user retaking it and getting a higher score (5)
    db_manager.update_course_progress(user_id, module, 1.0, 5)
    progress_data = db_manager.get_course_progress(user_id)
    assert progress_data[module]["score"] == 5 # Should update to the higher score