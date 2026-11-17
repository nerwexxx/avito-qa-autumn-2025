import requests
import pytest
import random
import uuid

# Базовый URL из задания
BASE_URL = "https://qa-internship.avito.com/api/1"

# Фикстура для генерации уникального sellerId
@pytest.fixture(scope="session")
def seller_id():
    return random.randint(111111, 999999)

# Фикстура для создания объявления
@pytest.fixture
def created_ad_id(seller_id):
    payload = {
        "name": "Тестовое объявление для автотеста",
        "price": 1500,
        "sellerId": seller_id,
        "statistics": {
            "contacts": 1,
            "likes": 5,
            "viewCount": 10
        }
    }
    response = requests.post(f"{BASE_URL}/item", json=payload)
    assert response.status_code == 200, "Не удалось создать тестовое объявление"
    data = response.json()
    ad_id = data.get("id") or data.get("result", {}).get("id")
    return ad_id

# TC-01: Создание объявления с валидными данными
@pytest.mark.xfail(reason="BUG-08: API возвращает 401 Unauthorized")
def test_create_ad(seller_id):
    payload = {
        "name": "Новое объявление",
        "price": 500,
        "sellerId": seller_id,
        "statistics": {"contacts": 0, "likes": 0, "viewCount": 0}
    }
    response = requests.post(f"{BASE_URL}/item", json=payload)
    
    assert response.status_code == 200, f"Ожидался 200, получен {response.status_code}"
    data = response.json()
    assert "id" in data or "result" in data, "В ответе нет созданного объекта"

# TC-02: Получение объявления по ID
@pytest.mark.xfail(reason="BUG-08: API возвращает 401 Unauthorized")
def test_get_ad_by_id(created_ad_id):
    response = requests.get(f"{BASE_URL}/item/{created_ad_id}")
    
    assert response.status_code == 200, f"Ожидался 200, получен {response.status_code}"
    data = response.json()
    assert isinstance(data, list), "Ожидался массив"
    assert data[0]["id"] == created_ad_id, "ID в ответе не совпадает с запрошенным"

# TC-03: Получение объявлений по sellerId
@pytest.mark.xfail(reason="BUG-08: API возвращает 401 Unauthorized")
def test_get_ads_by_seller_id(seller_id, created_ad_id):
    response = requests.get(f"{BASE_URL}/{seller_id}/item")
    
    assert response.status_code == 200, f"Ожидался 200, получен {response.status_code}"
    data = response.json()
    assert isinstance(data, list), "Ожидался массив объявлений"

# TC-04: Получение статистики
@pytest.mark.xfail(reason="BUG-08: API возвращает 401 Unauthorized")
def test_get_statistics(created_ad_id):
    response = requests.get(f"{BASE_URL}/statistic/{created_ad_id}")
    
    assert response.status_code == 200, f"Ожидался 200, получен {response.status_code}"
    data = response.json()
    assert isinstance(data, (list, dict)), "Ожидался объект или массив со статистикой"

# TC-05: Негативный - Создание без обязательного поля (name)
@pytest.mark.xfail(reason="BUG-08: API возвращает 401 Unauthorized")
def test_create_ad_invalid_data(seller_id):
    payload = {
        "price": 500,
        "sellerId": seller_id
    }
    response = requests.post(f"{BASE_URL}/item", json=payload)
    
    assert response.status_code == 400, f"Ожидался 400 (Bad Request), получен {response.status_code}"

# TC-06: Негативный - Получение по несуществующему ID
@pytest.mark.xfail(reason="BUG-08: API возвращает 401 Unauthorized")
def test_get_ad_invalid_id():
    fake_id = str(uuid.uuid4())
    response = requests.get(f"{BASE_URL}/item/{fake_id}")
    
    assert response.status_code in [400, 404], f"Ожидался 400 или 404, получен {response.status_code}"