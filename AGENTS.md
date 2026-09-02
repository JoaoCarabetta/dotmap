# AGENTS.md

Instruções para agentes que trabalham neste repositório. Leia isto antes de editar código, dados ou documentação.

## O que é este projeto

**dotmap** (**Onde o Brasil mora**) é um mapa de densidade de pontos da distribuição por cor ou raça no Brasil, com dados do Censo Demográfico 2022 (IBGE). Cada ponto representa um número de pessoas que varia com o zoom. O frontend usa Mapbox GL JS; os tiles vetoriais são gerados com Mapshaper + Tippecanoe e servidos localmente pelo tileserver-gl.

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

Sem restaurar arquivos extras: pontos funcionam; hover (`municipality.geojson` / `census_tract.geojson`) dá 404. Detalhes em `docs/local-setup.md`.

Público: https://carabetta.xyz/dataviz/brazildots/ (repo `carabetta.xyz`, tileserver-gl-light no Docker, nginx faz proxy).

Não rode `./makefiles.sh` só para visualizar: exige UF (`./makefiles.sh RJ`), precisa de GeoJSON que não está no git, e um run completo regenera 7–14 (caro). Para só 3–6: `./makefiles.sh RJ 3,4,5,6` (não apaga os outros zooms).

Dataset do zero (BigQuery / notebook + `./makefiles.sh RJ`): ver `README.md`.

Alternativa ao http.server: `uv run python server.py` (Flask + CORS, porta 8000).

## Mapa de arquivos

- `index.html` — UI, estilo, sidebar flutuante, busca, legenda, tooltip e **toda** a lógica do mapa (sources, layers, hover, filtros). Mapa full-bleed (`#map` 100vw/100vh); não há header/footer em barra. Título do produto (`h1` e `<title>`): **Onde o Brasil mora**. Subtítulo atual: **Cada ponto é um grupo de pessoas. A cor é a raça no Censo 2022.** (explica a viz; outras views reescrevem a explicação, não o h1). Card à esquerda (~340px) com título, subtítulo, busca (`mapbox-gl-geocoder` v5, cidade/CEP/endereço, `countries: br` + bbox RJ, sem pin; CEP de 8 dígitos via BrasilAPI), legenda (toggles + solo + escala) e créditos. Em viewports estreitas (≤520px) a card fica compacta; chevron expande/recolhe legenda + créditos. Créditos no card, não num rodapé: **Carabetta.xyz** (`© 2026`), não Escritório de Dados. “Dados: IBGE” aponta para o FTP dos Agregados por Setores 2022; “Censo Demográfico 2022” aponta para o dataset Censo 2022 na Base dos Dados (`https://basedosdados.org/dataset/08a1546e-251f-4546-9fe0-b1e6ab2b203d`); GitHub aponta para `https://github.com/JoaoCarabetta/dotmap`.
- `js/map.js` e `js/events.js` — arquivos vazios; não assumir que a lógica mora aí.
- `config.json` — fonte `censo2022` apontando para `data/tiles/censo2022.mbtiles`.
- `makefiles.sh` — gera GeoJSON de pontos por zoom e junta em um único MBTiles. Aceita `./makefiles.sh RJ 3,4,5,6` para rebuild parcial (não apaga `tiles/`).
- `scripts/build_municipality_rj.py` — agrega o CSV nacional + malha IBGE via mapshaper e escreve `municipality_RJ.geojson` (stdlib; sem geopandas).
- `notebooks/treat_2022.ipynb` — cruza microdados do censo com geometria de setores.
- `docs/docs.md` — zoom, densidade, schema demográfico, comportamento da legenda, basemap, chrome da sidebar (título/subtítulo, busca, créditos).
- `docs/fontes.md` — URLs e caveats dos arquivos brutos do IBGE (raça nacional já baixada).
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
- `setores` — GeoJSON concatenado `data/censo2022/output/tiles/race/census_tract.geojson` (simplificado no merge; hover a partir do zoom 10). Não escala até SP.
- `municipios` — GeoJSON concatenado `data/censo2022/output/tiles/race/municipality.geojson`. Hover abaixo do zoom 10.

Atributos esperados nos GeoJSON de polígonos: `populacao`, `branca`, `preta`, `amarela`, `parda`, `indigena`; municípios também têm `municipio`, `id_municipio`, `sigla_uf`.

Basemap: `mapbox://styles/mapbox/dark-v10`. Contornos de hover de setor/município usam `white` para ficar visíveis no fundo escuro. Cores dos pontos não mudam.

Zoom do mapa: `minzoom` 2 no construtor (o Mapbox trata o mínimo como exclusivo, `zoom > min`, para o usuário alcançar o 3), max 14, centro inicial no Rio (`[-43.1729, -22.9068]`), zoom inicial 7. A source `points` declara `minzoom: 3` para não pedir PBF de z=2. Scroll zoom está desligado; navegação pelo controle no canto superior direito (em viewports ≤520px o controle vai para o canto inferior direito, para não cobrir o card).

A escala da legenda (`1 ponto = N pessoas`) em `index.html` **bate com o pipeline em 3–6** (24000 / 12000 / 6000 / 3000) e **não bate em 7–14**. Ao mudar densidade, atualize `makefiles.sh`, a legenda e `docs/docs.md`.

`per_dot` atual no pipeline (`makefiles.sh`): zoom 3→24000 (city), 4→12000 (city), 5→6000 (city), 6→3000 (city), 7→150, 8→120, 9→90, 10→70, 11→50, 12→35, 13→25, 14→20 (census).

## Convenções

- Atualize `docs/` junto com qualquer feature, mudança de zoom/densidade, schema de dados ou comportamento de UI.
- Comentários no código explicam o **porquê**, não o óbvio.
- Implemente o pedido por completo; não deixe stubs, TODOs no lugar de código, nem extraia para `js/` sem mover de fato a lógica e atualizar o HTML.
- Não commitar `data/`, tiles intermediários, `.env` ou tokens. O token Mapbox hoje está inline em `index.html`; não espalhe em mais lugares e não o coloque em docs públicos novos.
- UI e copy do mapa em português (Brasil). Título do produto fica **Onde o Brasil mora** (h1/`<title>`); o subtítulo atual é **Cada ponto é um grupo de pessoas. A cor é a raça no Censo 2022.** (outras views reescrevem a explicação, não o h1). Nomes de categoria racial no código ficam sem acento (`indigena`, `preta`) para bater com os tiles.
- Preferir `uv` para Python. Não adicionar dependências sem necessidade.
- Mudanças de UI (layout, estado, rotas, dados renderizados) precisam ser verificadas no browser, não só por leitura de código.

## O que não fazer

- Não apagar `tiles/` ou `data/tiles/*.mbtiles` sem confirmação: regenerar é caro.
- Não tratar `docs/docs.md` e `TODO` como source of truth da densidade — o código em `makefiles.sh` e `index.html` é o que roda.
- Não assumir cobertura nacional no frontend: paths e centro estão no recorte RJ. A busca restringe resultados ao bbox do RJ.
- Não inventar novas categorias raciais além das cinco do IBGE usadas aqui.
