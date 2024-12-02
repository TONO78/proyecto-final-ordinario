from flask import Flask, render_template, request, redirect, url_for
import mysql.connector

app = Flask(__name__)

# Configuración de la conexión a la base de datos MySQL
def get_db_connection():
    conn = mysql.connector.connect(
        host='localhost',      # XAMPP MySQL server
        user='root',           # Usuario por defecto de MySQL
        password='',           # Contraseña por defecto de MySQL
        database='modelorama'  # Nombre de la base de datos
    )
    return conn

# Ruta principal - Mostrar productos
@app.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM productos')
    productos = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('index.html', productos=productos)

# Ruta para agregar un nuevo producto
@app.route('/agregar', methods=['GET', 'POST'])
def agregar_producto():
    if request.method == 'POST':
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        precio = request.form['precio']
        cantidad = request.form['cantidad']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO productos (nombre, descripcion, precio, cantidad) VALUES (%s, %s, %s, %s)', 
                       (nombre, descripcion, precio, cantidad))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('index'))
    return render_template('agregar_producto.html')

# Ruta para editar un producto
@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar_producto(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM productos WHERE id = %s', (id,))
    producto = cursor.fetchone()
    
    if request.method == 'POST':
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        precio = request.form['precio']
        cantidad = request.form['cantidad']
        
        cursor.execute('UPDATE productos SET nombre = %s, descripcion = %s, precio = %s, cantidad = %s WHERE id = %s',
                       (nombre, descripcion, precio, cantidad, id))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('index'))
    
    cursor.close()
    conn.close()
    return render_template('editar_producto.html', producto=producto)

# Ruta para eliminar un producto
@app.route('/eliminar/<int:id>')
def eliminar_producto(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Eliminamos el producto de la base de datos
    cursor.execute('DELETE FROM productos WHERE id = %s', (id,))
    conn.commit()
    cursor.close()
    conn.close()
    
    # Redirigimos a la página principal con los productos
    return redirect(url_for('index'))

# Ruta para ver el carrito de compras
@app.route('/carrito')
def carrito():
    return render_template('carrito.html')

# Ruta para ver la página de venta (GET) y realizar la venta (POST)
@app.route('/venta/<int:id>', methods=['GET', 'POST'])
def venta(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM productos WHERE id = %s', (id,))
    producto = cursor.fetchone()
    
    total_venta = 0  # Inicializamos el total_venta en 0

    if request.method == 'POST':
        cantidad = request.form['cantidad']
        
        # Verificar si la cantidad solicitada está disponible
        if int(producto['cantidad']) >= int(cantidad):
            nueva_cantidad = int(producto['cantidad']) - int(cantidad)
            
            # Calcular el total de la venta
            total_venta = float(producto['precio']) * int(cantidad)
            
            # Actualizar la cantidad del producto
            cursor.execute('UPDATE productos SET cantidad = %s WHERE id = %s', (nueva_cantidad, id))
            conn.commit()
            cursor.close()
            conn.close()
            return render_template('venta.html', producto=producto, total_venta=total_venta)
        else:
            cursor.close()
            conn.close()
            return render_template('venta.html', producto=producto, total_venta=0, error="No hay suficiente stock disponible.")
    
    cursor.close()
    conn.close()
    return render_template('venta.html', producto=producto, total_venta=total_venta)

if __name__ == '__main__':
    app.run(debug=True)
