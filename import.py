import csv

print("🚀 Convirtiendo CSV para Jira...")

# Leer el archivo original (probar diferentes encodings)
for encoding in ['utf-8-sig', 'latin-1']:
    try:
        with open('Backlog_Sistema_Restaurante.csv', 'r', encoding=encoding) as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        print(f"✅ Leído con encoding: {encoding}")
        break
    except:
        continue

# Escribir nuevo archivo para Jira
with open('issues_for_jira.csv', 'w', newline='', encoding='utf-8-sig') as f:
    writer = csv.writer(f)
    
    # Escribir encabezados para Jira
    writer.writerow(['Project', 'Summary', 'Description', 'Issue Type', 'Priority'])
    
    # Mapeo de prioridades
    priority_map = {'Alta': 'High', 'Media': 'Medium', 'Baja': 'Low'}
    
    for row in rows:
        writer.writerow([
            'SR',  # Project Key
            row['Summary'],  # Summary
            row['Description'],  # Description  
            row['Issue Type'],  # Issue Type
            priority_map.get(row['Priority'], 'Medium')  # Priority
        ])

print(f"✅ ¡LISTO! Archivo creado: issues_for_jira.csv")
print(f"📊 Total issues convertidos: {len(rows)}")
print("\n📌 Ahora en Jira:")
print("1. Ve a tu proyecto")
print("2. Click '...' → 'Import issues from CSV'") 
print("3. Selecciona 'issues_for_jira.csv'")