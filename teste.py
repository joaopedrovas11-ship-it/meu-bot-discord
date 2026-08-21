import qrcode

pix = "00020101021226820014br.gov.bcb.pix"

qr = qrcode.make(pix)
qr.save("pix.png")

print("QR Code criado com sucesso!")