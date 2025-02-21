import segno
qrcode = segno.make_qr('https://www.jmahfuz.com.br')
qrcode.save('qrcode.png', scale=10)