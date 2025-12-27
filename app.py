from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask import Blueprint
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
import os
import time
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from mysql import connector
from mysql.connector import Error
from datetime import datetime
import logging
import random
import string

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'AbCdEfGhIjKlMnOpQrStUvWxYz')
# --- KONFIGURASI MAIL (Gunakan Email Google/SMTP Anda) ---
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
# Ganti dengan email pengirim dan App Password (bukan password login biasa)
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', 'valekaleb46@gmail.com')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = 'valekaleb46@gmail.com'

mail = Mail(app)
s = URLSafeTimedSerializer(app.secret_key) # Untuk generate token aman

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['UPLOAD_FOLDER'] = os.path.join(basedir, 'static/img')
app.config['PROFILE_UPLOAD_FOLDER'] = os.path.join(basedir, 'static/img/profiles')

# db = connector.connect(
#     host = "wd5r3.h.filess.io",
#     database = "warungronde_frightenin",
#     port = "3307",
#     user = "warungronde_frightenin",
#     password = "66468c43cf1724d44a5148f1c0c89ecf02afed0e"
# )

# db = connector.connect(
#     host = "localhost",
#     database = "warung_ronde",
#     user = "root",
#     password = ""
# )

def get_db_connection():
    connection = connector.connect(
        user="webronde", 
        password="46Ronde46", 
        host="webronde.mysql.database.azure.com", 
        port=3306, 
        database="warung_ronde"
    )
    return connection

def allowed_file(filename):
    allowed_extensions = {'jpg', 'jpeg', 'png', 'webp', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def validate_file(file):
    if file is None:
        return False, 'No file part'
    if file.filename == '':
        return False, 'No selected file'
    if file and allowed_file(file.filename):
        if file.content_length > 1024 * 1024:  # 1MB
            return False, "File size exceeds 1MB limit."
        return True, 'File uploaded successfully'
    return False, 'Invalid file format'

def generate_random_string(length=10):
    """Generate a random string of fixed length."""
    letters = string.ascii_letters + string.digits  # Kombinasi huruf dan angka
    random_string = ''.join(random.choice(letters) for i in range(length))
    return random_string

@app.route('/', methods=['GET'])
def home():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM tbproduk")
    res = cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()
    return render_template('index.html', hasil=res)

@app.route('/about/')
def about():
    return render_template('about.html')

@app.route('/detail/<int:id>', methods=['GET'])
def detail(id):
    conn = get_db_connection()
    cur = conn.cursor()
    # Fetch the selected product details
    cur.execute("SELECT id, nama, harga, detail, foto, stok FROM tbproduk WHERE id = %s", (id,))
    product = cur.fetchone()
    # Fetch related products (excluding the selected product)
    cur.execute("SELECT id, nama, harga, foto, stok FROM tbproduk WHERE id != %s ORDER BY RAND() LIMIT 4", (id,))
    related_products = cur.fetchall()

    conn.commit()
    cur.close()
    conn.close()
    return render_template('item.html', product=product, related_products=related_products)

user_bp = Blueprint('user', __name__, template_folder='user')
admin_bp = Blueprint('admin', __name__, template_folder='admin')

@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor = db.cursor()
        cursor.execute("SELECT id_user, username, password, role FROM tbuser WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()

        if user and check_password_hash(user[2], password):  # Check hashed password
            session['username'] = username
            session['role'] = user[3]
            session['id_user'] = user[0]
            if user[3] == 'admin':
                return redirect(url_for('admin.admin_dashboard'))
            else:
                return redirect(url_for('user.user_dashboard')) 
        else:
            flash('Invalid username or password.', 'error')

    return render_template('login.html')

@app.route('/signup/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password)
        email = request.form['email']
        noHP = request.form['nomorHP']
        role = 'user'

        cursor = db.cursor()
        try:
            # --- 1. CEK EMAIL DUPLIKAT ---
            cursor.execute("SELECT id_user FROM tbuser WHERE email = %s", (email,))
            if cursor.fetchone():
                flash('Email sudah terdaftar. Gunakan email lain.', 'error')
                return render_template('signup.html')

            # --- 2. CEK USERNAME DUPLIKAT (BARU) ---
            cursor.execute("SELECT id_user FROM tbuser WHERE username = %s", (username,))
            if cursor.fetchone():
                flash('Username sudah digunakan orang lain. Silakan pilih username baru.', 'error')
                return render_template('signup.html')
            
            # --- 3. PROSES SIMPAN DATA (Jika lolos semua cek) ---
            cursor.execute("INSERT INTO tbuser (username, password, email, nomorHP, role) VALUES (%s, %s, %s, %s, %s)", 
                        (username, hashed_password, email, noHP, role))
            db.commit()
            flash('Registration successful! Silakan Login.', 'success')
            return redirect(url_for('login'))
            
        except Exception as e:
            db.rollback() 
            flash(f'Terjadi kesalahan: {str(e)}', 'error')
            return render_template('signup.html')
        finally:
            cursor.close()
            
    return render_template('signup.html')

@app.route('/user_about')
def user_about():
    conn = get_db_connection()
    cur = conn.cursor()  # Corrected line
    user_id = session.get('id_user')
    cur.execute("SELECT * FROM tbuser WHERE id_user = %s", (user_id,))
    user = cur.fetchone()  # Fetch user data
    conn.commit()
    cur.close()
    conn.close()
    
    if 'username' in session and session['role'] == 'user':
        return render_template('user/about.html', user=user)
    else:
        flash('You do not have permission to access this page.', 'error')
        return redirect(url_for('login'))

@user_bp.route('/user_dashboard')
def user_dashboard():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM tbproduk")
    res = cur.fetchall()

    # Fetch user data from session
    user_id = session.get('id_user')
    cur.execute("SELECT * FROM tbuser WHERE id_user = %s", (user_id,))
    user = cur.fetchone()  # Fetch user data

    conn.commit()
    cur.close()
    conn.close()
    if 'username' in session and session['role'] == 'user':
        return render_template('user/index.html', hasil=res, user=user)
    else:
        return redirect(url_for('login'))

@app.route('/user_detail/<int:id>', methods=['GET'])
def user_detail(id):
    conn = get_db_connection()
    cur = conn.cursor()
    # Fetch the selected product details
    cur.execute("SELECT id, nama, harga, detail, foto, stok FROM tbproduk WHERE id = %s", (id,))
    product = cur.fetchone()
    
    # Fetch related products
    cur.execute("SELECT id, nama, harga, foto, stok FROM tbproduk WHERE id != %s ORDER BY RAND() LIMIT 4", (id,))
    related_products = cur.fetchall()

    # --- TAMBAHAN: Fetch Reviews ---
    # Mengambil review, username user, dan tanggal
    cur.execute("""
        SELECT r.rating, r.komentar, r.tanggal, u.username, r.balasan, r.tanggal_balasan, r.id_review, r.id_user 
        FROM tbreview r 
        JOIN tbuser u ON r.id_user = u.id_user 
        WHERE r.id_produk = %s 
        ORDER BY r.tanggal DESC
    """, (id,))
    reviews = cur.fetchall()

    # Menghitung Rata-rata Rating (Opsional)
    cur.execute("SELECT AVG(rating) FROM tbreview WHERE id_produk = %s", (id,))
    avg_rating = cur.fetchone()[0]
    avg_rating = round(avg_rating, 1) if avg_rating else 0
    # -------------------------------

    user_id = session.get('id_user')
    cur.execute("SELECT * FROM tbuser WHERE id_user = %s", (user_id,))
    user = cur.fetchone()

    conn.commit()
    cur.close()
    conn.close()
    if 'username' in session and session['role'] == 'user':
        # Jangan lupa passing 'reviews' dan 'avg_rating' ke render_template
        return render_template('user/item.html', hasil=product, hasilrelate=related_products, user=user, reviews=reviews, avg_rating=avg_rating)
    else:
        flash('You do not have permission to access this page.', 'error')
        return redirect(url_for('login'))

@app.route('/user_edit_user/<int:id_user>', methods=['GET', 'POST'])
def user_edit_user(id_user):
    # Security Check
    if 'id_user' not in session or session['id_user'] != id_user:
        flash('Anda tidak memiliki akses.', 'error')
        return redirect(url_for('user.user_dashboard'))

    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        nomorHP = request.form['nomorHP']
        
        # --- LOGIKA UPLOAD FOTO PROFIL (BARU) ---
        foto_profil = request.files.get('foto_profil')
        filename_foto = None
        
        # Cek apakah user mengupload foto baru
        if foto_profil and foto_profil.filename != '':
            is_valid, msg = validate_file(foto_profil)
            if is_valid:
                # 1. Hapus foto lama jika ada (Optional, untuk menghemat storage)
                cur.execute("SELECT foto_profil FROM tbuser WHERE id_user = %s", (id_user,))
                old_foto = cur.fetchone()[0]
                if old_foto:
                    old_path = os.path.join(app.config['PROFILE_UPLOAD_FOLDER'], old_foto)
                    if os.path.exists(old_path):
                        os.remove(old_path)

                # 2. Simpan foto baru
                filename_foto = generate_random_string() + '.' + foto_profil.filename.rsplit('.', 1)[1].lower()
                save_path = os.path.join(app.config['PROFILE_UPLOAD_FOLDER'], filename_foto)
                foto_profil.save(save_path)
            else:
                flash(msg, 'error')
                return redirect(url_for('user_edit_user', id_user=id_user))
        # ----------------------------------------

        # Ambil data password
        current_password = request.form.get('current_password')
        new_password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        cur.execute("SELECT password FROM tbuser WHERE id_user = %s", (id_user,))
        stored_password_hash = cur.fetchone()[0]

        try:
            # Query Update Dasar
            sql_update = "UPDATE tbuser SET username = %s, email = %s, nomorHP = %s"
            val_update = [username, email, nomorHP]

            # Jika ada foto baru, tambahkan ke query
            if filename_foto:
                sql_update += ", foto_profil = %s"
                val_update.append(filename_foto)

            # Logika Ganti Password
            if new_password:
                if not current_password or not check_password_hash(stored_password_hash, current_password):
                    flash('Password saat ini salah.', 'error')
                    return redirect(url_for('user_edit_user', id_user=id_user))
                if new_password != confirm_password:
                    flash('Konfirmasi password baru tidak cocok.', 'error')
                    return redirect(url_for('user_edit_user', id_user=id_user))
                
                sql_update += ", password = %s"
                val_update.append(generate_password_hash(new_password))

            # Finalisasi Query
            sql_update += " WHERE id_user = %s"
            val_update.append(id_user)

            cur.execute(sql_update, tuple(val_update))
            db.commit()
            flash('Profil berhasil diperbarui!', 'success')

        except Exception as e:
            db.rollback()
            flash(f'Terjadi kesalahan: {str(e)}', 'error')
        finally:
            conn.commit()
            cur.close()
            conn.close()
        
        return redirect(url_for('profil')) 

    # Method GET
    cur.execute("SELECT * FROM tbuser WHERE id_user = %s", (id_user,))
    user = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()

    if 'username' in session and session['role'] == 'user':
        return render_template('user/user_edit.html', user=user)
    else:
        return redirect(url_for('login'))

@app.route('/add_to_cart/<int:id>', methods=['POST'])
def add_to_cart(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, nama, harga, foto FROM tbproduk WHERE id = %s", (id,))
    product = cur.fetchone()
    if product:
        jumlah = int(request.form.get('jumlah', 1))  # Get the quantity from the form
        cart.append({
            'id': product[0],
            'nama': product[1],
            'harga': product[2],
            'foto': product[3],
            'jumlah': jumlah  # Use the quantity from the form
        })
        
    return redirect(url_for('user.user_dashboard', hasil=product))

@app.route('/cart', methods=['GET'])
def view_cart():
    conn = get_db_connection()
    cur = conn.cursor()
    user_id = session.get('id_user')
    cur.execute("SELECT * FROM tbuser WHERE id_user = %s", (user_id,))
    user = cur.fetchone()  # user[6] adalah kolom poin (jika urutan kolom sesuai alter table)
    
    # Ambil poin user (asumsi kolom poin ada di index terakhir atau akses by name jika pakai dictionary cursor)
    # Karena fetchone mengembalikan tuple, kita perlu pastikan indexnya benar.
    # Biasanya: id, username, password, email, noHP, role, POIN
    poin_user = user[6] if len(user) > 6 else 0 

    conn.commit()
    cur.close()
    conn.close()
    if 'username' in session and session['role'] == 'user':
        return render_template('user/cart.html', cart=cart, user=user, user_poin=poin_user)
    else:
        flash('You do not have permission to access this page.', 'error')
        return redirect(url_for('login'))
cart = []

@app.route('/status', methods=['GET'])
def status():
    if 'username' in session:
        id_user = session.get('id_user')  # Get user ID from session
        conn = get_db_connection()
        cur = conn.cursor()
        # Fetch orders for the logged-in user
        cur.execute("SELECT id_pesanan, item_pesanan, tanggal_pesanan, modifikasi, total_harga, status, alamat, metode_pembayaran FROM tbpesanan WHERE id_user = %s", (id_user,))
        hasil = cur.fetchall()

        user_id = session.get('id_user')
        cur.execute("SELECT * FROM tbuser WHERE id_user = %s", (user_id,))
        user = cur.fetchone()  # Fetch user data

        conn.commit()
        cur.close()
        conn.close()
        return render_template('user/status.html', hasil=hasil, user=user)
    else:
        return redirect(url_for('login'))  # Redirect to login if not logged in

@app.route('/order_detail/<int:id_pesanan>', methods=['GET'])
def order_detail(id_pesanan):
    if 'username' in session:
        id_user = session.get('id_user')
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Ambil detail pesanan berdasarkan id_pesanan DAN id_user (untuk keamanan)
        cur.execute("SELECT * FROM tbpesanan WHERE id_pesanan = %s AND id_user = %s", (id_pesanan, id_user))
        pesanan = cur.fetchone()
        
        # Ambil data user untuk navbar/header (konsisten dengan route lain)
        cur.execute("SELECT * FROM tbuser WHERE id_user = %s", (id_user,))
        user = cur.fetchone()
        
        conn.commit()
        cur.close()
        conn.close()
        
        if pesanan:
            return render_template('user/order_detail.html', p=pesanan, user=user)
        else:
            flash('Pesanan tidak ditemukan atau Anda tidak memiliki akses.', 'error')
            return redirect(url_for('status'))
    else:
        return redirect(url_for('login'))

@app.route('/remove_order/<int:id_pesanan>', methods=['POST'])
def remove_order(id_pesanan):
    if 'username' in session:
        id_user = session.get('id_user')
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute("DELETE FROM tbpesanan WHERE id_pesanan = %s AND id_user = %s", (id_pesanan, id_user))
            db.commit()
            flash('Pesanan berhasil dihapus.', 'success')
        except Exception as e:
            db.rollback()
            flash('Terjadi kesalahan saat menghapus pesanan.', 'error')
        finally:
            conn.commit()
            cur.close()
            conn.close()
    else:
        flash('Anda harus login untuk menghapus pesanan.', 'error')
    return redirect(url_for('status'))

@app.route('/update_cart', methods=['POST'])
def update_cart():
    global cart
    for item in cart:
        jumlah = request.form.get(f'jumlah_{item["id"]}', 1)
        if jumlah.isdigit() and int(jumlah) > 0:
            item['jumlah'] = int(jumlah)
        else:
            flash('Jumlah harus berupa angka positif.', 'error')
    return redirect(url_for('view_cart'))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@app.route('/update_item_quantity', methods=['POST'])
def update_item_quantity():
    data = request.get_json() # Menerima data JSON dari Javascript
    
    if not data:
        return jsonify({'status': 'error', 'message': 'No data'}), 400

    item_id = int(data.get('id'))
    new_jumlah = int(data.get('jumlah'))
    
    global cart
    # Loop cart untuk update jumlah di sisi server
    for item in cart:
        if item['id'] == item_id:
            item['jumlah'] = new_jumlah
            break
            
    return jsonify({'status': 'success'})

@app.route('/checkout', methods=['POST'])
def checkout():
    global cart
    if not cart:
        flash('Keranjang belanja kosong.', 'error')
        return redirect(url_for('view_cart'))

    alamat = request.form['alamat']
    modifikasi = request.form['modifikasi']
    metode_pembayaran = request.form['metode_pembayaran']
    
    # Cek apakah user ingin menukar poin
    pakai_poin = request.form.get('tukar_poin') # Checkbox dari form HTML
    
    status = 'Menunggu'
    tanggal_pesanan = datetime.now()

    total_harga = 0
    item_list = []
    id_user = session.get('id_user')
    username = session.get('username')

    conn = get_db_connection()
    cur = conn.cursor()
    try:
        # 1. Hitung Total Awal
        for item in cart:
            total_harga += item['harga'] * item['jumlah']
            item_list.append(f"{item['nama']} ({item['jumlah']})")

        # 2. Logika Penukaran Poin (Redeem)
        potongan = 0
        poin_terpakai = 0
        
        # Ambil poin user saat ini dari DB
        cur.execute("SELECT poin FROM tbuser WHERE id_user = %s", (id_user,))
        current_poin = cur.fetchone()[0]

        if pakai_poin and current_poin >= 20:
            # Aturan: Gratis 1 Item (Kita ambil harga item pertama di cart atau yang termurah sebagai gratis)
            # Di sini kita ambil item pertama di keranjang untuk digratiskan (1 qty)
            if len(cart) > 0:
                potongan = cart[0]['harga'] # Gratiskan harga 1 item pertama
                total_harga -= potongan # Kurangi total harga
                poin_terpakai = 20 # Kurangi 20 poin
                item_list.append(f"[BONUS] Gratis {cart[0]['nama']} (Tukar 20 Poin)")
        
        # Pastikan total tidak minus
        if total_harga < 0: total_harga = 0

        # 3. Logika Tambah Poin (Earn)
        # Aturan: Dapat 1 Poin setiap belanja lebih dari Rp 20.000 dari total yang dibayarkan
        if total_harga >= 20000:
            poin_dapat = 1
        else:
            poin_dapat = 0

        # 4. Simpan Pesanan
        cur.execute(""" 
            INSERT INTO tbpesanan (id_user, username, item_pesanan, tanggal_pesanan, modifikasi, total_harga, status, alamat, metode_pembayaran) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (id_user, username, ', '.join(item_list), tanggal_pesanan, modifikasi, total_harga, status, alamat, metode_pembayaran))
        
        # 5. Update Poin User (Kurangi jika dipakai, Tambah dari hasil belanja)
        final_poin = current_poin - poin_terpakai + poin_dapat
        cur.execute("UPDATE tbuser SET poin = %s WHERE id_user = %s", (final_poin, id_user))

        db.commit()
        
        msg = f"Pesanan berhasil! Anda mendapatkan {poin_dapat} poin."
        if poin_terpakai > 0:
            msg += " (20 Poin berhasil ditukarkan)."
        flash(msg, 'success')

    except Exception as e:
        db.rollback()
        flash(f"Error: {str(e)}", 'error')
        return redirect(url_for('view_cart'))
    finally:
        conn.commit()
        cur.close()
        conn.close()

    cart = []  # Kosongkan cart setelah checkout
    return redirect(url_for('status'))

@app.route('/remove_from_cart/<int:id>', methods=['POST'])
def remove_from_cart(id):
    global cart
    cart = [item for item in cart if item['id'] != id]  # Remove item with the given id
    return redirect(url_for('view_cart'))

@app.route('/profil')
def profil():
    if 'username' in session and session['role'] == 'user':
        id_user = session.get('id_user')
        conn = get_db_connection()
        cur = conn.cursor()
        
        # UPDATE QUERY: Tambahkan foto_profil (index ke-6)
        # Urutan: 0=username, 1=email, 2=noHP, 3=role, 4=poin, 5=id_user, 6=foto_profil
        cur.execute("SELECT username, email, nomorHP, role, poin, id_user, foto_profil FROM tbuser WHERE id_user = %s", (id_user,))
        user = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        
        return render_template('user/profil.html', user=user)
    else:
        flash('Silakan login terlebih dahulu.', 'error')
        return redirect(url_for('login'))

@admin_bp.route('/admin_dashboard', methods=['GET'])
def admin_dashboard():
    conn = get_db_connection()
    cur = conn.cursor()
    # Ambil data dari tbdetailpesanan
    cur.execute(""" 
        SELECT id_pesanan, username, item_pesanan, tanggal_pesanan, modifikasi, total_harga, status, alamat, metode_pembayaran 
        FROM tbpesanan
        """)
    res_detail = cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()

    if 'username' in session and session['role'] == 'admin':
        return render_template('admin/index.html', hasil_detail=res_detail)
    else:
        flash('You do not have permission to access this page.', 'error')
        return redirect(url_for('login'))

app.register_blueprint(user_bp)
app.register_blueprint(admin_bp)

@app.route('/update_status/<int:id_pesanan>', methods=['POST'])
def update_status(id_pesanan):
    if 'username' in session and session['role'] == 'admin':
        new_status = request.form['status']
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute("UPDATE tbpesanan SET status = %s WHERE id_pesanan = %s", (new_status, id_pesanan))
            db.commit()
            flash('Status pesanan berhasil diperbarui.', 'success')
        except Exception as e:
            db.rollback()
            flash('Terjadi kesalahan saat memperbarui status pesanan.', 'error')
        finally:
            conn.commit()
            cur.close()
            conn.close()
    else:
        flash('Anda tidak memiliki izin untuk mengubah status.', 'error')
    return redirect(url_for('admin.admin_dashboard'))

@app.route('/admin_remove_order/<int:id_pesanan>', methods=['POST'])
def admin_remove_order(id_pesanan):
    if 'username' in session and session['role'] == 'admin':
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute("DELETE FROM tbpesanan WHERE id_pesanan = %s", (id_pesanan,))
            db.commit()
            flash('Pesanan berhasil dihapus.', 'success')
        except Exception as e:
            db.rollback()
            flash('Terjadi kesalahan saat menghapus pesanan.', 'error')
        finally:
            conn.commit()
            cur.close()
            conn.close()
    else:
        flash('Anda tidak memiliki izin untuk menghapus pesanan.', 'error')
    return redirect(url_for('admin.admin_dashboard'))

@app.route('/admin_detail/', methods=['GET'])
def admin_produk():
    conn = get_db_connection()
    cur = conn.cursor()
    # Fetch all products
    cur.execute("SELECT id, nama, harga, detail, foto, stok FROM tbproduk")
    all_products = cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()

    if 'username' in session and session['role'] == 'admin':
        return render_template('admin/item.html', related_products=all_products)
    else:
        flash('You do not have permission to access this page.', 'error')
        return redirect(url_for('login'))

@app.route('/adminuser_detail', methods=['GET'])
def adminuser_detail():
    conn = get_db_connection()
    cur = conn.cursor()
    # Ambil semua data user dari tbuser
    cur.execute("SELECT id_user, username, password, email, nomorHP, role FROM tbuser")
    users = cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()

    if 'username' in session and session['role'] == 'admin':
        return render_template('admin/user.html', users=users)
    else:
        flash('You do not have permission to access this page.', 'error')
        return redirect(url_for('login'))

@app.route('/admin_remove_user/<int:id_user>', methods=['POST'])
def admin_remove_user(id_user):
    if 'username' in session and session['role'] == 'admin':
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute("DELETE FROM tbuser WHERE id_user = %s", (id_user,))
            db.commit()
            flash('User  berhasil dihapus.', 'success')
        except Exception as e:
            db.rollback()
            flash('Terjadi kesalahan saat menghapus user.', 'error')
        finally:
            conn.commit()
            cur.close()
            conn.close()
    else:
        flash('Anda tidak memiliki izin untuk menghapus user.', 'error')
    return redirect(url_for('adminuser_detail'))

@app.route('/admin_edit_user/<int:id_user>', methods=['GET', 'POST'])
def admin_edit_user(id_user):
    conn = get_db_connection()
    cur = conn.cursor()
    
    if request.method == 'POST':
        # Ambil data dari form
        username = request.form['username']
        email = request.form['email']
        nomorHP = request.form['nomorHP']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        role = request.form['role']
        
        # Validasi password jika diisi
        if password and password != confirm_password:
            flash('Password dan konfirmasi password tidak cocok.', 'error')
            return redirect(url_for('admin_edit_user', id_user=id_user))

        try:
            # Update data user di database
            if password:  # Jika password diisi, hash dan update
                hashed_password = generate_password_hash(password)
                cur.execute(""" 
                    UPDATE tbuser 
                    SET username = %s, email = %s, nomorHP = %s, password = %s, role = %s 
                    WHERE id_user = %s
                """, (username, email, nomorHP, hashed_password, role, id_user))
            else:  # Jika password tidak diisi, update tanpa mengubah password
                cur.execute(""" 
                    UPDATE tbuser 
                    SET username = %s, email = %s, nomorHP = %s, role = %s 
                    WHERE id_user = %s
                """, (username, email, nomorHP, role, id_user))
                
            db.commit()
            flash('User  berhasil diperbarui!', 'success')
        except Exception as e:
            db.rollback()
            flash(f'Terjadi kesalahan saat memperbarui user: {str(e)}', 'error')
        finally:
            conn.commit()
            cur.close()
            conn.close()
        
        return redirect(url_for('adminuser_detail'))  # Redirect ke halaman tabel user setelah edit

    # Jika metode GET, ambil data user untuk ditampilkan di form
    cur.execute("SELECT * FROM tbuser WHERE id_user = %s", (id_user,))
    user = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()

    if 'username' in session and session['role'] == 'admin':
        return render_template('admin/user_edit.html', user=user)
    else:
        flash('Anda tidak memiliki izin untuk mengedit user.', 'error')
        return redirect(url_for('login'))

@app.route('/admin_remove_item/<int:id>', methods=['POST'])
def admin_remove_item(id):
    if 'username' in session and session['role'] == 'admin':
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            # Ambil nama file foto dari database
            cur.execute("SELECT foto FROM tbproduk WHERE id = %s", (id,))
            existing_product = cur.fetchone()
            if existing_product:
                existing_foto = existing_product[0]
                # Hapus file foto dari folder
                foto_path = os.path.join('static/img/Makanan/', existing_foto)
                if os.path.exists(foto_path):
                    os.remove(foto_path)  # Hapus file foto

            # Hapus produk dari database
            cur.execute("DELETE FROM tbproduk WHERE id = %s", (id,))
            db.commit()
            flash('Produk berhasil dihapus.', 'success')
        except Exception as e:
            db.rollback()
            flash('Terjadi kesalahan saat menghapus produk: {}'.format(str(e)), 'error')
        finally:
            conn.commit()
            cur.close()
            conn.close()
    else:
        flash('Anda tidak memiliki izin untuk menghapus produk.', 'error')
    return redirect(url_for('admin_produk'))

@app.route('/admin_add_product', methods=['POST'])
def admin_add_product():
    if 'username' in session and session['role'] == 'admin':
        nama = request.form['nama']
        harga = request.form['harga']
        detail = request.form['detail']
        stok = request.form['stok']
        foto = request.files['foto']  # Mengambil file foto

        # Validasi file
        is_valid, message = validate_file(foto)
        if not is_valid:
            flash(message, 'error')
            return redirect(url_for('admin_add'))  # Kembali ke halaman tambah produk

        # Menghasilkan nama file acak
        random_filename = generate_random_string() + '.' + foto.filename.rsplit('.', 1)[1]  # Menambahkan ekstensi file

        # Simpan foto ke direktori yang sesuai
        foto_path = f'static/img/Makanan/{random_filename}'
        try:
            foto.save(foto_path)  # Simpan file dengan nama acak
        except Exception as e:
            flash(f'Terjadi kesalahan saat menyimpan foto: {str(e)}', 'error')
            return redirect(url_for('admin_add'))

        conn = get_db_connection()
        cur = conn.cursor()
        try:
            # Menyimpan data produk baru ke database
            cur.execute(""" 
                INSERT INTO tbproduk (nama, harga, detail, foto, stok) 
                VALUES (%s, %s, %s, %s, %s)
            """, (nama, harga, detail, random_filename, stok))
            db.commit()
            flash('Produk berhasil ditambahkan!', 'success')
        except Exception as e:
            db.rollback()
            flash(f'Terjadi kesalahan saat menambahkan produk: {str(e)}', 'error')
        finally:
            conn.commit()
            cur.close()
            conn.close()

        return redirect(url_for('admin_produk'))  # Redirect ke halaman produk setelah menambah
    else:
        flash('Anda tidak memiliki izin untuk menambah produk.', 'error')
        return redirect(url_for('login'))

@app.route('/admin_edit/<int:id>', methods=['GET', 'POST'])
def admin_edit(id):
    conn = get_db_connection()
    cur = conn.cursor()
    
    if request.method == 'POST':
        # Ambil data dari form
        nama = request.form['nama']
        harga = request.form['harga']
        detail = request.form['detail']
        stok = request.form['stok']

        try:
            cur.execute(""" 
                UPDATE tbproduk 
                SET nama = %s, harga = %s, detail = %s, stok = %s 
                WHERE id = %s
            """, (nama, harga, detail, stok, id))

            db.commit()
            flash('Produk berhasil diperbarui!', 'success')
        except Exception as e:
            db.rollback()
            flash(f'Terjadi kesalahan saat memperbarui produk: {str(e)}', 'error')
        finally:
            conn.commit()
            cur.close()
            conn.close()

        return redirect(url_for('admin_produk'))  # Redirect ke halaman produk setelah edit

    # Jika metode GET, ambil data produk untuk ditampilkan di form
    cur.execute("SELECT * FROM tbproduk WHERE id = %s", (id,))
    product = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()

    if 'username' in session and session['role'] == 'admin':
        return render_template('admin/item_edit.html', product=product)
    else:
        flash('Anda tidak memiliki izin untuk mengedit produk.', 'error')
        return redirect(url_for('login'))

@app.route('/admin_add', methods=['GET'])
def admin_add():
    if 'username' in session and session['role'] == 'admin':
        return render_template('admin/item_tambah.html')
    else:
        flash('You do not have permission to access this page.', 'error')
        return redirect(url_for('login'))

# --- RUTE BARU: Admin View Detail Produk & Review ---
@app.route('/admin_view/<int:id>', methods=['GET'])
def admin_view(id):
    if 'username' in session and session['role'] == 'admin':
        conn = get_db_connection()
        cur = conn.cursor()
        
        # 1. Ambil detail produk
        cur.execute("SELECT id, nama, harga, detail, foto, stok FROM tbproduk WHERE id = %s", (id,))
        product = cur.fetchone()
        
        # 2. Ambil review beserta username user
        # Kita ambil id_review juga untuk keperluan form balasan
        cur.execute("""
            SELECT r.rating, r.komentar, r.tanggal, u.username, r.balasan, r.tanggal_balasan, r.id_review
            FROM tbreview r 
            JOIN tbuser u ON r.id_user = u.id_user 
            WHERE r.id_produk = %s 
            ORDER BY r.tanggal DESC
        """, (id,))
        reviews = cur.fetchall()

        # 3. Hitung Rata-rata (Opsional, untuk display)
        cur.execute("SELECT AVG(rating) FROM tbreview WHERE id_produk = %s", (id,))
        avg_rating = cur.fetchone()[0]
        avg_rating = round(avg_rating, 1) if avg_rating else 0
        
        conn.commit()
        cur.close()
        conn.close()
        return render_template('admin/item_detail.html', hasil=product, reviews=reviews, avg_rating=avg_rating)
    else:
        flash('Anda tidak memiliki izin.', 'error')
        return redirect(url_for('login'))

# --- RUTE BARU: Proses Balasan Admin ---
@app.route('/admin_reply_review/<int:id_review>/<int:id_produk>', methods=['POST'])
def admin_reply_review(id_review, id_produk):
    if 'username' in session and session['role'] == 'admin':
        balasan = request.form.get('balasan')
        tanggal_balasan = datetime.now()
        
        if not balasan:
            flash('Balasan tidak boleh kosong.', 'error')
            return redirect(url_for('admin_view', id=id_produk))

        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute("""
                UPDATE tbreview 
                SET balasan = %s, tanggal_balasan = %s 
                WHERE id_review = %s
            """, (balasan, tanggal_balasan, id_review))
            db.commit()
            flash('Balasan berhasil dikirim.', 'success')
        except Exception as e:
            db.rollback()
            flash(f'Error: {str(e)}', 'error')
        finally:
            conn.commit()
            cur.close()
            conn.close()
            
        return redirect(url_for('admin_view', id=id_produk))
    else:
        return redirect(url_for('login'))

@app.route('/submit_review/<int:id_produk>', methods=['POST'])
def submit_review(id_produk):
    if 'username' in session and session['role'] == 'user':
        id_user = session.get('id_user')
        rating = request.form.get('rating')
        komentar = request.form.get('komentar')
        tanggal = datetime.now()

        # Validasi sederhana
        if not rating:
            flash('Mohon berikan rating bintang.', 'error')
            return redirect(url_for('user_detail', id=id_produk))

        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute("""
                INSERT INTO tbreview (id_user, id_produk, rating, komentar, tanggal)
                VALUES (%s, %s, %s, %s, %s)
            """, (id_user, id_produk, rating, komentar, tanggal))
            db.commit()
            flash('Terima kasih atas ulasan Anda!', 'success')
        except Exception as e:
            db.rollback()
            flash(f'Terjadi kesalahan: {str(e)}', 'error')
        finally:
            conn.commit()
            cur.close()
            conn.close()
        
        return redirect(url_for('user_detail', id=id_produk))
    else:
        flash('Anda harus login untuk memberikan ulasan.', 'error')
        return redirect(url_for('login'))

@app.route('/delete_review/<int:id_review>/<int:id_produk>', methods=['POST'])
def delete_review(id_review, id_produk):
    if 'username' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cur = conn.cursor()
    try:
        # Cek Role
        if session['role'] == 'admin':
            # Admin bisa hapus review apa saja
            cur.execute("DELETE FROM tbreview WHERE id_review = %s", (id_review,))
        else:
            # User hanya bisa hapus review miliknya sendiri
            id_user_login = session['id_user']
            cur.execute("DELETE FROM tbreview WHERE id_review = %s AND id_user = %s", (id_review, id_user_login))
            
            # Cek apakah ada baris yang terhapus (validasi kepemilikan)
            if cur.rowcount == 0:
                flash('Anda tidak berhak menghapus ulasan ini.', 'error')
                return redirect(url_for('user_detail', id=id_produk))

        db.commit()
        flash('Ulasan berhasil dihapus.', 'success')
    except Exception as e:
        db.rollback()
        flash(f'Gagal menghapus: {str(e)}', 'error')
    finally:
        conn.commit()
        cur.close()
        conn.close()

    # Redirect kembali ke halaman yang sesuai
    if session['role'] == 'admin':
        return redirect(url_for('admin_view', id=id_produk))
    else:
        return redirect(url_for('user_detail', id=id_produk))

@app.route('/logout')
def logout():
    session.clear()
    session.pop('username', None)
    session.pop('role', None)  # Clear the role from the session
    return redirect(url_for('login'))

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM tbuser WHERE email = %s", (email,))
        user = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()

        if user:
            # Generate token yang berlaku selama 1 jam (3600 detik)
            token = s.dumps(email, salt='email-reset')
            
            # Buat link reset
            link = url_for('reset_token', token=token, _external=True)
            
            # --- OPSI 1: Kirim via Email (Aktifkan jika konfigurasi mail sudah benar) ---
            try:
                msg = Message('Reset Password Request', recipients=[email])
                msg.body = 'Klik link berikut untuk mereset password Anda: {}'.format(link)
                mail.send(msg)
                flash('Link reset password telah dikirim ke email Anda.', 'info')
            except Exception as e:
                flash(f'Gagal mengirim email: {str(e)}', 'error')
                # Untuk testing tanpa kirim email, kita print linknya di terminal
                print(f"LINK RESET (TESTING): {link}") 

            # --- OPSI 2 (Hanya untuk Testing Lokal): Print Link di Terminal ---
            # print(f"LINK RESET: {link}")
            # flash('Link reset (Simulasi) telah digenerate. Cek Terminal server.', 'info')
            
            return redirect(url_for('login'))
        else:
            flash('Email tidak terdaftar.', 'error')

    return render_template('forgot_password.html')

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    try:
        # Verifikasi token (maksimal umur token 1 jam)
        email = s.loads(token, salt='email-reset', max_age=3600)
    except SignatureExpired:
        flash('Link reset password telah kadaluarsa.', 'error')
        return redirect(url_for('forgot_password'))
    except Exception:
        flash('Link reset password tidak valid.', 'error')
        return redirect(url_for('forgot_password'))

    if request.method == 'POST':
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash('Password konfirmasi tidak cocok.', 'error')
            return redirect(url_for('reset_token', token=token))

        hashed_password = generate_password_hash(password)

        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute("UPDATE tbuser SET password = %s WHERE email = %s", (hashed_password, email))
            db.commit()
            flash('Password berhasil diubah! Silakan login.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.rollback()
            flash(f'Terjadi kesalahan database: {str(e)}', 'error')
        finally:
            conn.commit()
            cur.close()
            conn.close()

    return render_template('reset_password.html', token=token)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)