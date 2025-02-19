# Script para executar comandos Django

# Define o caminho para o executável do Python
$pythonPath = "python.exe"

# Define o caminho para o manage.py (relativo ao diretório do script)
$managePath = "djangoapp\manage.py"

# Comando collectstatic
Write-Host "Executando collectstatic..."
& $pythonPath $managePath collectstatic --noinput

# Comando makemigrations
Write-Host "Executando makemigrations..."
& $pythonPath $managePath makemigrations --noinput

# Comando migrate
Write-Host "Executando migrate..."
& $pythonPath $managePath migrate --noinput

# Comando runserver
Write-Host "Executando runserver..."
& $pythonPath $managePath runserver

Write-Host "Script finalizado."
