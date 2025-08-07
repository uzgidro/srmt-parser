import httpx
from config import API_KEY


# Убираем импорт JSONResponse, он больше не нужен


async def forward_data(url: str, data: dict | list):
    """
    Асинхронно отправляет данные на указанный URL.
    Предназначена для вызова из фоновых задач.
    Логирует результат в консоль.
    """
    headers = {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient() as client:
        try:
            print(f"BACKGROUND: Forwarding data to {url}...")
            response = await client.post(url, json=data, headers=headers, timeout=15.0)
            response.raise_for_status()

            # Просто логируем успех
            print(f"BACKGROUND: Successfully forwarded data. Target server responded with {response.status_code}.")

        except httpx.HTTPStatusError as e:
            # Логируем ошибку от целевого сервера
            error_details = f"Target server responded with {e.response.status_code}"
            print(f"BACKGROUND ERROR: Failed to forward data. {error_details}")
            # Можно также логировать тело ответа, если оно есть
            # print(f"Response body: {e.response.text}")

        except httpx.RequestError as e:
            # Логируем ошибку сети
            error_details = f"A network error occurred: {e.__class__.__name__}"
            print(f"BACKGROUND ERROR: Failed to forward data. {error_details}")
