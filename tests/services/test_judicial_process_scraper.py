import pytest
from unittest.mock import AsyncMock
from tusdatos.services.judicial_processes_scraper import JudicialProcessScraper
from httpx import codes
from httpx import Response


@pytest.fixture
def scraper(search_role, user_document_num):
    return JudicialProcessScraper(
        search_role=search_role,
        user_document_num=user_document_num,
    )


def create_mock_response(status_code=codes.OK, content=None, json_data=None):
    return Response(
        status_code=status_code,
        content=content,
        json=json_data,
    )


class TestJudicialProcessScraper:
    @pytest.mark.parametrize(
        "search_role, user_document_num, total_records",
        [
            ("ACTOR", "123456789", 10),
            ("ACTOR", "123456789", 100),
            ("DEMANDADO", "234234234", 1000),
            ("DEMANDADO", "234234234", 10000),
        ],
    )
    @pytest.mark.asyncio
    async def test_count_causes(self, search_role, user_document_num, total_records, scraper):
        mock_client = AsyncMock()
        mock_client.post.return_value = create_mock_response(content=str(total_records))

        count = await scraper._count_causes(client=mock_client)

        assert count == total_records
        mock_client.post.assert_awaited_once()

    @pytest.mark.parametrize(
        "search_role, user_document_num",
        [
            ("ACTOR", "123456789"),
            ("DEMANDADO", "234234234"),
        ],
    )
    @pytest.mark.asyncio
    async def test_search_all_causes(self, search_role, user_document_num, scraper):
        response_content = [
            {
                "estadoActual": "A",
                "fechaIngreso": "2023-09-14T16:04:17.180+00:00",
                "id": 1,
                "idJuicio": "09332200000000",
                "idMateria": 13,
                "iedocumentoAdjunto": "N",
                "nombreDelito": "PAGO DE DINERO",
            },
        ]

        mock_client = AsyncMock()
        mock_client.post.return_value = create_mock_response(json_data=response_content)

        causes = await scraper._search_all_causes(
            client=mock_client,
            total_causes=len(response_content),
        )

        assert len(causes) == len(response_content)
        assert causes[0].id == response_content[0]["id"]

        mock_client.post.assert_awaited_once()

    @pytest.mark.parametrize(
        "search_role, user_document_num",
        [
            ("ACTOR", "123456789"),
            ("DEMANDADO", "234234234"),
        ],
    )
    @pytest.mark.asyncio
    async def test_search_legal_actions(self, search_role, user_document_num, scraper):
        response_content = [
            {
                "codigo": 234234,
                "idJudicatura": "234234",
                "idJuicio": "2344230176",
                "fecha": "2024-03-13T20:23:39.000+00:00",
                "tipo": "OFICIO (OFICIO) ",
                "actividad": "Lorem ipsum dolor sit amet, consectetur adipiscing elit",
                "visible": "S",
                "origen": "ProvPrimera",
                "idMovimientoJuicioIncidente": 26015981,
                "ieTablaReferencia": "ProvPrimera",
                "ieDocumentoAdjunto": "S",
                "escapeOut": "false",
                "uuid": "29999993-152333333337-533333339-138888884",
                "alias": "HBA01",
                "nombreArchivo": "02222222222176_23_15_23_39_P20.pdf",
                "tipoIngreso": "O",
                "idTablaReferencia": "26015981",
            },
        ]

        mock_client = AsyncMock()
        mock_client.post.return_value = create_mock_response(json_data=response_content)

        legal_actions = await scraper._search_legal_actions(
            client=mock_client,
            incidente_judicatura_id="23423412342",
            judicatura_id=response_content[0]["idJudicatura"],
            juicio_id=response_content[0]["idJuicio"],
            movimiento_juicio_incidente_id=response_content[0]["idMovimientoJuicioIncidente"],
        )

        assert len(legal_actions) == len(response_content)

        for key in response_content[0].keys():
            assert getattr(legal_actions[0], key) == response_content[0][key]
