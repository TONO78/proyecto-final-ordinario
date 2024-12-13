from flask import Flask, render_template, request, redirect, url_for
import mysql.connector

app = Flask(__name__)

class Database:
    def __init__(self):
        self.conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='modelorama'
        )
        self.cursor = self.conn.cursor(dictionary=True)

    def close(self):
        self.cursor.close()
        self.conn.close()

class Producto(Database):
    def get_all(self):
        self.cursor.execute('SELECT * FROM productos')
        return self.cursor.fetchall()

    def get_by_id(self, id):
        self.cursor.execute('SELECT * FROM productos WHERE id = %s', (id,))
        return self.cursor.fetchone()

    def add(self, nombre, descripcion, precio, cantidad, punto_reorden, proveedor_id):
        self.cursor.execute('''INSERT INTO productos (nombre, descripcion, precio, cantidad, punto_reorden, proveedor_id) 
                               VALUES (%s, %s, %s, %s, %s, %s)''', 
                            (nombre, descripcion, precio, cantidad, punto_reorden, proveedor_id))
        self.conn.commit()

    def update(self, id, nombre, descripcion, precio, cantidad, punto_reorden, proveedor_id):
        self.cursor.execute('''UPDATE productos 
                               SET nombre = %s, descripcion = %s, precio = %s, cantidad = %s, 
                                   punto_reorden = %s, proveedor_id = %s 
                               WHERE id = %s''', 
                            (nombre, descripcion, precio, cantidad, punto_reorden, proveedor_id, id))
        self.conn.commit()

    def delete(self, id):
        self.cursor.execute('DELETE FROM productos WHERE id = %s', (id,))
        self.conn.commit()

class Proveedor(Database):
    def get_all(self):
        self.cursor.execute('SELECT * FROM proveedores')
        return self.cursor.fetchall()

    def get_by_id(self, id):
        self.cursor.execute('SELECT * FROM proveedores WHERE id = %s', (id,))
        return self.cursor.fetchone()

    def add(self, nombre, direccion, telefono, email):
        self.cursor.execute('INSERT INTO proveedores (nombre, direccion, telefono, email) VALUES (%s, %s, %s, %s)', 
                            (nombre, direccion, telefono, email))
        self.conn.commit()

    def update(self, id, nombre, direccion, telefono, email):
        self.cursor.execute('UPDATE proveedores SET nombre = %s, direccion = %s, telefono = %s, email = %s WHERE id = %s',
                            (nombre, direccion, telefono, email, id))
        self.conn.commit()

    def delete(self, id):
        self.cursor.execute('DELETE FROM proveedores WHERE id = %s', (id,))
        self.conn.commit()

class Venta(Database):
    def get_all(self):
        self.cursor.execute('''SELECT v.id, p.nombre AS producto, v.cantidad, v.precio_total, v.fecha, pr.nombre AS proveedor
                               FROM ventas v
                               JOIN productos p ON v.producto_id = p.id
                               JOIN proveedores pr ON v.proveedor_id = pr.id
                               ORDER BY v.fecha DESC''')
        return self.cursor.fetchall()

    def add(self, producto_id, cantidad, precio_total, proveedor_id):
        self.cursor.execute('INSERT INTO ventas (producto_id, cantidad, precio_total, proveedor_id) VALUES (%s, %s, %s, %s)', 
                            (producto_id, cantidad, precio_total, proveedor_id))
        self.conn.commit()

@app.route('/')
def index():
    db = Producto()
    productos = db.get_all()
    db.close()
    return render_template('index.html', productos=productos)

@app.route('/agregar', methods=['GET', 'POST'])
def agregar_producto():
    db_proveedor = Proveedor()
    proveedores = db_proveedor.get_all()
    db_proveedor.close()

    if request.method == 'POST':
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        precio = request.form['precio']
        cantidad = request.form['cantidad']
        punto_reorden = request.form['punto_reorden']
        proveedor_id = request.form['proveedor_id']
        
        try:
            db = Producto()
            db.add(nombre, descripcion, precio, cantidad, punto_reorden, proveedor_id)
            db.close()
            return redirect(url_for('index'))
        except Exception as e:
            print(f"Error al agregar producto: {e}")
            return render_template('agregar_producto.html', error="Hubo un problema al agregar el producto. Inténtalo de nuevo.", proveedores=proveedores)
    
    return render_template('agregar_producto.html', proveedores=proveedores)

@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar_producto(id):
    db = Producto()
    producto = db.get_by_id(id)
    db_proveedor = Proveedor()
    proveedores = db_proveedor.get_all()
    db_proveedor.close()

    if request.method == 'POST':
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        precio = request.form['precio']
        cantidad = request.form['cantidad']
        punto_reorden = request.form['punto_reorden']
        proveedor_id = request.form['proveedor_id']

        try:
            db.update(id, nombre, descripcion, precio, cantidad, punto_reorden, proveedor_id)
            db.close()
            return redirect(url_for('index'))
        except Exception as e:
            print(f"Error al editar producto: {e}")
            return render_template('editar_producto.html', producto=producto, proveedores=proveedores, error="Hubo un problema al editar el producto. Inténtalo de nuevo.")

    db.close()
    return render_template('editar_producto.html', producto=producto, proveedores=proveedores)

@app.route('/eliminar/<int:id>')
def eliminar_producto(id):
    db = Producto()
    db.delete(id)
    db.close()
    return redirect(url_for('index'))

@app.route('/venta/<int:id>', methods=['GET', 'POST'])
def venta(id):
    db = Producto()
    producto = db.get_by_id(id)
    total_venta = 0

    if request.method == 'POST':
        cantidad = request.form['cantidad']
        
        if int(producto['cantidad']) >= int(cantidad):
            nueva_cantidad = int(producto['cantidad']) - int(cantidad)
            total_venta = float(producto['precio']) * int(cantidad)
            
            try:
                db_venta = Venta()
                db_venta.add(id, cantidad, total_venta, producto['proveedor_id'])
                db_venta.close()
                db.update(id, producto['nombre'], producto['descripcion'], producto['precio'], nueva_cantidad, producto['punto_reorden'], producto['proveedor_id'])
                db.close()
                return render_template('venta.html', producto=producto, total_venta=total_venta)
            except Exception as e:
                print(f"Error al realizar la venta: {e}")
                return render_template('venta.html', producto=producto, total_venta=0, error="Hubo un problema al realizar la venta. Inténtalo de nuevo.")
        else:
            db.close()
            return render_template('venta.html', producto=producto, total_venta=0, error="No hay suficiente stock disponible.")
    
    db.close()
    return render_template('venta.html', producto=producto, total_venta=total_venta)

@app.route('/reporte_ventas')
def reporte_ventas():
    db = Venta()
    ventas = db.get_all()
    db.close()
    return render_template('reporte_ventas.html', ventas=ventas)

@app.route('/proveedores')
def proveedores():
    db = Proveedor()
    proveedores = db.get_all()
    db.close()
    return render_template('proveedores.html', proveedores=proveedores)

@app.route('/agregar_proveedor', methods=['GET', 'POST'])
def agregar_proveedor():
    if request.method == 'POST':
        nombre = request.form['nombre']
        direccion = request.form['direccion']
        telefono = request.form['telefono']
        email = request.form['email']
        
        try:
            db = Proveedor()
            db.add(nombre, direccion, telefono, email)
            db.close()
            return redirect(url_for('proveedores'))
        except Exception as e:
            print(f"Error al agregar proveedor: {e}")
            return render_template('agregar_proveedor.html', error="Hubo un problema al agregar el proveedor.")
    return render_template('agregar_proveedor.html')

@app.route('/editar_proveedor/<int:id>', methods=['GET', 'POST'])
def editar_proveedor(id):
    db = Proveedor()
    proveedor = db.get_by_id(id)

    if request.method == 'POST':
        nombre = request.form['nombre']
        direccion = request.form['direccion']
        telefono = request.form['telefono']
        email = request.form['email']
        
        db.update(id, nombre, direccion, telefono, email)
        db.close()
        return redirect(url_for('proveedores'))
    
    db.close()
    return render_template('editar_proveedor.html', proveedor=proveedor)

@app.route('/eliminar_proveedor/<int:id>')
def eliminar_proveedor(id):
    db = Proveedor()
    db.delete(id)
    db.close()
    return redirect(url_for('proveedores'))

if __name__ == '__main__':
    app.run(debug=True)
