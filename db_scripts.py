import PySimpleGUI as sg
import sqlite3
from sqlite3 import Error

sg.theme('DarkGrey9')
debug=sg.Print
#debug('db_scripts.py imported', keep_on_top=False, relative_location=(-300,100))

#connect to the sqlite3 database
#return conn
####################################
def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        
        #debug("sqlite3 version:", sqlite3.version)
        #debug("total changes:", conn.total_changes)
        #debug("connection to the database is established")
        
        return conn
    except Error as e:
        debug("Error: ", e)
        #pass
    return conn

def create_table_tasks(conn):
    sql = """ CREATE TABLE IF NOT EXISTS tasks (
        id integer PRIMARY KEY,
        date text,
        focus_time text,
        break_time text,
        task_name text
    );"""
    if conn is not None:
        try:
            cur = conn.cursor()
            cur.execute(sql)
            
            #debug('created table')
            
        except Error as e:
            debug(e)
            #pass
    
        conn.close()
        
        
        return conn
    else:
        #pass
        debug("Error! cannot create the database connection")

def insert_data(conn, py_data):
    sql = """ INSERT INTO tasks (
        date,
        focus_time,
        break_time,
        task_name
    ) VALUES(?,?,?,?)"""
    if conn is not None:
        try:
            cur = conn.cursor()
            
            cur.execute(sql, py_data)
            conn.commit()
            
            #debug('inserted data')
        except Error as e:
            #pass
            debug(e)
            

        conn.close()
        #debug("connection closed")
        
        return cur.lastrowid
    else:
        #pass
        debug("Error! cannot create the database connection")



def sql_select(conn, sql, conditions):
    if conn is not None:
        try:
            cur = conn.cursor()
            
            cur.execute(sql, conditions)
            rows = cur.fetchall()
            
            
            #for row in rows:
                #debug(row)
            
            return rows
        except Error as e:
            debug(e)
    
        conn.close()
        #debug("connection closed")
        return cur.lastrowid
    else:
        debug("Error! cannot create the database connection")

#gotta be careful, it's not date format, it's text
def select_date_range(conn, start_date, end_date):
    sql = """
    SELECT *
    FROM tasks
    WHERE date
    BETWEEN ? AND ?
    ORDER BY date ASC
    """
    conditions = (start_date, end_date)
    
    return sql_select(conn, sql, conditions)

def select_all_for_total(conn):
    sql = """
    SELECT *
    FROM tasks
    ORDER BY date ASC
    """
    if conn is not None:
        try:
            cur = conn.cursor()
            
            cur.execute(sql)
            rows = cur.fetchall()
            #debug('selected data')
            #for row in rows:
                #debug(row)
            return rows
        except Error as e:
            debug(e)
    
        conn.close()
        #debug("connection closed")
        return cur.lastrowid
    else:
        debug("Error! cannot create the database connection")