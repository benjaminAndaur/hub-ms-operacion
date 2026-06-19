from datetime import date

import pytest
from unittest.mock import AsyncMock, MagicMock

from src.repository.operacion_repository import OperacionRepository
from src.models.operacion_db import Viaje


@pytest.fixture
def mock_session():
    return AsyncMock()


@pytest.fixture
def repository(mock_session):
    return OperacionRepository(mock_session)


@pytest.mark.asyncio
async def test_check_db_health_ejecuta_select_1_retorna_true(repository, mock_session):
    # Arrange
    mock_session.execute.return_value = MagicMock()

    # Act
    result = await repository.check_db_health()

    # Assert
    assert result is True
    mock_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_create_viaje_con_fechas_string_las_convierte_a_date(repository, mock_session):
    # Arrange
    data = {
        "fecha": "2026-06-18",
        "fecha_carga": "2026-06-17",
        "fecha_descarga": "2026-06-19",
        "estado": "IDA",
    }

    # Act
    result = await repository.create_viaje(data)

    # Assert
    assert isinstance(result, Viaje)
    assert result.fecha == date(2026, 6, 18)
    assert result.fecha_carga == date(2026, 6, 17)
    assert result.fecha_descarga == date(2026, 6, 19)
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once_with()
    mock_session.refresh.assert_called_once()


@pytest.mark.asyncio
async def test_create_viaje_con_fecha_carga_y_descarga_none_no_falla(repository, mock_session):
    # Arrange
    data = {
        "fecha": "2026-06-18",
        "fecha_carga": None,
        "fecha_descarga": None,
        "estado": "IDA",
    }

    # Act
    result = await repository.create_viaje(data)

    # Assert
    assert isinstance(result, Viaje)
    assert result.fecha == date(2026, 6, 18)
    assert result.fecha_carga is None
    assert result.fecha_descarga is None
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once_with()


@pytest.mark.asyncio
async def test_create_viaje_sin_campos_de_fecha_opcionales_no_falla(repository, mock_session):
    # Arrange
    data = {"fecha": "2026-06-18", "estado": "IDA"}

    # Act
    result = await repository.create_viaje(data)

    # Assert
    assert isinstance(result, Viaje)
    assert result.fecha == date(2026, 6, 18)
    mock_session.add.assert_called_once()


@pytest.mark.asyncio
async def test_get_viajes_sin_filtros_retorna_todos(repository, mock_session):
    # Arrange
    viajes_esperados = [MagicMock(spec=Viaje), MagicMock(spec=Viaje)]
    mock_scalars = MagicMock()
    mock_scalars.all.return_value = viajes_esperados
    mock_result = MagicMock()
    mock_result.scalars.return_value = mock_scalars
    mock_session.execute.return_value = mock_result

    # Act
    result = await repository.get_viajes()

    # Assert
    assert result == viajes_esperados
    mock_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_get_viajes_con_fecha_inicio_y_fin_string_filtra_correctamente(repository, mock_session):
    # Arrange
    viajes_esperados = [MagicMock(spec=Viaje)]
    mock_scalars = MagicMock()
    mock_scalars.all.return_value = viajes_esperados
    mock_result = MagicMock()
    mock_result.scalars.return_value = mock_scalars
    mock_session.execute.return_value = mock_result

    # Act
    result = await repository.get_viajes(fecha_inicio="2026-06-01", fecha_fin="2026-06-30")

    # Assert
    assert result == viajes_esperados
    mock_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_get_viajes_con_fecha_inicio_como_date_no_la_reconvierte(repository, mock_session):
    # Arrange
    viajes_esperados = []
    mock_scalars = MagicMock()
    mock_scalars.all.return_value = viajes_esperados
    mock_result = MagicMock()
    mock_result.scalars.return_value = mock_scalars
    mock_session.execute.return_value = mock_result

    # Act
    result = await repository.get_viajes(fecha_inicio=date(2026, 6, 1))

    # Assert
    assert result == viajes_esperados
    mock_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_get_viajes_sin_resultados_retorna_lista_vacia(repository, mock_session):
    # Arrange
    mock_scalars = MagicMock()
    mock_scalars.all.return_value = []
    mock_result = MagicMock()
    mock_result.scalars.return_value = mock_scalars
    mock_session.execute.return_value = mock_result

    # Act
    result = await repository.get_viajes()

    # Assert
    assert result == []


@pytest.mark.asyncio
async def test_get_viaje_by_id_existente_retorna_viaje(repository, mock_session):
    # Arrange
    viaje_esperado = MagicMock(spec=Viaje)
    mock_session.get.return_value = viaje_esperado

    # Act
    result = await repository.get_viaje_by_id(1)

    # Assert
    assert result == viaje_esperado
    mock_session.get.assert_called_once_with(Viaje, 1)


@pytest.mark.asyncio
async def test_get_viaje_by_id_inexistente_retorna_none(repository, mock_session):
    # Arrange
    mock_session.get.return_value = None

    # Act
    result = await repository.get_viaje_by_id(999)

    # Assert
    assert result is None
    mock_session.get.assert_called_once_with(Viaje, 999)


@pytest.mark.asyncio
async def test_update_viaje_existente_actualiza_campos_y_retorna_viaje(repository, mock_session):
    # Arrange
    viaje_existente = Viaje(id=1, fecha=date(2026, 6, 18), estado="IDA")
    mock_session.get.return_value = viaje_existente
    data = {"estado": "RETORNO"}

    # Act
    result = await repository.update_viaje(1, data)

    # Assert
    assert result == viaje_existente
    assert result.estado == "RETORNO"
    mock_session.commit.assert_called_once_with()
    mock_session.refresh.assert_called_once_with(viaje_existente)


@pytest.mark.asyncio
async def test_update_viaje_inexistente_retorna_none_sin_commit(repository, mock_session):
    # Arrange
    mock_session.get.return_value = None

    # Act
    result = await repository.update_viaje(999, {"estado": "RETORNO"})

    # Assert
    assert result is None
    mock_session.commit.assert_not_called()
    mock_session.refresh.assert_not_called()


@pytest.mark.asyncio
async def test_delete_viaje_existente_elimina_y_retorna_true(repository, mock_session):
    # Arrange
    viaje_existente = Viaje(id=1, fecha=date(2026, 6, 18), estado="IDA")
    mock_session.get.return_value = viaje_existente

    # Act
    result = await repository.delete_viaje(1)

    # Assert
    assert result is True
    mock_session.delete.assert_called_once_with(viaje_existente)
    mock_session.commit.assert_called_once_with()


@pytest.mark.asyncio
async def test_delete_viaje_inexistente_retorna_false_sin_commit(repository, mock_session):
    # Arrange
    mock_session.get.return_value = None

    # Act
    result = await repository.delete_viaje(999)

    # Assert
    assert result is False
    mock_session.delete.assert_not_called()
    mock_session.commit.assert_not_called()
