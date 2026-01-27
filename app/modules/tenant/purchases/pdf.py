from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas


def build_purchase_pdf(purchase: dict) -> bytes:
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)

    w, h = letter
    x = 0.75 * inch
    y = h - 0.75 * inch

    prov = purchase.get("proveedor") or {}
    prov_nombre = (prov.get("nombre") or "").strip() or f"#{purchase.get('proveedor_id')}"
    prov_nit = (prov.get("nit") or "").strip()
    prov_tel = (prov.get("telefono") or "").strip()
    prov_dir = (prov.get("direccion") or "").strip()
    prov_email = (prov.get("email") or "").strip()

    c.setFont("Helvetica-Bold", 14)
    c.drawString(x, y, f"Purchase #{purchase.get('compra_id')}")
    y -= 18

    c.setFont("Helvetica", 10)
    c.drawString(x, y, f"Supplier: {prov_nombre}")
    y -= 14

    if prov_nit:
        c.drawString(x, y, f"NIT: {prov_nit}")
        y -= 14
    if prov_tel:
        c.drawString(x, y, f"Phone: {prov_tel}")
        y -= 14
    if prov_dir:
        c.drawString(x, y, f"Address: {prov_dir}")
        y -= 14
    if prov_email:
        c.drawString(x, y, f"Email: {prov_email}")
        y -= 14

    c.drawString(x, y, f"Date: {purchase.get('fecha_hora') or ''}")
    y -= 14
    c.drawString(x, y, f"Status: {purchase.get('estado') or ''}")
    y -= 14

    obs = purchase.get("observacion") or ""
    if obs:
        c.drawString(x, y, f"Note: {obs}")
        y -= 14

    y -= 8
    c.setFont("Helvetica-Bold", 10)
    c.drawString(x, y, "Product")
    c.drawString(x + 290, y, "Qty")
    c.drawString(x + 350, y, "Cost")
    c.drawString(x + 430, y, "Subtotal")
    y -= 10
    c.line(x, y, w - x, y)
    y -= 14

    c.setFont("Helvetica", 10)
    for d in purchase.get("detalle", []) or []:
        if y < 1.2 * inch:
            c.showPage()
            y = h - 0.75 * inch
            c.setFont("Helvetica-Bold", 10)
            c.drawString(x, y, "Product")
            c.drawString(x + 290, y, "Qty")
            c.drawString(x + 350, y, "Cost")
            c.drawString(x + 430, y, "Subtotal")
            y -= 10
            c.line(x, y, w - x, y)
            y -= 14
            c.setFont("Helvetica", 10)

        prod = d.get("producto") or {}
        pid = int(d.get("producto_id") or 0)
        cod = (prod.get("codigo") or "").strip()
        desc = (prod.get("descripcion") or "").strip()
        name = (f"{cod} - {desc}".strip(" -")) if (cod or desc) else f"#{pid}"

        qty = float(d.get("cantidad") or 0)
        cost = float(d.get("costo_unit") or 0)
        sub = float(d.get("subtotal") or 0)

        c.drawString(x, y, str(name)[:48])
        c.drawRightString(x + 325, y, f"{qty:g}")
        c.drawRightString(x + 405, y, f"{cost:.2f}")
        c.drawRightString(x + 500, y, f"{sub:.2f}")
        y -= 14

        lote = (d.get("lote") or "").strip()
        fv = (d.get("fecha_vencimiento") or "").strip()
        if lote or fv:
            extra = []
            if lote:
                extra.append(f"Lot: {lote}")
            if fv:
                extra.append(f"Exp: {fv}")
            c.setFont("Helvetica", 9)
            c.drawString(x + 12, y, " | ".join(extra)[:90])
            c.setFont("Helvetica", 10)
            y -= 12

    y -= 8
    c.line(x, y, w - x, y)
    y -= 18

    c.setFont("Helvetica-Bold", 12)
    total = float(purchase.get("total") or 0)
    c.drawRightString(w - x, y, f"Total: {total:.2f}")

    c.showPage()
    c.save()

    return buf.getvalue()
