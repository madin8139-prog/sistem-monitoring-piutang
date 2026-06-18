from flask import Flask, render_template, request, redirect
import mysql.connector

app = Flask(__name__)

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="db_piutang"
)

# ==========================
# HOME
# ==========================

@app.route('/')
def awal():
    return redirect('/home')

@app.route('/home')
def home():
    return render_template('home.html')


# ==========================
# VIS
# ==========================

@app.route('/vis')
def vis():
    return redirect('/dashboard?cabang=VIS')


# ==========================
# SALLO
# ==========================

@app.route('/sallo')
def sallo():
    return redirect('/dashboard?cabang=SALLO')


# ==========================
# DASHBOARD
# ==========================

@app.route('/dashboard')
def index():

    keyword = request.args.get('keyword', '')
    cabang = request.args.get('cabang', 'VIS')

    cursor = db.cursor(dictionary=True)

    # DATA TABEL

    if keyword:

        cursor.execute("""
            SELECT *
            FROM piutang
            WHERE cabang=%s
            AND (
                no_nota LIKE %s
                OR nama LIKE %s
            )
            ORDER BY tanggal DESC
        """,
        (
            cabang,
            f"%{keyword}%",
            f"%{keyword}%"
        ))

    else:

        cursor.execute("""
            SELECT *
            FROM piutang
            WHERE cabang=%s
            ORDER BY tanggal DESC
        """,
        (cabang,))

    data = cursor.fetchall()

    # DASHBOARD

    cursor.execute("""
        SELECT COUNT(*) total_data
        FROM piutang
        WHERE cabang=%s
    """,
    (cabang,))
    total_data = cursor.fetchone()["total_data"]

    cursor.execute("""
        SELECT COUNT(*) belum_bayar
        FROM piutang
        WHERE cabang=%s
        AND status='Belum Bayar'
    """,
    (cabang,))
    belum_bayar = cursor.fetchone()["belum_bayar"]

    cursor.execute("""
        SELECT COUNT(*) lunas
        FROM piutang
        WHERE cabang=%s
        AND status='Lunas'
    """,
    (cabang,))
    lunas = cursor.fetchone()["lunas"]

    cursor.execute("""
        SELECT IFNULL(SUM(nominal),0) total_nominal
        FROM piutang
        WHERE cabang=%s
        AND status='Belum Bayar'
    """,
    (cabang,))
    total_nominal = cursor.fetchone()["total_nominal"]

    return render_template(
        'index.html',
        data=data,
        keyword=keyword,
        total_data=total_data,
        belum_bayar=belum_bayar,
        lunas=lunas,
        total_nominal=total_nominal,
        cabang=cabang
    )


# ==========================
# TAMBAH PIUTANG
# ==========================

@app.route('/tambah', methods=['GET', 'POST'])
def tambah():

    if request.method == 'POST':

        cabang = request.form['cabang']
        no_nota = request.form['no_nota']
        tanggal = request.form['tanggal']
        jenis = request.form['jenis']
        nama = request.form['nama']
        nominal = request.form['nominal']

        cursor = db.cursor()

        cursor.execute("""
            INSERT INTO piutang
            (
                cabang,
                no_nota,
                tanggal,
                jenis,
                nama,
                nominal,
                status
            )
            VALUES
            (
                %s,%s,%s,%s,%s,%s,
                'Belum Bayar'
            )
        """,
        (
            cabang,
            no_nota,
            tanggal,
            jenis,
            nama,
            nominal
        ))

        db.commit()

        return redirect('/dashboard?cabang=' + cabang)

    cabang = request.args.get('cabang')

    return render_template(
        'tambah.html',
        cabang=cabang
    )





@app.route('/bayar/<no_nota>', methods=['GET', 'POST'])
def bayar(no_nota):

    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM piutang
        WHERE no_nota=%s
    """, (no_nota,))

    data = cursor.fetchone()

    if request.method == 'POST':

        tanggal_bayar = request.form['tanggal_bayar']
        nominal_bayar = request.form['nominal_bayar']
        metode_bayar = request.form['metode_bayar']

        cursor2 = db.cursor()

        cursor2.execute("""
            UPDATE piutang
            SET
                status='Lunas',
                tanggal_bayar=%s,
                nominal_bayar=%s,
                metode_bayar=%s
            WHERE no_nota=%s
        """,
        (
            tanggal_bayar,
            nominal_bayar,
            metode_bayar,
            no_nota
        ))

        db.commit()

        return redirect('/dashboard?cabang=' + data['cabang'])

    return render_template(
        'bayar.html',
        data=data
    )



if __name__ == '__main__':
    app.run(debug=True)