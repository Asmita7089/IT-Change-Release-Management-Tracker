import sqlite3
from datetime import datetime


DB_NAME = "change_management.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def create_tables():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS changes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            requester TEXT NOT NULL,
            change_type TEXT NOT NULL,
            impact INTEGER NOT NULL,
            likelihood INTEGER NOT NULL,
            risk_score INTEGER NOT NULL,
            risk_level TEXT NOT NULL,
            status TEXT NOT NULL,
            planned_date TEXT,
            implementation_plan TEXT,
            rollback_plan TEXT,
            testing_completed INTEGER DEFAULT 0,
            approval_obtained INTEGER DEFAULT 0,
            documentation_ready INTEGER DEFAULT 0,
            created_at TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            change_id INTEGER NOT NULL,
            implementation_result TEXT NOT NULL,
            issues TEXT,
            lessons_learned TEXT,
            review_date TEXT NOT NULL,
            FOREIGN KEY (change_id) REFERENCES changes(id)
        )
    """)

    connection.commit()
    connection.close()


def add_change(
    title,
    description,
    requester,
    change_type,
    impact,
    likelihood,
    risk_score,
    risk_level,
    status,
    planned_date,
    implementation_plan,
    rollback_plan
):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO changes (
            title,
            description,
            requester,
            change_type,
            impact,
            likelihood,
            risk_score,
            risk_level,
            status,
            planned_date,
            implementation_plan,
            rollback_plan,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        title,
        description,
        requester,
        change_type,
        impact,
        likelihood,
        risk_score,
        risk_level,
        status,
        planned_date,
        implementation_plan,
        rollback_plan,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    connection.commit()
    connection.close()


def get_all_changes():
    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            title,
            requester,
            change_type,
            impact,
            likelihood,
            risk_score,
            risk_level,
            status,
            planned_date,
            created_at
        FROM changes
        ORDER BY id DESC
    """)

    rows = cursor.fetchall()
    connection.close()

    return rows


def get_change_by_id(change_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM changes
        WHERE id = ?
    """, (change_id,))

    row = cursor.fetchone()
    connection.close()

    return row


def update_change_status(change_id, status):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE changes
        SET status = ?
        WHERE id = ?
    """, (status, change_id))

    connection.commit()
    connection.close()


def update_readiness(
    change_id,
    testing_completed,
    approval_obtained,
    documentation_ready
):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE changes
        SET
            testing_completed = ?,
            approval_obtained = ?,
            documentation_ready = ?
        WHERE id = ?
    """, (
        testing_completed,
        approval_obtained,
        documentation_ready,
        change_id
    ))

    connection.commit()
    connection.close()


def add_review(
    change_id,
    implementation_result,
    issues,
    lessons_learned
):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO reviews (
            change_id,
            implementation_result,
            issues,
            lessons_learned,
            review_date
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        change_id,
        implementation_result,
        issues,
        lessons_learned,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    connection.commit()
    connection.close()


def get_reviews():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            reviews.id,
            reviews.change_id,
            changes.title,
            reviews.implementation_result,
            reviews.issues,
            reviews.lessons_learned,
            reviews.review_date
        FROM reviews
        JOIN changes
        ON reviews.change_id = changes.id
        ORDER BY reviews.id DESC
    """)

    rows = cursor.fetchall()
    connection.close()

    return rows