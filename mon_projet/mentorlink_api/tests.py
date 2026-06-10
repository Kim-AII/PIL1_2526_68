import pymysql

try:
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database='mentorlink_db',
        port=3306
    )
    print("✅ Connexion à MySQL réussie !")
    
    with connection.cursor() as cursor:
        cursor.execute("SHOW TABLES;")
        tables = cursor.fetchall()
        print("📋 Tables dans mentorlink_db :")
        for table in tables:
            print(f"   - {table[0]}")
    
    connection.close()
except Exception as e:
    print(f"❌ Erreur : {e}")