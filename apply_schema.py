import subprocess
import sys

def install_and_run():
    subprocess.check_call([sys.executable, "-m", "pip", "install", "psycopg2-binary"])
    import psycopg2
    conn = psycopg2.connect("postgresql://postgres:EAD%4025scse1280014@db.rvanooyrwksbbakiypsg.supabase.co:5432/postgres")
    conn.autocommit = True
    with conn.cursor() as cur:
        with open("schema.sql", "r") as f:
            cur.execute(f.read())
    print("Schema applied successfully.")

if __name__ == "__main__":
    install_and_run()
