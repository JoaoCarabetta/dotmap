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

Um clone fresco **não** tem `data/`. Os MBTiles por zoom estão em `tiles/`. Junte-os antes de servir (`tile-join` usa `-f`, não `--force`; `--no-tile-size-limit` evita dropar o tile SP+MG de z7, ~508 KB vs limite padrão de 500 KB):

```sh
mkdir -p data/tiles
tile-join -f --no-tile-size-limit -o data/tiles/censo2022.mbtiles tiles/*/*/tiles.mbtiles
npx --yes tileserver-gl -c config.json -V
uv run python -m http.server 8001
```

A página fica em `http://localhost:8001` (use 8000 se a porta estiver livre). Os tiles vêm de `http://localhost:8080/data/censo2022/{z}/{x}/{y}.pbf`.

Sem restaurar arquivos extras: pontos funcionam; hover (`data/tiles/hover.mbtiles`) dá 404 até `python3 scripts/ibge_uf.py tiles`. Detalhes em `docs/local-setup.md`.

Público: https://carabetta.xyz/dataviz/brazildots/ (repo `carabetta.xyz`, tileserver-gl-light no Docker, nginx faz proxy).

Não rode `./makefiles.sh` só para visualizar: exige UF (`./makefiles.sh RR`), precisa de GeoJSON que não está no git, e um run completo regenera 7–14 daquela UF (caro). Tiles de outras UFs não são apagados. Para só 3–6: `python3 scripts/build_density_clusters.py RR` e `./makefiles.sh RR 3,4,5,6`. Loop nacional: `SKIP_TILE_JOIN=1` por UF e um `tile-join` no fim.

Dataset do zero (CSV nacional + `python3 scripts/build_municipality.py UF` + `python3 scripts/build_census_tract.py UF` + `python3 scripts/build_density_clusters.py UF` + `./makefiles.sh UF`): ver `README.md`.

Alternativa ao http.server: `uv run python server.py` (Flask + CORS, porta 8000).

## Mapa de arquivos

- `index.html` — UI, estilo, dois cards flutuantes, rodapé fino, busca, legenda clicável, detalhes de hover e **toda** a lógica do mapa (sources, layers, hover, filtros). Painel **dev** só em loopback (`localhost` / `127.0.0.1` / `::1` / `*.localhost`): botão no canto superior direito ou `D` / `` ` ``, `sessionStorage` `dotmap-dev-panel`; mostra pessoas/ponto, centro, bbox, hover (corte z10) e **fonte** dos tiles (setor agrupado z3–6 / setor z7–14); zoom e raio são editáveis (slider; raio é multiplicador 0.5×–3× sobre a curva, `reset` volta a 1, `sessionStorage` `dotmap-dev-radius-mult`); **cores** para testar paletas (Atual / Dark2 / Set1 / Okabe–Ito / Print / Terra) com **permutar** (roda as mesmas 5 cores entre as raças), **embaralhar** e **reset**, `sessionStorage` `dotmap-dev-palette` + `dotmap-dev-permute` + `dotmap-dev-hues`; aplica `circle-color` e os swatches da legenda; atalhos `1` Brasil e `2` Rio @ zoom 15. Não aparece em `carabetta.xyz`. Mapa full-bleed (`#map` 100vw/100vh); não há header em barra nem rail esquerdo. **Card de intro** (`.chrome-stack` / `.intro-card`, top-left ~14px): título, explainer, divisor e busca (`mapbox-gl-geocoder` v5, cidade/bairro/CEP/endereço, `countries: br` + bbox RJ, sem pin; CEP de 8 dígitos via BrasilAPI). **Card de legenda** (`.detail-card`, ~268px) fica **canto inferior esquerdo** (`position: fixed; left: 14px`), acima do rodapé slim, com cinco linhas de raça (toggle + solo; multi-select; sem chip/dropdown) e `1 ponto = N pessoas`. Os números do município/setor ficam no **tooltip do mapa** (popup), não no card. Não inventar chips de outras camadas. Título do produto (`h1` e `<title>`): **Onde o Brasil mora**. Explainer: **Cada ponto é um grupo de pessoas. A cor é a raça declarada no Censo Demográfico 2022 (IBGE). O número de pessoas por ponto muda com o zoom.** (outras views reescrevem a explicação, não o h1). **Rodapé slim** (~32px, não a barra antiga de 60px): créditos **Carabetta.xyz** (`© 2026`), não Escritório de Dados. “Dados: IBGE” aponta para o FTP dos Agregados por Setores 2022; “Censo Demográfico 2022” aponta para o dataset Censo 2022 na Base dos Dados (`https://basedosdados.org/dataset/08a1546e-251f-4546-9fe0-b1e6ab2b203d`); GitHub aponta para `https://github.com/JoaoCarabetta/dotmap`. Zoom `+/-` fica no canto inferior direito, logo acima do rodapé.
- `js/map.js` e `js/events.js` — arquivos vazios; não assumir que a lógica mora aí.
- `config.json` — fontes `censo2022` (pontos) e `hover` (município/setor) em `data/tiles/`.
- `makefiles.sh` — gera pontos e MBTiles em `tiles/{UF}/zoomN-N/` e junta **todas** as UFs em `data/tiles/censo2022.mbtiles`. Aceita `./makefiles.sh RR 3,4,5,6` para rebuild parcial daquela UF.
- `scripts/build_municipality.py` — CSV nacional + malha municipal IBGE → `municipality_{UF}.geojson` (stdlib; sem geopandas).
- `scripts/build_census_tract.py` — CSV nacional + malha de setor IBGE por UF → `census_tract_{UF}.geojson`.
- `scripts/build_density_clusters.py` — agrupa setores adjacentes da mesma classe de densidade → `cluster_{UF}_z3.geojson` … `cluster_{UF}_z6.geojson` (stdlib + mapshaper; adjacência via TopoJSON).
- `scripts/ibge_uf.py` — códigos IBGE, download, merge do hover concatenado e `tiles` (MBTiles de hover).
- `scripts/build_municipality_rj.py` — wrapper que chama `build_municipality.py RJ`.
- `notebooks/treat_2022.ipynb` — cruza microdados do censo com geometria de setores.
- `docs/docs.md` — zoom, densidade, schema demográfico, filtro na legenda, basemap, chrome (intro top-left, legenda canto inferior esquerdo, rodapé slim; sem rail), painel dev localhost-only.
- `docs/fontes.md` — URLs e caveats dos arquivos brutos do IBGE (raça nacional já baixada).
- `docs/local-setup.md` — como juntar os tiles versionados e servir o mapa.
- `docs/structure.md` — árvore do repositório.
- `debugger.html` — visualizador OpenLayers para inspecionar PBF local.
- `tiles/` — MBTiles versionados por UF (`tiles/{UF}/zoomN-N/tiles.mbtiles`). Cobertura atual: todas as 27 UFs (AC–TO, inclusive MG e SP).
- `data/` — gitignored. GeoJSON e MBTiles mesclados não entram no git.
- `dots/`, `output/` — intermediários do pipeline; também gitignored.

## Dados e camadas do mapa

Categorias raciais (keys estáveis no código e nos tiles): `branca`, `preta`, `amarela`, `parda`, `indigena`.

Cores atuais dos pontos:

| Categoria | Cor |
|---|---|
| branca | `#4daf4a` |
| preta | `#ff7f00` |
| amarela | `#377eb8` |
| parda | `#e41a1c` |
| indigena | `#984ea3` |

Sources no mapa:

- `points` — vector tiles (`source-layer: points`), atributo `race`.
- `setores` — vector tiles `hover` (`source-layer: setores`), zoom 10–12 (overzoom até 14). O GeoJSON nacional não entra no browser (trava no zoom alto).
- `municipios` — vector tiles `hover` (`source-layer: municipios`), zoom 3–9.

Atributos esperados nos GeoJSON de polígonos: `populacao`, `branca`, `preta`, `amarela`, `parda`, `indigena`; municípios também têm `municipio`, `id_municipio`, `sigla_uf`.

Basemap: `mapbox://styles/mapbox/light-v10` (não dark-v10, não um estilo vazio). Depois do load, todas as layers `symbol` ficam `visibility: none` (sem nomes de cidade/rua/POI); fill/line/background do basemap ficam. Contornos de hover de setor/município usam `#202124` para ficar visíveis no fundo claro; o fill correspondente ganha um tint `#202124` a 8% só no hover. Cores dos pontos são ColorBrewer Set1 permutadas (HUD test; contraste no light-v10): `branca` `#4daf4a`, `preta` `#ff7f00`, `amarela` `#377eb8`, `parda` `#e41a1c`, `indigena` `#984ea3`. HUD **Atual** / reset usa as mesmas; produção não carrega o HUD.

Zoom do mapa: `minZoom` 2 no construtor (o Mapbox trata o mínimo como exclusivo, `zoom > min`, para o usuário alcançar o 3), `maxZoom` 15 (atalho local Rio; tiles PBF param em 14). A câmera inicial é o Brasil inteiro: fallback `center [-51.9, -14.2]` / zoom 3.5 e, no `load`, `fitBounds` `[[-74, -34], [-32, 6]]`. A source `points` declara `minzoom: 3` / `maxzoom: 14`. Scroll zoom está desligado; navegação pelo `NavigationControl` no canto inferior direito (`+/-`). Painel dev local: `1` Brasil, `2` Rio @ 15.

A escala da legenda (`1 ponto = N pessoas`) em `index.html` **bate com** `makefiles.sh` em 3–14 (4500 / 2000 / 900 / 400 / 150 / 120 / 90 / 70 / 50 / 35 / 25 / 20). Zoom 15 da câmera usa o N do z14 (20). Ao mudar densidade, atualize `makefiles.sh`, a legenda (`peoplePerDot`) e `docs/docs.md` juntos.

Tiles gerados em `makefiles.sh` (não o hover): **setor agrupado** (`cluster` / `cluster_*_z3.geojson` … `_z6.geojson`) nos zooms **3–6** (`per_dot` 4500 / 2000 / 900 / 400); **setor censitário** (`census` / `census_tract_*.geojson`) nos zooms **7–14** (`per_dot` 150 / 120 / 90 / 70 / 50 / 35 / 25 / 20). Zoom 15 da câmera só faz overzoom do z=14. Tabela completa em [`docs/docs.md`](docs/docs.md). Hover no mapa é outro corte (município < 10, setor ≥ 10). Rebuild de z3–6: `python3 scripts/build_density_clusters.py UF` então `SKIP_TILE_JOIN=1 ./makefiles.sh UF 3,4,5,6` por UF, e um `tile-join` no fim. Todas as **27 UFs** já têm tiles de cluster nesses zooms.

## Convenções

- Atualize `docs/` junto com qualquer feature, mudança de zoom/densidade, schema de dados ou comportamento de UI.
- Comentários no código explicam o **porquê**, não o óbvio.
- Implemente o pedido por completo; não deixe stubs, TODOs no lugar de código, nem extraia para `js/` sem mover de fato a lógica e atualizar o HTML.
- Não commitar `data/`, tiles intermediários, `.env` ou tokens. O token Mapbox hoje está inline em `index.html`; não espalhe em mais lugares e não o coloque em docs públicos novos.
- UI e copy do mapa em português (Brasil). Título do produto fica **Onde o Brasil mora** (h1/`<title>`); o explainer no card esquerdo é **Cada ponto é um grupo de pessoas. A cor é a raça declarada no Censo Demográfico 2022 (IBGE). O número de pessoas por ponto muda com o zoom.** (outras views reescrevem a explicação, não o h1). Nomes de categoria racial no código ficam sem acento (`indigena`, `preta`) para bater com os tiles.
- Preferir `uv` para Python. Não adicionar dependências sem necessidade.
- Mudanças de UI (layout, estado, rotas, dados renderizados) precisam ser verificadas no browser, não só por leitura de código.

## O que não fazer

- Não apagar `tiles/` ou `data/tiles/*.mbtiles` sem confirmação: regenerar é caro.
- Não tratar `docs/docs.md` e `TODO` como source of truth da densidade — o código em `makefiles.sh` e `index.html` é o que roda.
- Pontos cobrem as 27 UFs. A busca ainda restringe resultados ao bbox do RJ. Hover no browser é `data/tiles/hover.mbtiles`, não o GeoJSON concatenado.
- Não inventar novas categorias raciais além das cinco do IBGE usadas aqui.
