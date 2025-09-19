from fastapi import HTTPException, status

# Esta é a nossa exceção de credenciais centralizada.
# Qualquer arquivo que precisar dela irá importar deste local.
credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)