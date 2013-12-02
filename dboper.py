#coding=utf-8
import sqlite3

class Dboper:
    def __init__(self, databasename):
        self.conn = sqlite3.connect(databasename)
        self.cur = self.conn.cursor()
        
    def isExistTable(self, tableName='result'):
        """
        判断result表是否存在
        """
        sql = "SELECT COUNT(*) FROM sqlite_master where type='table' and name='%s'" % tableName
        res = self.cur.execute(sql)
        r = self.cur.fetchone()
        return r[0]
        
    def createTable(self, tableName='result'):
        """
        创建result表
        """
        sql = """
            CREATE TABLE %s(
            id INTEGER PRIMARY KEY NOT NULL,
            url TEXT,
            depth INT,
            keyword TEXT);
        """ % tableName
        self.cur.execute(sql)
        self.conn.commit()
        
    def clearTable(self, tableName="result"):
        """
        清空数据库
        """
        sql = """
        DROP TABLE %s;
        """ % tableName
        self.cur.execute(sql)
        self.createTable(tableName)
        self.conn.commit()
        
    def insert(self, tableName="result", url="", depth=0, keyword=""):
        """
        向数据库中插入url
        """
        sql = "INSERT INTO %s(url, depth, keyword) VALUES('%s', %d, '%s')" % (tableName, url, depth, keyword)
        self.cur.execute(sql)
        self.conn.commit()
        
    def select_count(self, tableName="result", url=""):
        """
        判断数据库中是否存在url，不存在则返回0
        """
        sql = "SELECT COUNT(*) FROM %s WHERE url='%s'" % (tableName, url)
        res = self.cur.execute(sql)
        r = self.cur.fetchone()
        return r[0]
    
        
    def __del__(self):
        self.conn.close()
        

if __name__ =="__main__":
    db = Dboper("test.db")
    url = "http://www.baidu.com/"
    domain = "baidu.com".replace('.','_')
    db.createTable(domain)
    db.insert(domain, url)