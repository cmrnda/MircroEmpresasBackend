from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

def build_purchase_pdf(purchase: dict, supplier_name: str, product_map: dict[int, str]) -> bytes:
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)

    w, h = letter
    x = 0.75 * inch
    y = h - 0.75 * inch

    c.setFont("Helvetica-Bold", 14)
    c.drawString(x, y, f"Purchase #{purchase.get('compra_id')}")
    y -= 18

    c.setFont("Helvetica", 10)
    c.drawString(x, y, f"Supplier: {supplier_name}")
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
    c.drawString(x + 300, y, "Qty")
    c.drawString(x + 360, y, "Cost")
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
            c.drawString(x + 300, y, "Qty")
            c.drawString(x + 360, y, "Cost")
            c.drawString(x + 430, y, "Subtotal")
            y -= 10
            c.line(x, y, w - x, y)
            y -= 14
            c.setFont("Helvetica", 10)

        pid = int(d.get("producto_id") or 0)
        desc = product_map.get(pid, f"#{pid}")

        qty = d.get("cantidad") or 0
        cost = d.get("costo_unit") or 0
        sub = d.get("subtotal") or 0

        c.drawString(x, y, str(desc)[:45])
        c.drawRightString(x + 335, y, str(qty))
        c.drawRightString(x + 415, y, f"{float(cost):.2f}")
        c.drawRightString(x + 500, y, f"{float(sub):.2f}")
        y -= 14

        lote = d.get("lote") or ""
        fv = d.get("fecha_vencimiento") or ""
        if lote or fv:
            extra = []
            if lote:
                extra.append(f"Lot: {lote}")
            if fv:
                extra.append(f"Exp: {fv}")
            c.setFont("Helvetica", 9)
            c.drawString(x + 12, y, " | ".join(extra)[:80])
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
