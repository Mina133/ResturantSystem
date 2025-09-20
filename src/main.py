#!/usr/bin/env python3
"""
نظام إدارة المطاعم المحسن - تطبيق Flask
نظام شامل لإدارة المطاعم والمقاهي باللغة العربية مع معالجة محسنة للأخطاء
"""

import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_from_directory, render_template_string
from flask_cors import CORS
import sqlite3
import hashlib
from datetime import datetime, date
import json
import uuid
import traceback

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.secret_key = 'arabic_restaurant_management_fixed_2024'
CORS(app)

# إعداد قاعدة البيانات
DATABASE = os.path.join(os.path.dirname(__file__), 'database', 'restaurant_arabic_fixed.db')

def get_db_connection():
    """إنشاء اتصال آمن بقاعدة البيانات"""
    try:
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

def init_db():
    """تهيئة قاعدة البيانات مع جميع الجداول المطلوبة"""
    try:
        # التأكد من وجود مجلد قاعدة البيانات
        os.makedirs(os.path.dirname(DATABASE), exist_ok=True)
        
        conn = get_db_connection()
        if not conn:
            return False
            
        cursor = conn.cursor()
        
        # جدول المستخدمين
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                full_name VARCHAR(100) NOT NULL,
                role VARCHAR(20) DEFAULT 'staff',
                location_id INTEGER DEFAULT 1,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        ''')
        
        # جدول المحافظات
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS governorates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) NOT NULL,
                code VARCHAR(10) UNIQUE NOT NULL,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # جدول المناطق
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS regions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) NOT NULL,
                code VARCHAR(10) NOT NULL,
                governorate_id INTEGER NOT NULL,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (governorate_id) REFERENCES governorates(id)
            )
        ''')
        
        # جدول الفروع
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS locations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) NOT NULL,
                code VARCHAR(10) UNIQUE NOT NULL,
                address TEXT,
                phone VARCHAR(20),
                governorate_id INTEGER,
                region_id INTEGER,
                manager_name VARCHAR(100),
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (governorate_id) REFERENCES governorates(id),
                FOREIGN KEY (region_id) REFERENCES regions(id)
            )
        ''')
        
        # جدول مجموعات الأصناف
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS item_groups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) NOT NULL,
                code VARCHAR(20) UNIQUE NOT NULL,
                description TEXT,
                parent_id INTEGER,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (parent_id) REFERENCES item_groups(id)
            )
        ''')
        
        # جدول الأقسام
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS departments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) NOT NULL,
                code VARCHAR(20) UNIQUE NOT NULL,
                description TEXT,
                manager_name VARCHAR(100),
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # جدول كارت الصنف (الأصناف)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(200) NOT NULL,
                arabic_name VARCHAR(200),
                code VARCHAR(50) UNIQUE NOT NULL,
                barcode VARCHAR(50),
                description TEXT,
                group_id INTEGER,
                department_id INTEGER,
                unit_of_measure VARCHAR(20) NOT NULL,
                cost_price DECIMAL(10,2) DEFAULT 0,
                selling_price DECIMAL(10,2) NOT NULL,
                min_stock DECIMAL(10,2) DEFAULT 0,
                max_stock DECIMAL(10,2) DEFAULT 0,
                reorder_level DECIMAL(10,2) DEFAULT 0,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (group_id) REFERENCES item_groups(id),
                FOREIGN KEY (department_id) REFERENCES departments(id)
            )
        ''')
        
        # جدول الموردين
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS suppliers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(200) NOT NULL,
                code VARCHAR(20) UNIQUE NOT NULL,
                contact_person VARCHAR(100),
                phone VARCHAR(20),
                mobile VARCHAR(20),
                email VARCHAR(100),
                address TEXT,
                governorate_id INTEGER,
                region_id INTEGER,
                tax_number VARCHAR(50),
                commercial_register VARCHAR(50),
                payment_terms VARCHAR(50),
                credit_limit DECIMAL(12,2) DEFAULT 0,
                current_balance DECIMAL(12,2) DEFAULT 0,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (governorate_id) REFERENCES governorates(id),
                FOREIGN KEY (region_id) REFERENCES regions(id)
            )
        ''')
        
        # جدول العملاء
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(200) NOT NULL,
                code VARCHAR(20) UNIQUE NOT NULL,
                phone VARCHAR(20),
                mobile VARCHAR(20),
                email VARCHAR(100),
                address TEXT,
                governorate_id INTEGER,
                region_id INTEGER,
                customer_type VARCHAR(20) DEFAULT 'regular',
                credit_limit DECIMAL(12,2) DEFAULT 0,
                current_balance DECIMAL(12,2) DEFAULT 0,
                discount_percentage DECIMAL(5,2) DEFAULT 0,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (governorate_id) REFERENCES governorates(id),
                FOREIGN KEY (region_id) REFERENCES regions(id)
            )
        ''')
        
        # جدول الطيارين
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS delivery_drivers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) NOT NULL,
                code VARCHAR(20) UNIQUE NOT NULL,
                phone VARCHAR(20) NOT NULL,
                mobile VARCHAR(20),
                license_number VARCHAR(50),
                vehicle_type VARCHAR(50),
                vehicle_number VARCHAR(20),
                location_id INTEGER NOT NULL,
                commission_percentage DECIMAL(5,2) DEFAULT 0,
                fixed_commission DECIMAL(10,2) DEFAULT 0,
                current_balance DECIMAL(12,2) DEFAULT 0,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (location_id) REFERENCES locations(id)
            )
        ''')
        
        # جدول المبيعات (للإحصائيات)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_number VARCHAR(50) UNIQUE NOT NULL,
                customer_id INTEGER,
                location_id INTEGER NOT NULL,
                total_amount DECIMAL(12,2) NOT NULL,
                payment_method VARCHAR(20) DEFAULT 'cash',
                sale_date DATE NOT NULL,
                user_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES customers(id),
                FOREIGN KEY (location_id) REFERENCES locations(id),
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        conn.commit()
        
        # إدراج البيانات الافتراضية
        cursor.execute('SELECT COUNT(*) FROM users')
        if cursor.fetchone()[0] == 0:
            # إدراج مستخدمين متعددين
            users = [
                ('admin', 'admin@restaurant.com', 'password', 'مدير النظام', 'admin', 1),
                ('manager', 'manager@restaurant.com', '123456', 'مدير الفرع', 'manager', 1),
                ('cashier', 'cashier@restaurant.com', 'cashier123', 'أمين الصندوق', 'cashier', 1),
                ('waiter', 'waiter@restaurant.com', 'waiter123', 'النادل', 'staff', 1),
                ('supervisor', 'supervisor@restaurant.com', 'super123', 'المشرف العام', 'supervisor', 1)
            ]
            
            for username, email, password, full_name, role, location_id in users:
                password_hash = hashlib.md5(password.encode()).hexdigest()
                cursor.execute('''
                    INSERT INTO users (username, email, password, full_name, role, location_id)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (username, email, password_hash, full_name, role, location_id))
            
            # إدراج المحافظات
            governorates = [
                ('القاهرة', 'CAI'),
                ('الجيزة', 'GIZ'),
                ('الإسكندرية', 'ALX'),
                ('القليوبية', 'QAL'),
                ('الشرقية', 'SHR')
            ]
            
            for gov_name, gov_code in governorates:
                cursor.execute('''
                    INSERT INTO governorates (name, code)
                    VALUES (?, ?)
                ''', (gov_name, gov_code))
            
            # إدراج المناطق
            regions = [
                ('وسط القاهرة', 'CAI01', 1),
                ('مصر الجديدة', 'CAI02', 1),
                ('المعادي', 'CAI03', 1),
                ('الدقي', 'GIZ01', 2),
                ('المهندسين', 'GIZ02', 2),
                ('الهرم', 'GIZ03', 2),
                ('سيدي جابر', 'ALX01', 3),
                ('المنتزه', 'ALX02', 3)
            ]
            
            for reg_name, reg_code, gov_id in regions:
                cursor.execute('''
                    INSERT INTO regions (name, code, governorate_id)
                    VALUES (?, ?, ?)
                ''', (reg_name, reg_code, gov_id))
            
            # إدراج الفروع
            locations = [
                ('الفرع الرئيسي - وسط القاهرة', 'BR001', 'شارع التحرير، وسط القاهرة', '02-25555555', 1, 1, 'أحمد محمد'),
                ('فرع مصر الجديدة', 'BR002', 'شارع العروبة، مصر الجديدة', '02-26666666', 1, 2, 'سارة أحمد'),
                ('فرع الجيزة', 'BR003', 'شارع الهرم، الجيزة', '02-33777777', 2, 6, 'محمد علي'),
                ('فرع الإسكندرية', 'BR004', 'كورنيش الإسكندرية', '03-4888888', 3, 7, 'فاطمة حسن')
            ]
            
            for loc_name, loc_code, address, phone, gov_id, reg_id, manager in locations:
                cursor.execute('''
                    INSERT INTO locations (name, code, address, phone, governorate_id, region_id, manager_name)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (loc_name, loc_code, address, phone, gov_id, reg_id, manager))
            
            # إدراج مجموعات الأصناف
            item_groups = [
                ('الدجاج المقلي', 'FC001', 'أصناف الدجاج المقلي'),
                ('البرجر', 'BG001', 'أنواع البرجر المختلفة'),
                ('الأطباق الجانبية', 'SD001', 'الأطباق المرافقة'),
                ('المشروبات', 'BV001', 'المشروبات الباردة والساخنة'),
                ('الحلويات', 'DS001', 'الحلويات والآيس كريم'),
                ('القهوة والشاي', 'CT001', 'مشروبات القهوة والشاي')
            ]
            
            for group_name, group_code, description in item_groups:
                cursor.execute('''
                    INSERT INTO item_groups (name, code, description)
                    VALUES (?, ?, ?)
                ''', (group_name, group_code, description))
            
            # إدراج الأقسام
            departments = [
                ('المطبخ', 'KITCH', 'قسم المطبخ والطبخ', 'رئيس الطباخين'),
                ('المشروبات', 'BEVG', 'قسم تحضير المشروبات', 'مسؤول المشروبات'),
                ('الكاشير', 'CASH', 'قسم الكاشير والمبيعات', 'رئيس الكاشيرات'),
                ('التوصيل', 'DELV', 'قسم التوصيل والطيارين', 'مسؤول التوصيل')
            ]
            
            for dept_name, dept_code, description, manager in departments:
                cursor.execute('''
                    INSERT INTO departments (name, code, description, manager_name)
                    VALUES (?, ?, ?, ?)
                ''', (dept_name, dept_code, description, manager))
            
            # إدراج أصناف العينة
            items = [
                ('دجاج بالوصفة الأصلية', 'دجاج بالوصفة الأصلية', 'FC001', '1234567890123', 'دجاج مقلي بالوصفة الأصلية المميزة', 1, 1, 'قطعة', 12.00, 25.00, 10, 100, 20),
                ('أجنحة دجاج حارة', 'أجنحة دجاج حارة', 'FC002', '1234567890124', 'أجنحة دجاج مقرمشة بالتتبيلة الحارة', 1, 1, 'قطعة', 10.00, 22.00, 15, 150, 25),
                ('قطع دجاج مقرمشة', 'قطع دجاج مقرمشة', 'FC003', '1234567890125', 'قطع دجاج طرية ومقرمشة', 1, 1, 'قطعة', 9.00, 20.00, 20, 200, 30),
                ('برجر كلاسيكي', 'برجر كلاسيكي', 'BG001', '1234567890126', 'برجر لحم بقري مع الخضار والصوص المميز', 2, 1, 'قطعة', 8.00, 18.00, 10, 100, 15),
                ('برجر دجاج', 'برجر دجاج', 'BG002', '1234567890127', 'برجر دجاج مشوي مع الخضار الطازجة', 2, 1, 'قطعة', 7.50, 16.00, 10, 100, 15),
                ('بطاطس مقلية', 'بطاطس مقلية', 'SD001', '1234567890128', 'بطاطس مقلية ذهبية مقرمشة', 3, 1, 'طبق', 3.00, 8.00, 20, 200, 30),
                ('سلطة كولسلو', 'سلطة كولسلو', 'SD002', '1234567890129', 'سلطة كرنب وجزر طازجة', 3, 1, 'طبق', 2.50, 6.00, 10, 100, 20),
                ('كوكا كولا', 'كوكا كولا', 'BV001', '1234567890130', 'كوكا كولا كلاسيك', 4, 1, 'علبة', 2.00, 5.00, 50, 500, 100),
                ('عصير برتقال طازج', 'عصير برتقال طازج', 'BV002', '1234567890131', 'عصير برتقال طبيعي طازج', 4, 2, 'كوب', 3.50, 8.00, 20, 200, 40),
                ('كيكة الشوكولاتة', 'كيكة الشوكولاتة', 'DS001', '1234567890132', 'قطعة كيك شوكولاتة غنية', 5, 1, 'قطعة', 5.00, 12.00, 10, 100, 20),
                ('قهوة', 'قهوة', 'CT001', '1234567890133', 'قهوة عربية فاخرة', 6, 2, 'كوب', 2.50, 7.00, 30, 300, 50),
                ('شاي', 'شاي', 'CT002', '1234567890134', 'شاي تقليدي', 6, 2, 'كوب', 1.50, 4.00, 50, 500, 100)
            ]
            
            for item in items:
                cursor.execute('''
                    INSERT INTO items (name, arabic_name, code, barcode, description, group_id, department_id, 
                                     unit_of_measure, cost_price, selling_price, min_stock, max_stock, reorder_level)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', item)
            
            # إدراج بيانات مبيعات تجريبية للإحصائيات
            sales_data = [
                ('ORD001', None, 1, 150.50, 'cash', '2024-09-16', 1),
                ('ORD002', None, 1, 89.25, 'card', '2024-09-16', 1),
                ('ORD003', None, 1, 234.75, 'cash', '2024-09-16', 2),
                ('ORD004', None, 2, 67.00, 'cash', '2024-09-15', 1),
                ('ORD005', None, 1, 123.50, 'card', '2024-09-15', 3)
            ]
            
            for sale in sales_data:
                cursor.execute('''
                    INSERT INTO sales (order_number, customer_id, location_id, total_amount, payment_method, sale_date, user_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', sale)
            
            conn.commit()
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"Database initialization error: {e}")
        traceback.print_exc()
        return False

@app.route('/')
def index():
    """الصفحة الرئيسية - إعادة توجيه لصفحة تسجيل الدخول"""
    if 'user_id' in session:
        return redirect('/dashboard')
    return redirect('/login')

@app.route('/login')
def login_page():
    """صفحة تسجيل الدخول"""
    return render_template_string(LOGIN_TEMPLATE)

@app.route('/dashboard')
def dashboard():
    """لوحة التحكم الرئيسية"""
    if 'user_id' not in session:
        return redirect('/login')
    return render_template_string(DASHBOARD_TEMPLATE)

# قوالب HTML
LOGIN_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>تسجيل الدخول - نظام إدارة المطاعم</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        .login-card {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            padding: 3rem;
            max-width: 500px;
            width: 100%;
        }
        .login-header {
            text-align: center;
            margin-bottom: 2rem;
        }
        .login-header i {
            font-size: 3rem;
            color: #667eea;
            margin-bottom: 1rem;
        }
        .form-control {
            border-radius: 10px;
            padding: 12px 15px;
            border: 2px solid #e9ecef;
            margin-bottom: 1rem;
        }
        .btn-login {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            border-radius: 10px;
            padding: 12px;
            color: white;
            font-weight: bold;
            width: 100%;
        }
        .demo-credentials {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 1.5rem;
            margin-top: 1rem;
            font-size: 0.9rem;
        }
        .user-option {
            background: #e3f2fd;
            border: 1px solid #2196f3;
            border-radius: 8px;
            padding: 10px;
            margin: 5px 0;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        .user-option:hover {
            background: #bbdefb;
            transform: translateY(-1px);
        }
        .user-option.selected {
            background: #2196f3;
            color: white;
        }
        .alert {
            border-radius: 10px;
            margin-top: 1rem;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="row justify-content-center">
            <div class="col-md-8">
                <div class="login-card">
                    <div class="login-header">
                        <i class="fas fa-utensils"></i>
                        <h2>نظام إدارة المطاعم المحسن</h2>
                        <p class="text-muted">تسجيل الدخول إلى حسابك</p>
                    </div>
                    
                    <div id="alertContainer"></div>
                    
                    <form id="loginForm">
                        <div class="mb-3">
                            <div class="input-group">
                                <span class="input-group-text"><i class="fas fa-user"></i></span>
                                <input type="text" class="form-control" id="username" placeholder="اسم المستخدم أو البريد الإلكتروني" required>
                            </div>
                        </div>
                        
                        <div class="mb-3">
                            <div class="input-group">
                                <span class="input-group-text"><i class="fas fa-lock"></i></span>
                                <input type="password" class="form-control" id="password" placeholder="كلمة المرور" required>
                            </div>
                        </div>
                        
                        <button type="submit" class="btn btn-login">
                            <i class="fas fa-sign-in-alt me-2"></i>
                            تسجيل الدخول
                        </button>
                    </form>
                    
                    <div class="demo-credentials">
                        <h5><i class="fas fa-users"></i> <strong>حسابات التجربة المتاحة</strong></h5>
                        <div class="row">
                            <div class="col-md-6">
                                <div class="user-option" onclick="selectUser('admin', 'password')">
                                    <strong>👨‍💼 مدير النظام</strong><br>
                                    <small>admin / password</small>
                                </div>
                                <div class="user-option" onclick="selectUser('manager', '123456')">
                                    <strong>👨‍💻 مدير الفرع</strong><br>
                                    <small>manager / 123456</small>
                                </div>
                                <div class="user-option" onclick="selectUser('supervisor', 'super123')">
                                    <strong>👨‍🏫 المشرف العام</strong><br>
                                    <small>supervisor / super123</small>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="user-option" onclick="selectUser('cashier', 'cashier123')">
                                    <strong>💰 أمين الصندوق</strong><br>
                                    <small>cashier / cashier123</small>
                                </div>
                                <div class="user-option" onclick="selectUser('waiter', 'waiter123')">
                                    <strong>🍽️ النادل</strong><br>
                                    <small>waiter / waiter123</small>
                                </div>
                            </div>
                        </div>
                        
                        <div class="mt-3 p-2 bg-info text-white rounded">
                            <small><i class="fas fa-info-circle"></i> انقر على أي حساب لملء البيانات تلقائياً</small>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        function selectUser(username, password) {
            document.getElementById('username').value = username;
            document.getElementById('password').value = password;
            
            // إزالة التحديد السابق
            document.querySelectorAll('.user-option').forEach(el => el.classList.remove('selected'));
            
            // تحديد الخيار الحالي
            event.target.closest('.user-option').classList.add('selected');
        }
        
        function showAlert(message, type = 'danger') {
            const alertContainer = document.getElementById('alertContainer');
            alertContainer.innerHTML = `
                <div class="alert alert-${type} alert-dismissible fade show" role="alert">
                    ${message}
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                </div>
            `;
        }
        
        document.getElementById('loginForm').addEventListener('submit', function(e) {
            e.preventDefault();
            
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            
            if (!username || !password) {
                showAlert('يرجى إدخال اسم المستخدم وكلمة المرور');
                return;
            }
            
            // إظهار مؤشر التحميل
            const submitBtn = document.querySelector('.btn-login');
            const originalText = submitBtn.innerHTML;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>جاري تسجيل الدخول...';
            submitBtn.disabled = true;
            
            fetch('/api/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    username: username,
                    password: password
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showAlert('تم تسجيل الدخول بنجاح! جاري التحويل...', 'success');
                    setTimeout(() => {
                        window.location.href = data.redirect;
                    }, 1500);
                } else {
                    showAlert('خطأ في تسجيل الدخول: ' + data.message);
                    submitBtn.innerHTML = originalText;
                    submitBtn.disabled = false;
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showAlert('حدث خطأ في الاتصال. يرجى المحاولة مرة أخرى.');
                submitBtn.innerHTML = originalText;
                submitBtn.disabled = false;
            });
        });
    </script>
</body>
</html>
'''

DASHBOARD_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>لوحة التحكم - نظام إدارة المطاعم</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body {
            background-color: #f8f9fa;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        .sidebar {
            background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: white;
            padding: 0;
            position: fixed;
            top: 0;
            right: 0;
            width: 280px;
            overflow-y: auto;
            z-index: 1000;
        }
        .sidebar-header {
            padding: 1.5rem;
            background: rgba(0,0,0,0.1);
            text-align: center;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        .sidebar-menu {
            padding: 1rem 0;
        }
        .menu-item {
            display: block;
            color: white;
            text-decoration: none;
            padding: 12px 20px;
            border: none;
            background: none;
            width: 100%;
            text-align: right;
            transition: all 0.3s ease;
            border-left: 3px solid transparent;
        }
        .menu-item:hover {
            background: rgba(255,255,255,0.1);
            color: white;
            border-left-color: #fff;
        }
        .menu-item.active {
            background: rgba(255,255,255,0.2);
            border-left-color: #fff;
        }
        .submenu {
            background: rgba(0,0,0,0.1);
            display: none;
        }
        .submenu.show {
            display: block;
        }
        .submenu .menu-item {
            padding-right: 40px;
            font-size: 0.9rem;
        }
        .main-content {
            margin-right: 280px;
            padding: 2rem;
        }
        .welcome-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 15px;
            padding: 2rem;
            margin-bottom: 2rem;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        .stats-card {
            background: white;
            border-radius: 15px;
            padding: 1.5rem;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            text-align: center;
            margin-bottom: 1.5rem;
            transition: transform 0.3s ease;
        }
        .stats-card:hover {
            transform: translateY(-5px);
        }
        .stats-icon {
            font-size: 3rem;
            margin-bottom: 1rem;
        }
        .quick-actions {
            background: white;
            border-radius: 15px;
            padding: 1.5rem;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        .action-btn {
            border-radius: 10px;
            padding: 15px 20px;
            margin: 5px;
            border: none;
            color: white;
            font-weight: bold;
            text-decoration: none;
            display: inline-block;
            transition: all 0.3s ease;
            text-align: center;
            min-width: 120px;
        }
        .action-btn:hover {
            transform: translateY(-2px);
            color: white;
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }
        .user-info {
            background: rgba(255,255,255,0.1);
            border-radius: 10px;
            padding: 1rem;
            margin-bottom: 1rem;
        }
        @media (max-width: 768px) {
            .sidebar {
                width: 100%;
                position: relative;
            }
            .main-content {
                margin-right: 0;
            }
        }
    </style>
</head>
<body>
    <div class="container-fluid">
        <div class="row">
            <!-- الشريط الجانبي -->
            <div class="sidebar">
                <div class="sidebar-header">
                    <h4><i class="fas fa-utensils me-2"></i>نظام إدارة المطاعم</h4>
                    <div class="user-info">
                        <small id="userWelcome">مرحباً، مستخدم</small><br>
                        <small id="userRole">الدور: موظف</small>
                    </div>
                </div>
                
                <div class="sidebar-menu">
                    <a href="/dashboard" class="menu-item active">
                        <i class="fas fa-tachometer-alt me-2"></i>لوحة التحكم
                    </a>
                    
                    <!-- التكويدات -->
                    <button class="menu-item" onclick="toggleSubmenu('codings')">
                        <i class="fas fa-cog me-2"></i>التكويدات
                        <i class="fas fa-chevron-down float-start mt-1"></i>
                    </button>
                    <div id="codings" class="submenu">
                        <a href="#" class="menu-item">المحافظة</a>
                        <a href="#" class="menu-item">المنطقة</a>
                    </div>
                    
                    <!-- الأصناف -->
                    <button class="menu-item" onclick="toggleSubmenu('items')">
                        <i class="fas fa-boxes me-2"></i>الأصناف
                        <i class="fas fa-chevron-down float-start mt-1"></i>
                    </button>
                    <div id="items" class="submenu">
                        <a href="#" class="menu-item">مجموعات الأصناف</a>
                        <a href="#" class="menu-item">القسم</a>
                        <a href="#" class="menu-item">كارت الصنف</a>
                        <a href="#" class="menu-item">تقارير الأصناف</a>
                    </div>
                    
                    <!-- المشتريات -->
                    <button class="menu-item" onclick="toggleSubmenu('purchases')">
                        <i class="fas fa-shopping-cart me-2"></i>المشتريات
                        <i class="fas fa-chevron-down float-start mt-1"></i>
                    </button>
                    <div id="purchases" class="submenu">
                        <a href="#" class="menu-item">قائمة المشتريات</a>
                        <a href="#" class="menu-item">الموردين</a>
                        <a href="#" class="menu-item">فاتورة المشتريات</a>
                        <a href="#" class="menu-item">مرتد المشتريات</a>
                        <a href="#" class="menu-item">تقارير المشتريات</a>
                        <a href="#" class="menu-item">تقارير مرتدات المشتريات</a>
                    </div>
                    
                    <!-- المخازن -->
                    <button class="menu-item" onclick="toggleSubmenu('warehouses')">
                        <i class="fas fa-warehouse me-2"></i>المخازن
                        <i class="fas fa-chevron-down float-start mt-1"></i>
                    </button>
                    <div id="warehouses" class="submenu">
                        <a href="#" class="menu-item">الرصيد الافتتاحي</a>
                        <a href="#" class="menu-item">جرد وتعديل كميات</a>
                        <a href="#" class="menu-item">إهلاك المخزون</a>
                        <a href="#" class="menu-item">التحويلات المخزنية</a>
                        <a href="#" class="menu-item">التحويل بين الفروع</a>
                        <a href="#" class="menu-item">تقارير المخازن</a>
                    </div>
                    
                    <!-- الخزينة -->
                    <button class="menu-item" onclick="toggleSubmenu('treasury')">
                        <i class="fas fa-cash-register me-2"></i>الخزينة
                        <i class="fas fa-chevron-down float-start mt-1"></i>
                    </button>
                    <div id="treasury" class="submenu">
                        <a href="#" class="menu-item">مجموعات الإيرادات</a>
                        <a href="#" class="menu-item">الإيرادات</a>
                        <a href="#" class="menu-item">مجموعات المصروفات</a>
                        <a href="#" class="menu-item">المصروفات</a>
                        <a href="#" class="menu-item">إيصال استلام نقدية</a>
                        <a href="#" class="menu-item">إيصال صرف نقدية</a>
                        <a href="#" class="menu-item">التحويلات المالية</a>
                    </div>
                    
                    <!-- الورديات -->
                    <button class="menu-item" onclick="toggleSubmenu('shifts')">
                        <i class="fas fa-clock me-2"></i>الورديات
                        <i class="fas fa-chevron-down float-start mt-1"></i>
                    </button>
                    <div id="shifts" class="submenu">
                        <a href="#" class="menu-item">الوردية</a>
                        <a href="#" class="menu-item">تفاصيل الوردية</a>
                        <a href="#" class="menu-item">تقارير استلام النقدية</a>
                        <a href="#" class="menu-item">تقارير صرف النقدية</a>
                        <a href="#" class="menu-item">تقارير الحسابات</a>
                        <a href="#" class="menu-item">تقارير الورديات</a>
                    </div>
                    
                    <!-- المطعم -->
                    <button class="menu-item" onclick="toggleSubmenu('restaurant')">
                        <i class="fas fa-utensils me-2"></i>المطعم
                        <i class="fas fa-chevron-down float-start mt-1"></i>
                    </button>
                    <div id="restaurant" class="submenu">
                        <a href="#" class="menu-item">نقطة البيع</a>
                        <a href="#" class="menu-item">تقارير المطعم</a>
                        <a href="#" class="menu-item">حساب الطيارين</a>
                        <a href="#" class="menu-item">تحميل الطيارين</a>
                    </div>
                    
                    <!-- العملاء والطيارين -->
                    <button class="menu-item" onclick="toggleSubmenu('customers')">
                        <i class="fas fa-users me-2"></i>العملاء والطيارين
                        <i class="fas fa-chevron-down float-start mt-1"></i>
                    </button>
                    <div id="customers" class="submenu">
                        <a href="#" class="menu-item">العملاء</a>
                        <a href="#" class="menu-item">الطيارين</a>
                        <a href="#" class="menu-item">مجموعة المندوبين</a>
                    </div>
                    
                    <!-- مديول الإنتاج -->
                    <button class="menu-item" onclick="toggleSubmenu('production')">
                        <i class="fas fa-industry me-2"></i>مديول الإنتاج
                        <i class="fas fa-chevron-down float-start mt-1"></i>
                    </button>
                    <div id="production" class="submenu">
                        <a href="#" class="menu-item">مكونات الأصناف</a>
                        <a href="#" class="menu-item">شاشة تصنيع</a>
                    </div>
                    
                    <!-- الصلاحيات -->
                    <button class="menu-item" onclick="toggleSubmenu('permissions')">
                        <i class="fas fa-shield-alt me-2"></i>الصلاحيات
                        <i class="fas fa-chevron-down float-start mt-1"></i>
                    </button>
                    <div id="permissions" class="submenu">
                        <a href="#" class="menu-item">تسجيل الباسوردات</a>
                        <a href="#" class="menu-item">خصومات المستخدمين</a>
                    </div>
                    
                    <!-- تسجيل الخروج -->
                    <button class="menu-item" onclick="logout()" style="margin-top: 2rem; border-top: 1px solid rgba(255,255,255,0.1);">
                        <i class="fas fa-sign-out-alt me-2"></i>تسجيل الخروج
                    </button>
                </div>
            </div>
            
            <!-- المحتوى الرئيسي -->
            <div class="main-content">
                <!-- بطاقة الترحيب -->
                <div class="welcome-card">
                    <h2><i class="fas fa-home me-2"></i>مرحباً بك في نظام إدارة المطاعم!</h2>
                    <p><i class="fas fa-map-marker-alt me-2"></i>الموقع: <span id="locationName">الفرع الرئيسي - وسط القاهرة</span></p>
                    <p><i class="fas fa-user-tag me-2"></i>الدور: <span id="userRoleMain">مدير</span></p>
                    <p><i class="fas fa-calendar me-2"></i>التاريخ: <span id="currentDate"></span></p>
                </div>
                
                <!-- بطاقات الإحصائيات -->
                <div class="row">
                    <div class="col-md-3">
                        <div class="stats-card">
                            <div class="stats-icon text-primary">
                                <i class="fas fa-shopping-cart"></i>
                            </div>
                            <h3 id="todayOrders">0</h3>
                            <p>طلبات اليوم</p>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="stats-card">
                            <div class="stats-icon text-success">
                                <i class="fas fa-dollar-sign"></i>
                            </div>
                            <h3 id="todayRevenue">0.00 جنيه</h3>
                            <p>إيرادات اليوم</p>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="stats-card">
                            <div class="stats-icon text-info">
                                <i class="fas fa-users"></i>
                            </div>
                            <h3 id="totalCustomers">0</h3>
                            <p>إجمالي العملاء</p>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="stats-card">
                            <div class="stats-icon text-warning">
                                <i class="fas fa-utensils"></i>
                            </div>
                            <h3 id="menuItems">12</h3>
                            <p>أصناف القائمة</p>
                        </div>
                    </div>
                </div>
                
                <!-- الإجراءات السريعة -->
                <div class="quick-actions">
                    <h4><i class="fas fa-bolt me-2"></i>الإجراءات السريعة</h4>
                    <div class="row mt-3">
                        <div class="col-md-2">
                            <a href="#" class="action-btn" style="background: #007bff;">
                                <i class="fas fa-cash-register"></i><br>طلب جديد
                            </a>
                        </div>
                        <div class="col-md-2">
                            <a href="#" class="action-btn" style="background: #28a745;">
                                <i class="fas fa-plus"></i><br>إضافة صنف
                            </a>
                        </div>
                        <div class="col-md-2">
                            <a href="#" class="action-btn" style="background: #17a2b8;">
                                <i class="fas fa-user-plus"></i><br>إضافة عميل
                            </a>
                        </div>
                        <div class="col-md-2">
                            <a href="#" class="action-btn" style="background: #ffc107;">
                                <i class="fas fa-boxes"></i><br>فحص المخزون
                            </a>
                        </div>
                        <div class="col-md-2">
                            <a href="#" class="action-btn" style="background: #6f42c1;">
                                <i class="fas fa-chart-bar"></i><br>عرض التقارير
                            </a>
                        </div>
                        <div class="col-md-2">
                            <a href="#" class="action-btn" style="background: #6c757d;">
                                <i class="fas fa-cogs"></i><br>الإعدادات
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        function toggleSubmenu(id) {
            const submenu = document.getElementById(id);
            submenu.classList.toggle('show');
        }
        
        function logout() {
            if (confirm('هل أنت متأكد من تسجيل الخروج؟')) {
                fetch('/api/logout', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        window.location.href = data.redirect;
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    window.location.href = '/login';
                });
            }
        }
        
        // تحميل الإحصائيات
        function loadStats() {
            fetch('/api/dashboard-stats')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('todayOrders').textContent = data.todays_orders;
                    document.getElementById('todayRevenue').textContent = data.todays_revenue.toFixed(2) + ' جنيه';
                    document.getElementById('totalCustomers').textContent = data.total_customers;
                    document.getElementById('menuItems').textContent = data.menu_items;
                })
                .catch(error => console.error('Error loading stats:', error));
        }
        
        // تحميل معلومات المستخدم
        function loadUserInfo() {
            fetch('/api/user-info')
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        document.getElementById('userWelcome').textContent = 'مرحباً، ' + data.full_name;
                        document.getElementById('userRole').textContent = 'الدور: ' + data.role_arabic;
                        document.getElementById('userRoleMain').textContent = data.role_arabic;
                        document.getElementById('locationName').textContent = data.location_name;
                    }
                })
                .catch(error => console.error('Error loading user info:', error));
        }
        
        // تحديث التاريخ
        function updateDate() {
            const now = new Date();
            const options = { 
                year: 'numeric', 
                month: 'long', 
                day: 'numeric',
                weekday: 'long'
            };
            document.getElementById('currentDate').textContent = now.toLocaleDateString('ar-EG', options);
        }
        
        // تحميل البيانات عند تحميل الصفحة
        document.addEventListener('DOMContentLoaded', function() {
            loadStats();
            loadUserInfo();
            updateDate();
            
            // تحديث الإحصائيات كل 30 ثانية
            setInterval(loadStats, 30000);
        });
    </script>
</body>
</html>
'''

# API Routes
@app.route('/api/login', methods=['POST'])
def api_login():
    """معالجة تسجيل الدخول"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'لم يتم إرسال بيانات'})
            
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'success': False, 'message': 'اسم المستخدم وكلمة المرور مطلوبان'})
        
        password_hash = hashlib.md5(password.encode()).hexdigest()
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'message': 'خطأ في الاتصال بقاعدة البيانات'})
        
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, username, full_name, role, location_id
            FROM users 
            WHERE (username = ? OR email = ?) AND password = ? AND is_active = 1
        ''', (username, username, password_hash))
        
        user = cursor.fetchone()
        conn.close()
        
        if user:
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['full_name'] = user[2]
            session['role'] = user[3]
            session['location_id'] = user[4]
            return jsonify({'success': True, 'redirect': '/dashboard'})
        else:
            return jsonify({'success': False, 'message': 'بيانات الدخول غير صحيحة'})
            
    except Exception as e:
        print(f"Login error: {e}")
        return jsonify({'success': False, 'message': 'حدث خطأ في النظام'})

@app.route('/api/logout', methods=['POST'])
def api_logout():
    """تسجيل الخروج"""
    session.clear()
    return jsonify({'success': True, 'redirect': '/login'})

@app.route('/api/user-info')
def api_user_info():
    """معلومات المستخدم الحالي"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'غير مسجل الدخول'})
    
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'message': 'خطأ في الاتصال بقاعدة البيانات'})
        
        cursor = conn.cursor()
        cursor.execute('''
            SELECT u.full_name, u.role, l.name as location_name
            FROM users u
            LEFT JOIN locations l ON u.location_id = l.id
            WHERE u.id = ?
        ''', (session['user_id'],))
        
        user = cursor.fetchone()
        conn.close()
        
        if user:
            role_translations = {
                'admin': 'مدير النظام',
                'manager': 'مدير الفرع',
                'supervisor': 'المشرف العام',
                'cashier': 'أمين الصندوق',
                'staff': 'موظف',
                'waiter': 'النادل'
            }
            
            return jsonify({
                'success': True,
                'full_name': user[0],
                'role': user[1],
                'role_arabic': role_translations.get(user[1], user[1]),
                'location_name': user[2] or 'غير محدد'
            })
        else:
            return jsonify({'success': False, 'message': 'المستخدم غير موجود'})
            
    except Exception as e:
        print(f"User info error: {e}")
        return jsonify({'success': False, 'message': 'حدث خطأ في النظام'})

@app.route('/api/dashboard-stats')
def api_dashboard_stats():
    """إحصائيات لوحة التحكم"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({
                'todays_orders': 0,
                'todays_revenue': 0.0,
                'total_customers': 0,
                'menu_items': 0
            })
        
        cursor = conn.cursor()
        
        # عدد الطلبات اليوم
        cursor.execute('''
            SELECT COUNT(*) FROM sales 
            WHERE DATE(sale_date) = DATE('now')
        ''')
        todays_orders = cursor.fetchone()[0]
        
        # إيرادات اليوم
        cursor.execute('''
            SELECT COALESCE(SUM(total_amount), 0) FROM sales 
            WHERE DATE(sale_date) = DATE('now')
        ''')
        todays_revenue = cursor.fetchone()[0]
        
        # إجمالي العملاء
        cursor.execute('''
            SELECT COUNT(*) FROM customers WHERE is_active = 1
        ''')
        total_customers = cursor.fetchone()[0]
        
        # عدد الأصناف
        cursor.execute('''
            SELECT COUNT(*) FROM items WHERE is_active = 1
        ''')
        menu_items = cursor.fetchone()[0]
        
        conn.close()
        
        return jsonify({
            'todays_orders': todays_orders,
            'todays_revenue': float(todays_revenue),
            'total_customers': total_customers,
            'menu_items': menu_items
        })
        
    except Exception as e:
        print(f"Dashboard stats error: {e}")
        return jsonify({
            'todays_orders': 0,
            'todays_revenue': 0.0,
            'total_customers': 0,
            'menu_items': 0
        })

if __name__ == '__main__':
    # تهيئة قاعدة البيانات
    if init_db():
        print("Database initialized successfully")
    else:
        print("Database initialization failed")
    
    # تشغيل التطبيق
    app.run(host='0.0.0.0', port=5000, debug=False)
