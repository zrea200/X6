#!/usr/bin/env python3
"""
检查数据库内容
"""
import sqlite3

def check_database():
    """检查数据库内容"""
    try:
        conn = sqlite3.connect('test.db')
        cursor = conn.cursor()
        
        # 检查用户表
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        print(f"用户数量: {user_count}")
        
        if user_count > 0:
            cursor.execute("SELECT id, username, email, is_active, is_superuser FROM users")
            users = cursor.fetchall()
            print("用户列表:")
            for user in users:
                print(f"  ID: {user[0]}, 用户名: {user[1]}, 邮箱: {user[2]}, 活跃: {user[3]}, 超级用户: {user[4]}")
        else:
            print("数据库中没有用户")
        
        conn.close()
        
    except Exception as e:
        print(f"检查数据库失败: {e}")

if __name__ == "__main__":
    check_database()
