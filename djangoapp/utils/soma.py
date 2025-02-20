def somar(a,b):
    r = round((a / b - 1.0) * 100, 2) * -1
    
    return str(r) + '%'