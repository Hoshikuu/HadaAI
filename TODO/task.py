#   ----------------------------------------------------
#          Hoshikuu - https://github.com/Hoshikuu
#   ----------------------------------------------------
#   HadaAI/todo/task.py - V0.0.2

from flask import Flask, jsonify, request, render_template
import json, os, uuid
from datetime import datetime

app  = Flask(__name__)
FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tasks.json")

def load():
    if os.path.exists(FILE):
        try:
            with open(FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save(tasks):
    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)

@app.route("/api/tasks", methods=["GET"])
def api_get():
    return jsonify(load())

@app.route("/api/tasks", methods=["POST"])
def api_create():
    d = request.json or {}
    if not d.get("name", "").strip():
        return jsonify({"error": "El nombre es obligatorio"}), 400
    tasks = load()
    task = {
        "id":         str(uuid.uuid4()),
        "name":       d["name"].strip(),
        "topic":      d.get("topic", "General").strip() or "General",
        "notes":      d.get("notes", "").strip(),
        "due_date":   d.get("due_date", "").strip(),
        "priority":   d.get("priority", "media"),
        "color":      d.get("color", "#3b82f6"),
        "status":     d.get("status", "pendiente"),
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    }
    tasks.append(task)
    save(tasks)
    return jsonify(task), 201

@app.route("/api/tasks/<tid>", methods=["PUT"])
def api_update(tid):
    tasks = load()
    for t in tasks:
        if t["id"] == tid:
            d = request.json or {}
            for k in ("name", "topic", "notes", "due_date", "priority", "color", "status"):
                if k in d:
                    t[k] = d[k]
            t["updated_at"] = datetime.now().isoformat()
            save(tasks)
            return jsonify(t)
    return jsonify({"error": "Tarea no encontrada"}), 404

@app.route("/api/tasks/<tid>", methods=["DELETE"])
def api_delete(tid):
    tasks = load()
    new   = [t for t in tasks if t["id"] != tid]
    if len(new) == len(tasks):
        return jsonify({"error": "Tarea no encontrada"}), 404
    save(new)
    return jsonify({"ok": True})

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    print()
    print("  ╔══════════════════════════════════════╗")
    print("  ║     TaskBoard Web · Hoshiku 2026     ║")
    print("  ╠══════════════════════════════════════╣")
    print("  ║        http://localhost:8005         ║")
    print("  ╚══════════════════════════════════════╝")
    print()
    app.run(host="127.0.0.1", port=8005, debug=False)
