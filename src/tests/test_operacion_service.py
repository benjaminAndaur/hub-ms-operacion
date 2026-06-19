import pytest
from unittest.mock import AsyncMock

from src.service.operacion_service import OperacionService


@pytest.fixture
def mock_repo():
    return AsyncMock()


@pytest.fixture
def service(mock_repo):
    return OperacionService(mock_repo)


@pytest.mark.asyncio
async def test_check_db_health_repo_ok_retorna_true(service, mock_repo):
    # Arrange
    mock_repo.check_db_health.return_value = True

    # Act
    result = await service.check_db_health()

    # Assert
    assert result is True
    mock_repo.check_db_health.assert_called_once_with()


@pytest.mark.asyncio
async def test_check_db_health_repo_lanza_excepcion_retorna_false(service, mock_repo):
    # Arrange
    mock_repo.check_db_health.side_effect = Exception("connection error")

    # Act
    result = await service.check_db_health()

    # Assert
    assert result is False
    mock_repo.check_db_health.assert_called_once_with()


@pytest.mark.asyncio
async def test_create_viaje_con_datos_validos_retorna_viaje_creado(service, mock_repo):
    # Arrange
    data = {"fecha": "2026-06-18", "estado": "IDA", "conductor_id": 1}
    viaje_creado = {"id": 1, **data}
    mock_repo.create_viaje.return_value = viaje_creado

    # Act
    result = await service.create_viaje(data)

    # Assert
    assert result == viaje_creado
    mock_repo.create_viaje.assert_called_once_with(data)


@pytest.mark.asyncio
async def test_get_viajes_sin_filtros_retorna_lista_completa(service, mock_repo):
    # Arrange
    viajes = [{"id": 1}, {"id": 2}]
    mock_repo.get_viajes.return_value = viajes

    # Act
    result = await service.get_viajes()

    # Assert
    assert result == viajes
    mock_repo.get_viajes.assert_called_once_with(None, None)


@pytest.mark.asyncio
async def test_get_viajes_con_rango_de_fechas_pasa_filtros_al_repo(service, mock_repo):
    # Arrange
    viajes = [{"id": 1}]
    mock_repo.get_viajes.return_value = viajes

    # Act
    result = await service.get_viajes(fecha_inicio="2026-06-01", fecha_fin="2026-06-30")

    # Assert
    assert result == viajes
    mock_repo.get_viajes.assert_called_once_with("2026-06-01", "2026-06-30")


@pytest.mark.asyncio
async def test_get_viajes_sin_resultados_retorna_lista_vacia(service, mock_repo):
    # Arrange
    mock_repo.get_viajes.return_value = []

    # Act
    result = await service.get_viajes()

    # Assert
    assert result == []


@pytest.mark.asyncio
async def test_update_viaje_existente_retorna_viaje_actualizado(service, mock_repo):
    # Arrange
    data = {"estado": "RETORNO"}
    viaje_actualizado = {"id": 1, "estado": "RETORNO"}
    mock_repo.update_viaje.return_value = viaje_actualizado

    # Act
    result = await service.update_viaje(1, data)

    # Assert
    assert result == viaje_actualizado
    mock_repo.update_viaje.assert_called_once_with(1, data)


@pytest.mark.asyncio
async def test_update_viaje_inexistente_retorna_none(service, mock_repo):
    # Arrange
    mock_repo.update_viaje.return_value = None

    # Act
    result = await service.update_viaje(999, {"estado": "RETORNO"})

    # Assert
    assert result is None
    mock_repo.update_viaje.assert_called_once_with(999, {"estado": "RETORNO"})


@pytest.mark.asyncio
async def test_delete_viaje_existente_retorna_true(service, mock_repo):
    # Arrange
    mock_repo.delete_viaje.return_value = True

    # Act
    result = await service.delete_viaje(1)

    # Assert
    assert result is True
    mock_repo.delete_viaje.assert_called_once_with(1)


@pytest.mark.asyncio
async def test_delete_viaje_inexistente_retorna_false(service, mock_repo):
    # Arrange
    mock_repo.delete_viaje.return_value = False

    # Act
    result = await service.delete_viaje(999)

    # Assert
    assert result is False
    mock_repo.delete_viaje.assert_called_once_with(999)
