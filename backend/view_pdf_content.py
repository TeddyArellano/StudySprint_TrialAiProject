import sqlite3

conn = sqlite3.connect('data/study_agent.db')
cursor = conn.cursor()

print("=" * 80)
print("📄 CONTENIDO DE PDFs ALMACENADOS EN LA BASE DE DATOS")
print("=" * 80)

# Obtener todos los PDFs cargados
cursor.execute("""
    SELECT 
        tc.id,
        tc.topic_id,
        t.name as topic_name,
        s.name as subject_name,
        tc.source_file,
        LENGTH(tc.content) as content_length,
        tc.content,
        tc.created_at
    FROM topic_content tc
    JOIN topics t ON tc.topic_id = t.id
    JOIN subjects s ON t.subject_id = s.id
    ORDER BY tc.created_at DESC
""")

rows = cursor.fetchall()

if not rows:
    print("\n⚠️  No hay PDFs cargados en la base de datos.")
else:
    print(f"\n✅ Se encontraron {len(rows)} PDF(s) cargado(s):\n")
    
    for row in rows:
        pdf_id, topic_id, topic_name, subject_name, source_file, content_length, content, created_at = row
        
        print("=" * 80)
        print(f"📌 PDF ID: {pdf_id}")
        print(f"📚 Materia: {subject_name}")
        print(f"📖 Tema: {topic_name} (ID: {topic_id})")
        print(f"📁 Archivo: {source_file}")
        print(f"📏 Tamaño: {content_length} caracteres ({content_length / 1024:.2f} KB)")
        print(f"🕐 Subido: {created_at}")
        print("-" * 80)
        print("📄 CONTENIDO EXTRAÍDO:")
        print("-" * 80)
        
        # Mostrar el contenido completo
        if content:
            print(content)
        else:
            print("⚠️  (Sin contenido)")
        
        print("\n" + "=" * 80 + "\n")

conn.close()

print("\n✅ Verificación completa.")
print("\n💡 TIP: Si el contenido es muy largo, puedes redirigir la salida a un archivo:")
print("   python view_pdf_content.py > pdf_content.txt")
