import csv
import os
import subprocess
import mysql.connector
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

INPUT_CSV = 'companie_data.csv'

def get_connection(include_database=True):
    config = {
        "host":os.getenv("MYSQL_HOST", "localhost"),
        "port": int(os.getenv("MYSQL_PORT", 3306)),
        "user":os.getenv("MYSQL_USER", "root"),
        "password": os.getenv("MYSQL_PASSWORD", ""),
    }
    if include_database:
        config["database"] = os.getenv("MYSQL_DATABASE", "ahu_companies")
    return mysql.connector.connect(**config)

def create_database():
    conn= get_connection(include_database=False)
    cursor= conn.cursor()
    db_name=os.getenv("MYSQL_DATABASE", "ahu_companies")
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}`")
    cursor.close()
    conn.close()

CREATE_COMPANY_TYPES_TABLE = """
CREATE TABLE IF NOT EXISTS company_types (
    id   INT          NOT NULL AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL UNIQUE,
    PRIMARY KEY (id)
);
"""

CREATE_COMPANIES_TABLE = """
CREATE TABLE IF NOT EXISTS companies (
    nbrs_id      VARCHAR(20)  NOT NULL,
    company_name VARCHAR(255),
    phone        VARCHAR(50),
    address      TEXT,
    type_id      INT,
    created_at   DATETIME     NOT NULL,
    updated_at   DATETIME     NOT NULL,
    PRIMARY KEY (nbrs_id),
    FOREIGN KEY (type_id) REFERENCES company_types(id)
);
"""

def create_tables(cursor):
    cursor.execute(CREATE_COMPANY_TYPES_TABLE)
    cursor.execute(CREATE_COMPANIES_TABLE)

def get_or_create_type(cursor, type_name):
    if not type_name:
        type_name = 'Unknown'
    cursor.execute("SELECT id FROM company_types WHERE name = %s", (type_name,))
    row = cursor.fetchone()
    if row:
        return row[0]
    cursor.execute("INSERT INTO company_types (name) VALUES (%s)", (type_name,))
    return cursor.lastrowid

def upsert_company(cursor, row, type_id, now):
    sql = """
        INSERT INTO companies (nbrs_id, company_name, phone, address, type_id, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            company_name = VALUES(company_name),
            phone        = VALUES(phone),
            address      = VALUES(address),
            type_id      = VALUES(type_id),
            updated_at   = VALUES(updated_at)
    """
    cursor.execute(sql, (row['nbrs_id'],row['company_name'],row['phone'],row['address'],type_id,now,now))

def export_sql():
    db_name=os.getenv("MYSQL_DATABASE", "ahu_companies")
    user= os.getenv("MYSQL_USER", "root")
    password= os.getenv("MYSQL_PASSWORD", "")
    host= os.getenv("MYSQL_HOST", "localhost")
    port=os.getenv("MYSQL_PORT", "3306")
    output="database.sql"

    command = ["mysqldump",f"--host={host}",f"--port={port}",f"--user={user}",f"--password={password}","--databases","--add-drop-database",db_name]

    with open(output, "w", encoding="utf-8") as f:
        subprocess.run(command, stdout=f, check=True, shell=True)


def run(input_csv=None):
    csv_file = input_csv or INPUT_CSV

    create_database()

    print("connection with mysql")
    conn   = get_connection()
    cursor = conn.cursor()

    create_tables(cursor)
    conn.commit()

    with open(csv_file, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows   = list(reader)

    print(len(rows))
    now=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    inserted= 0
    updated= 0
    skipped= 0
    type_cache= {}

    for i, row in enumerate(rows, 1):
        nbrs_id = row.get('nbrs_id', '').strip()
        if not nbrs_id:
            skipped += 1
            continue

        type_name = row.get('company_type', '').strip()
        if type_name not in type_cache:
            type_cache[type_name] = get_or_create_type(cursor, type_name)
        type_id = type_cache[type_name]

        cursor.execute("SELECT nbrs_id FROM companies WHERE nbrs_id = %s", (nbrs_id,))
        exists = cursor.fetchone()

        upsert_company(cursor, row, type_id, now)

        if exists:
            updated += 1
        else:
            inserted += 1

        if i % 500 == 0:
            conn.commit()

    conn.commit()

    # closing 
    cursor.close()
    conn.close()

    # creatingn the .sql file
    export_sql()

if __name__ == "__main__":
    run()