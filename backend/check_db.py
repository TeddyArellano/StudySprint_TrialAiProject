import sqlite3

conn = sqlite3.connect('data/study_agent.db')
cursor = conn.cursor()

print("=" * 60)
print("VERIFICACIÓN DE BASE DE DATOS")
print("=" * 60)

# Tablas
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print("\n📊 TABLAS EN LA BASE DE DATOS:")
for t in tables:
    print(f"  - {t[0]}")

# Subjects
print("\n📚 SUBJECTS (Materias):")
cursor.execute("SELECT COUNT(*) FROM subjects")
count = cursor.fetchone()[0]
print(f"  Total: {count} registros")
if count > 0:
    cursor.execute("SELECT id, name, description FROM subjects LIMIT 5")
    rows = cursor.fetchall()
    for row in rows:
        print(f"    ID {row[0]}: {row[1]} - {row[2]}")
else:
    print("  ⚠️  Tabla VACÍA")

# Topics
print("\n📖 TOPICS (Temas):")
cursor.execute("SELECT COUNT(*) FROM topics")
count = cursor.fetchone()[0]
print(f"  Total: {count} registros")
if count > 0:
    cursor.execute("SELECT id, subject_id, name, description FROM topics LIMIT 5")
    rows = cursor.fetchall()
    for row in rows:
        print(f"    ID {row[0]} (Subject {row[1]}): {row[2]} - {row[3]}")
else:
    print("  ⚠️  Tabla VACÍA")

# Topic Content
print("\n📄 TOPIC_CONTENT (Contenido de PDFs):")
cursor.execute("SELECT COUNT(*) FROM topic_content")
count = cursor.fetchone()[0]
print(f"  Total: {count} registros")
if count > 0:
    cursor.execute("SELECT id, topic_id, LENGTH(content), source_file FROM topic_content LIMIT 5")
    rows = cursor.fetchall()
    for row in rows:
        print(f"    ID {row[0]} (Topic {row[1]}): {row[2]} chars - {row[3]}")
else:
    print("  ⚠️  Tabla VACÍA")

# Study Sessions
print("\n🎯 STUDY_SESSIONS (Sesiones completadas):")
cursor.execute("SELECT COUNT(*) FROM study_sessions")
count = cursor.fetchone()[0]
print(f"  Total: {count} registros")
if count > 0:
    cursor.execute("SELECT id, topic_id, duration, score, total_questions, completed_at FROM study_sessions LIMIT 5")
    rows = cursor.fetchall()
    for row in rows:
        percentage = (row[3] / row[4] * 100) if row[4] > 0 else 0
        print(f"    ID {row[0]} (Topic {row[1]}): {row[2]}min, Score: {row[3]}/{row[4]} ({percentage:.0f}%) - {row[5]}")
else:
    print("  ⚠️  Tabla VACÍA")

print("\n" + "=" * 60)

conn.close()
