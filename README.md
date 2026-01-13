# MircroEmpresasBackend
Get-Content .\schema.sql | docker compose exec -T postgres psql -U sinpapel -d sinpapel
Get-Content .\seed.sql   | docker compose exec -T postgres psql -U sinpapel -d sinpapel
