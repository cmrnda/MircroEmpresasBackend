from io import BytesIO
from datetime import datetime

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from app.extensions import db
from app.database.models.empresa import Empresa
from app.database.models.empresa_settings import EmpresaSettings
from app.database.models.venta import Venta, VentaDetalle
from app.database.models.producto import Producto
from app.database.models.cliente import Cliente


def build_sale_receipt_pdf(empresa_id: int, venta_id: int) -> bytes:
    empresa_id = int(empresa_id)
    venta_id = int(venta_id)

    venta = (
        db.session.query(Venta)
        .filter(Venta.empresa_id == empresa_id)
        .filter(Venta.venta_id == venta_id)
        .first()
    )
    if not venta:
        raise ValueError("not_found")

    empresa = db.session.query(Empresa).filter(Empresa.empresa_id == empresa_id).first()
    settings = db.session.query(EmpresaSettings).filter(EmpresaSettings.empresa_id == empresa_id).first()

    cliente = None
    if getattr(venta, "cliente_id", None):
        cliente = (
            db.session.query(Cliente)
            .filter(Cliente.empresa_id == empresa_id)
            .filter(Cliente.cliente_id == int(venta.cliente_id))
            .first()
        )

    # detalles + producto (para descripcion/codigo)
    detalles = (
        db.session.query(VentaDetalle, Producto)
        .join(
            Producto,
            (Producto.empresa_id == VentaDetalle.empresa_id)
            & (Producto.producto_id == VentaDetalle.producto_id),
        )
        .filter(VentaDetalle.empresa_id == empresa_id)
        .filter(VentaDetalle.venta_id == venta_id)
        .order_by(VentaDetalle.venta_detalle_id.asc())
        .all()
    )

    buff = BytesIO()
    c = canvas.Canvas(buff, pagesize=letter)
    w, h = letter

    y = h - 40

    # --- Header (Empresa)
    nombre_empresa = getattr(empresa, "nombre", None) or "Empresa"
    nit_empresa = getattr(settings, "nit", None) or getattr(empresa, "nit", None) or "S/N"
    direccion = getattr(settings, "direccion", None) or getattr(empresa, "direccion", None) or "S/N"
    telefono = getattr(settings, "telefono", None) or getattr(empresa, "telefono", None) or "S/N"

    c.setFont("Helvetica-Bold", 14)
    c.drawString(40, y, str(nombre_empresa)[:60]); y -= 16

    c.setFont("Helvetica", 10)
    c.drawString(40, y, f"NIT: {nit_empresa}"); y -= 12
    c.drawString(40, y, f"Dirección: {direccion}"); y -= 12
    c.drawString(40, y, f"Teléfono: {telefono}"); y -= 18

    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, y, "RECIBO / COMPROBANTE DE VENTA"); y -= 16

    fecha = getattr(venta, "creado_en", None) or datetime.utcnow()
    c.setFont("Helvetica", 10)
    c.drawString(40, y, f"Nro. Venta: {venta_id}"); y -= 12
    c.drawString(40, y, f"Fecha/Hora: {fecha.strftime('%Y-%m-%d %H:%M:%S')}"); y -= 12

    # Usuario/cajero si lo tienes en venta (ajusta campos)
    cajero = getattr(venta, "usuario_nombre", None) or getattr(venta, "usuario_id", None) or "S/N"
    c.drawString(40, y, f"Cajero: {cajero}"); y -= 16

    # --- Cliente
    c.setFont("Helvetica-Bold", 10)
    c.drawString(40, y, "Cliente:"); y -= 12
    c.setFont("Helvetica", 10)
    if cliente:
        c.drawString(40, y, f"Nombre: {getattr(cliente, 'nombre', '')}"); y -= 12
        c.drawString(40, y, f"NIT/CI: {getattr(cliente, 'nit', None) or getattr(cliente, 'ci', None) or 'S/N'}"); y -= 12
    else:
        c.drawString(40, y, "Nombre: S/N"); y -= 12
        c.drawString(40, y, "NIT/CI: S/N"); y -= 12
    y -= 10

    # --- Tabla items
    c.setFont("Helvetica-Bold", 10)
    c.drawString(40, y, "Cant"); c.drawString(90, y, "Producto"); c.drawRightString(470, y, "P.Unit"); c.drawRightString(560, y, "Subtotal")
    y -= 10
    c.line(40, y, 570, y)
    y -= 14

    c.setFont("Helvetica", 10)
    total = 0.0

    for det, prod in detalles:
        qty = float(getattr(det, "qty", None) or getattr(det, "cantidad", None) or 0)
        pu = float(getattr(det, "precio_unit", None) or getattr(det, "precio", None) or 0)
        sub = float(getattr(det, "subtotal", None) or (qty * pu))

        desc = getattr(prod, "descripcion", None) or "Producto"
        codigo = getattr(prod, "codigo", None) or ""
        linea = f"{desc} {('- ' + codigo) if codigo else ''}".strip()

        if y < 80:
            c.showPage()
            y = h - 40
            c.setFont("Helvetica", 10)

        c.drawString(40, y, f"{qty:g}")
        c.drawString(90, y, linea[:55])
        c.drawRightString(470, y, f"{pu:.2f}")
        c.drawRightString(560, y, f"{sub:.2f}")
        y -= 14
        total += sub

    y -= 6
    c.line(340, y, 570, y)
    y -= 16

    c.setFont("Helvetica-Bold", 11)
    c.drawRightString(470, y, "TOTAL:")
    c.drawRightString(560, y, f"{total:.2f}")
    y -= 16

    # Pago
    c.setFont("Helvetica", 10)
    metodo = getattr(venta, "metodo_pago", None) or getattr(venta, "forma_pago", None) or "EFECTIVO"
    recibido = float(getattr(venta, "monto_recibido", None) or getattr(venta, "efectivo", None) or 0)
    cambio = float(getattr(venta, "cambio", None) or 0)

    c.drawString(40, y, f"Método de pago: {metodo}"); y -= 12
    c.drawString(40, y, f"Monto recibido: {recibido:.2f}"); y -= 12
    c.drawString(40, y, f"Cambio: {cambio:.2f}"); y -= 18

    # Footer
    c.setFont("Helvetica-Oblique", 9)
    c.drawString(40, y, "Gracias por su compra. Este documento es un comprobante interno."); y -= 12

    c.showPage()
    c.save()

    return buff.getvalue()
