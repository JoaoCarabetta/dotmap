# AGENTS.md

Instruções para agentes que trabalham neste repositório. Leia isto antes de editar código, dados ou documentação.

## O que é este projeto

**dotmap** é um mapa de densidade de pontos da distribuição racial no Brasil, com dados do Censo Demográfico 2022 (IBGE). Cada ponto representa um número de pessoas que varia com o zoom. O frontend usa Mapbox GL JS; os tiles vetoriais são gerados com Mapshaper + Tippecanoe e servidos localmente pelo tileserver-gl.

Produto associado ao Escritório de Dados.

## Stack

| Camada | Tecnologia |
|---|---|
| Mapa / UI | HTML + Mapbox GL JS 2.3.1 (lógica hoje inline em `index.html`) |
| Servidor da página | Flask (`server.py`) ou `python -m http.server` (8000, ou outra se estiver ocupada) |
| Tiles | `npx tileserver-gl -c config.json` na porta 8080 (hardcoded em `index.html`) |
| Pipeline de pontos | `makefiles.sh` (mapshaper, tippecanoe, tile-join) — **não** rode só para ver o mapa |
| Tratamento de dados | `notebooks/treat_2022.ipynb` (pandas, geopandas, geobr) |
| Python | 3.12+, gerenciado com `uv` (`pyproject.toml`) |

## Comandos locais

Um clone fresco **não** tem `data/`. Os MBTiles por zoom estão em `tiles/`. Junte-os antes de servir (`tile-join` usa `-f`, não `--force`):

```sh
mkdir -p data/tiles
tile-join -f -o data/tiles/censo2022.mbtiles tiles/*/tiles.mbtiles
npx --yes tileserver-gl -c config.json -V
uv run python -m http.server 8001
```

A página fica em `http://localhost:8001` (use 8000 se a porta estiver livre). Os tiles vêm de `http://localhost:8080/data/censo2022/{z}/{x}/{y}.pbf`.

Sem restaurar arquivos extras: pontos funcionam; hover (`*_RJ.geojson`) e `assets/logo.png` dão 404. Detalhes em `docs/local-setup.md`.

Público: https://carabetta.xyz/dataviz/brazildots/ (repo `carabetta.xyz`, tileserver-gl-light no Docker, nginx faz proxy).

Não rode `./makefiles.sh` só para visualizar: exige UF (`./makefiles.sh RJ`), apaga `tiles/` e precisa de GeoJSON que não está no git.

Dataset do zero (BigQuery / notebook + `./makefiles.sh RJ`): ver `README.md`.

Alternativa ao http.server: `uv run python server.py` (Flask + CORS, porta 8000).

## Mapa de arquivos

- `index.html` — UI, estilo, header/footer, legenda, tooltip e **toda** a lógica do mapa (sources, layers, hover, filtros).
- `js/map.js` e `js/events.js` — arquivos vazios; não assumir que a lógica mora aí.
- `config.json` — fonte `censo2022` apontando para `data/tiles/censo2022.mbtiles`.
- `makefiles.sh` — gera GeoJSON de pontos por zoom e junta em um único MBTiles.
- `notebooks/treat_2022.ipynb` — cruza microdados do censo com geometria de setores.
- `docs/docs.md` — zoom, densidade, schema demográfico, comportamento da legenda.
- `docs/local-setup.md` — como juntar os tiles versionados e servir o mapa.
- `docs/structure.md` — árvore do repositório.
- `debugger.html` — visualizador OpenLayers para inspecionar PBF local.
- `data/` — gitignored. GeoJSON e MBTiles não entram no git.
- `dots/`, `output/` — intermediários do pipeline; também gitignored.

## Dados e camadas do mapa

Categorias raciais (keys estáveis no código e nos tiles): `branca`, `preta`, `amarela`, `parda`, `indigena`.

Cores atuais dos pontos:

| Categoria | Cor |
|---|---|
| branca | `#fb3640` |
| preta | `#fff07c` |
| amarela | `#89ffa7` |
| parda | `#3899c9` |
| indigena | `#e8800c` |

Sources no mapa:

- `points` — vector tiles (`source-layer: points`), atributo `race`.
- `setores` — GeoJSON `data/censo2022/output/tiles/race/census_tract_RJ.geojson`. Hover/tooltip a partir do zoom 10.
- `municipios` — GeoJSON `data/censo2022/output/tiles/race/municipality_RJ.geojson`. Hover/tooltip abaixo do zoom 10.

Atributos esperados nos GeoJSON de polígonos: `populacao`, `branca`, `preta`, `amarela`, `parda`, `indigena`; municípios também têm `municipio`, `id_municipio`, `sigla_uf`.

Zoom do mapa: min 7, max 14, centro inicial no Rio (`[-43.1729, -22.9068]`). Scroll zoom está desligado; navegação pelo controle no canto superior direito.

A escala da legenda (`1 ponto = N pessoas`) em `index.html` **não está alinhada** com os `per_dot` de `makefiles.sh`. Ao mudar densidade, atualize os dois e `docs/docs.md`.

`per_dot` atual no pipeline (`makefiles.sh`): zoom 7→150, 8→120, 9→90, 10→70, 11→50, 12→35, 13→25, 14→20. Agregação: setor censitário em todos esses zooms.

## Convenções

- Atualize `docs/` junto com qualquer feature, mudança de zoom/densidade, schema de dados ou comportamento de UI.
- Comentários no código explicam o **porquê**, não o óbvio.
- Implemente o pedido por completo; não deixe stubs, TODOs no lugar de código, nem extraia para `js/` sem mover de fato a lógica e atualizar o HTML.
- Não commitar `data/`, tiles intermediários, `.env` ou tokens. O token Mapbox hoje está inline em `index.html`; não espalhe em mais lugares e não o coloque em docs públicos novos.
- UI e copy do mapa em português (Brasil). Nomes de categoria racial no código ficam sem acento (`indigena`, `preta`) para bater com os tiles.
- Preferir `uv` para Python. Não adicionar dependências sem necessidade.
- Mudanças de UI (layout, estado, rotas, dados renderizados) precisam ser verificadas no browser, não só por leitura de código.

## O que não fazer

- Não apagar `tiles/` ou `data/tiles/*.mbtiles` sem confirmação: regenerar é caro.
- Não tratar `docs/docs.md` e `TODO` como source of truth da densidade — o código em `makefiles.sh` e `index.html` é o que roda.
- Não assumir cobertura nacional no frontend: paths e centro estão no recorte RJ.
- Não inventar novas categorias raciais além das cinco do IBGE usadas aqui.
