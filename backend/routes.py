"""
DevFlow API Routes
==================
Defines all API endpoints for the DevFlow backend.
Uses in-memory mock data — no database required.
"""

from flask import jsonify, request
from datetime import datetime, timedelta
import random

# ─────────────────────────────────────────────
# MOCK DATA STORE
# ─────────────────────────────────────────────

TASKS = [
    {
        "id": 1,
        "title": "Fix authentication token refresh bug",
        "description": "The JWT refresh token silently fails after ~12 hours. Users are getting logged out unexpectedly. Root cause: token expiry not handled in the interceptor.",
        "priority": "high",
        "status": "in_progress",
        "deadline": "2025-04-22",
        "tags": ["bug", "auth", "backend"],
        "assignee": "Aditya K.",
        "created_at": "2025-04-18",
        "comments": [
            {"author": "Priya S.", "text": "Reproduced locally – happens after idle for 12h.", "time": "2 hours ago"},
            {"author": "Aditya K.", "text": "Investigating the interceptor logic now.", "time": "1 hour ago"},
        ],
        "activity": [
            {"event": "Task created", "time": "4 days ago"},
            {"event": "Priority set to High", "time": "3 days ago"},
            {"event": "Assigned to Aditya K.", "time": "2 days ago"},
            {"event": "Status → In Progress", "time": "1 hour ago"},
        ]
    },
    {
        "id": 2,
        "title": "Implement cursor-based pagination for /api/feed",
        "description": "Current offset pagination breaks with real-time data inserts. Switch to cursor-based pagination for the main feed endpoint.",
        "priority": "high",
        "status": "pending",
        "deadline": "2025-04-24",
        "tags": ["api", "performance", "backend"],
        "assignee": "Aditya K.",
        "created_at": "2025-04-20",
        "comments": [],
        "activity": [
            {"event": "Task created", "time": "2 days ago"},
            {"event": "Tagged api, performance", "time": "2 days ago"},
        ]
    },
    {
        "id": 3,
        "title": "Review PR #312 – database abstraction layer",
        "description": "Review the new DB abstraction layer. Check for N+1 query issues and ensure proper connection pooling.",
        "priority": "medium",
        "status": "pending",
        "deadline": "2025-04-22",
        "tags": ["review", "database"],
        "assignee": "Aditya K.",
        "created_at": "2025-04-21",
        "comments": [
            {"author": "Rahul M.", "text": "PR is ready for review, all tests pass.", "time": "3 hours ago"},
        ],
        "activity": [
            {"event": "Task created", "time": "1 day ago"},
            {"event": "PR #312 linked", "time": "3 hours ago"},
        ]
    },
    {
        "id": 4,
        "title": "Update OpenAPI documentation for v2 endpoints",
        "description": "All v2 API endpoints need updated Swagger/OpenAPI specs with proper request/response schemas.",
        "priority": "low",
        "status": "completed",
        "deadline": "2025-04-20",
        "tags": ["docs", "api"],
        "assignee": "Aditya K.",
        "created_at": "2025-04-15",
        "comments": [],
        "activity": [
            {"event": "Task created", "time": "7 days ago"},
            {"event": "Status → Completed", "time": "2 days ago"},
        ]
    },
    {
        "id": 5,
        "title": "Write unit tests for token parser module",
        "description": "Achieve 90%+ test coverage for the token parser. Cover edge cases: malformed tokens, expiry, signature mismatch.",
        "priority": "medium",
        "status": "completed",
        "deadline": "2025-04-19",
        "tags": ["testing", "auth"],
        "assignee": "Aditya K.",
        "created_at": "2025-04-14",
        "comments": [],
        "activity": [
            {"event": "Task created", "time": "8 days ago"},
            {"event": "Status → Completed", "time": "3 days ago"},
        ]
    },
    {
        "id": 6,
        "title": "Set up CI/CD pipeline with GitHub Actions",
        "description": "Automate testing, linting, and deployment on every PR merge. Deploy staging on PR open, production on main merge.",
        "priority": "high",
        "status": "overdue",
        "deadline": "2025-04-18",
        "tags": ["devops", "ci-cd"],
        "assignee": "Aditya K.",
        "created_at": "2025-04-10",
        "comments": [],
        "activity": [
            {"event": "Task created", "time": "12 days ago"},
            {"event": "Deadline passed", "time": "4 days ago"},
        ]
    },
]

PROGRESS_DATA = {
    "user": {
        "name": "Meera Singh",
        "role": "Full Stack Developer",
        "avatar_initials": "AK",
        "streak": 28,
        "level": 14,
        "xp": 3420,
        "xp_to_next": 4000,
    },
    "stats": {
        "tasks_completed": 48,
        "tasks_in_progress": 7,
        "tasks_overdue": 2,
        "focus_score": 87,
        "commits_this_week": 23,
        "prs_merged": 5,
    },
    "weekly_output": [
        {"day": "Mon", "tasks": 9},
        {"day": "Tue", "tasks": 12},
        {"day": "Wed", "tasks": 7},
        {"day": "Thu", "tasks": 11},
        {"day": "Fri", "tasks": 14},
        {"day": "Sat", "tasks": 4},
        {"day": "Sun", "tasks": 2},
    ],
    "skills": [
        {"name": "TypeScript", "level": 88, "color": "#4f6ef7"},
        {"name": "React",      "level": 74, "color": "#7c3aed"},
        {"name": "Node.js",    "level": 65, "color": "#4f6ef7"},
        {"name": "PostgreSQL", "level": 52, "color": "#10b981"},
        {"name": "Docker",     "level": 38, "color": "#f59e0b"},
        {"name": "Rust",       "level": 18, "color": "#ef4444"},
    ],
    "courses": [
        {"title": "Advanced TypeScript Patterns", "progress": 88, "category": "Language", "hours_spent": 22, "total_hours": 25},
        {"title": "System Design Fundamentals",   "progress": 60, "category": "Architecture", "hours_spent": 15, "total_hours": 25},
        {"title": "Rust for Backend Developers",  "progress": 18, "category": "Language", "hours_spent": 4,  "total_hours": 30},
        {"title": "PostgreSQL Deep Dive",         "progress": 52, "category": "Database", "hours_spent": 13, "total_hours": 20},
        {"title": "Docker & Kubernetes Essentials","progress": 38, "category": "DevOps", "hours_spent": 9,  "total_hours": 18},
    ],
    "achievements": [
        {"title": "Speed Coder",    "description": "Complete 50 tasks in one week", "icon": "🚀", "earned": True},
        {"title": "On Fire",        "description": "28-day learning streak",        "icon": "🔥", "earned": True},
        {"title": "TypeScript Pro", "description": "Reach 80%+ TypeScript skill",  "icon": "🏆", "earned": True},
        {"title": "Merge Master",   "description": "Merge 25 PRs",                 "icon": "🔀", "earned": False},
        {"title": "Test Champion",  "description": "Achieve 95% test coverage",    "icon": "✅", "earned": False},
    ],
    "sprint": {
        "name": "Sprint 14 – Auth & Performance",
        "progress": 75,
        "monthly_goal": 60,
        "test_coverage": 90,
        "days_remaining": 3,
    }
}


# ─────────────────────────────────────────────
# ROUTE REGISTRATION
# ─────────────────────────────────────────────

def register_routes(app):
    """Register all API routes on the Flask app instance."""

    @app.route("/")
    def index():
        """Health check / API info endpoint."""
        return jsonify({
            "app": "DevFlow API",
            "version": "1.0.0",
            "status": "running",
            "endpoints": ["/tasks", "/tasks/<id>", "/add-task", "/progress", "/dashboard-summary"]
        })

    # ── GET /tasks ──────────────────────────────
    @app.route("/tasks", methods=["GET"])
    def get_tasks():
        """
        Return all tasks, with optional filtering.
        Query params:
          ?status=pending|in_progress|completed|overdue
          ?priority=high|medium|low
        """
        status   = request.args.get("status")
        priority = request.args.get("priority")
        result   = TASKS[:]

        if status:
            result = [t for t in result if t["status"] == status]
        if priority:
            result = [t for t in result if t["priority"] == priority]

        return jsonify({
            "success": True,
            "count": len(result),
            "tasks": result
        })

    # ── GET /tasks/<id> ─────────────────────────
    @app.route("/tasks/<int:task_id>", methods=["GET"])
    def get_task(task_id):
        """Return a single task by ID (used by the Task Detail page)."""
        task = next((t for t in TASKS if t["id"] == task_id), None)
        if not task:
            return jsonify({"success": False, "error": "Task not found"}), 404
        return jsonify({"success": True, "task": task})

    # ── POST /add-task ───────────────────────────
    @app.route("/add-task", methods=["POST"])
    def add_task():
        """
        Add a new task. Expects JSON body:
        {
          "title":    "string (required)",
          "priority": "high|medium|low (default: medium)",
          "deadline": "YYYY-MM-DD (optional)",
          "tags":     ["string"] (optional)
        }
        """
        data = request.get_json()
        if not data or not data.get("title"):
            return jsonify({"success": False, "error": "title is required"}), 400

        new_id = max(t["id"] for t in TASKS) + 1
        new_task = {
            "id":          new_id,
            "title":       data["title"],
            "description": data.get("description", ""),
            "priority":    data.get("priority", "medium"),
            "status":      "pending",
            "deadline":    data.get("deadline", ""),
            "tags":        data.get("tags", []),
            "assignee":    "Aditya K.",
            "created_at":  datetime.now().strftime("%Y-%m-%d"),
            "comments":    [],
            "activity":    [{"event": "Task created", "time": "just now"}]
        }
        TASKS.append(new_task)
        return jsonify({"success": True, "task": new_task}), 201

    # ── DELETE /tasks/<id> ───────────────────────
    @app.route("/tasks/<int:task_id>", methods=["DELETE"])
    def delete_task(task_id):
        """Delete a task by ID."""
        global TASKS
        task = next((t for t in TASKS if t["id"] == task_id), None)
        if not task:
            return jsonify({"success": False, "error": "Task not found"}), 404
        TASKS = [t for t in TASKS if t["id"] != task_id]
        return jsonify({"success": True, "message": f"Task {task_id} deleted"})

    # ── PATCH /tasks/<id>/status ─────────────────
    @app.route("/tasks/<int:task_id>/status", methods=["PATCH"])
    def update_task_status(task_id):
        """
        Update task status. Body: { "status": "completed" }
        """
        task = next((t for t in TASKS if t["id"] == task_id), None)
        if not task:
            return jsonify({"success": False, "error": "Task not found"}), 404

        data = request.get_json()
        new_status = data.get("status")
        valid = ["pending", "in_progress", "completed", "overdue"]
        if new_status not in valid:
            return jsonify({"success": False, "error": f"status must be one of {valid}"}), 400

        task["status"] = new_status
        task["activity"].append({"event": f"Status → {new_status.replace('_',' ').title()}", "time": "just now"})
        return jsonify({"success": True, "task": task})

    # ── GET /progress ─────────────────────────────
    @app.route("/progress", methods=["GET"])
    def get_progress():
        """Return user progress, skills, courses, and achievements."""
        return jsonify({"success": True, "data": PROGRESS_DATA})

    # ── GET /dashboard-summary ────────────────────
    @app.route("/dashboard-summary", methods=["GET"])
    def dashboard_summary():
        """
        Return a compact summary for the dashboard:
        stats, recent tasks, weekly output.
        """
        recent_tasks = [t for t in TASKS if t["status"] != "completed"][:4]
        return jsonify({
            "success": True,
            "summary": {
                "stats":         PROGRESS_DATA["stats"],
                "sprint":        PROGRESS_DATA["sprint"],
                "weekly_output": PROGRESS_DATA["weekly_output"],
                "recent_tasks":  recent_tasks,
                "user":          PROGRESS_DATA["user"],
            }
        })
