# AGENTS.md

Instruções para agentes que trabalham neste repositório. Leia isto antes de editar código, dados ou documentação.

## O que é este projeto

**dotmap** (**Onde o Brasil mora**) é um mapa de densidade de pontos do Censo Demográfico 2022 (IBGE). Raça, renda do responsável e idade ao falecer cobrem as 27 UFs. A unidade do ponto muda por view e zoom.

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
tile-join -f --no-tile-size-limit -o data/tiles/censo2022_income.mbtiles tiles/income/*/*/tiles.mbtiles
tile-join -f --no-tile-size-limit -o data/tiles/censo2022_deaths.mbtiles tiles/deaths/*/*/tiles.mbtiles
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

- `index.html` — UI, estilo, **um painel único** flutuante no desktop (story-first: h1 com a view, linha-herói `1 ponto = N` com estado de filtro, seletor, explainer, legenda com scroll próprio em telas baixas, e slot de stats fixado por **clique** — hover mantém o popup no cursor; clique vazio/✕/troca de view fecham o slot; a **busca é uma pill flutuante logo à direita do painel, alinhada ao topo**, `#desk-search`), rodapé fino, detalhes de hover e **toda** a lógica do mapa. O painel tem seletor **Raça / Renda** (**Óbitos existe no pipeline/tiles mas está oculto na UI** via `HIDDEN_VIEWS` em `index.html`; para reexibir, restaure o botão nos dois seletores e tire `deaths` do set). Basemap único: `light-v10` sem labels. A legenda e `1 ponto = N unidades` mudam por view. Painel **dev** só em loopback (`localhost` / `127.0.0.1` / `::1` / `*.localhost`): botão no canto superior direito ou `D` / `` ` ``, `sessionStorage` `dotmap-dev-panel`; mostra unidades/ponto, centro, bbox, hover e fonte dos tiles; ferramentas de paleta aparecem só em Raça. Mapa full-bleed (`#map` 100vw/100vh, com fallback `100dvh`), sem header em barra nem rail esquerdo. Título: o `h1` do desktop e o título do sheet mobile carregam a view ativa — **Onde o Brasil mora por Raça/Renda** (Óbitos oculto) — reescritos no switch; o `<title>` da página permanece só **Onde o Brasil mora**. Cada view reescreve também o explainer. Rodapé slim mantém os créditos Carabetta.xyz. **Mobile (≤640px)**: gramática Waze — cards e rodapé do desktop somem e tudo vive em **um bottom sheet** (`.m-chrome`, estados peek/half/full por drag no header, pointer events + transform, `sessionStorage` `dotmap-sheet-state`, primeira visita abre em half). Peek mostra título + `1 ponto = N` — o título do sheet (`#sheet-title`) carrega a view ativa (**Onde o Brasil mora por Raça/Renda**, atualizado no switch; Óbitos oculto); half soma seletor de view + explainer; full soma legenda com linhas de 44px + solo e os **créditos** (não há rodapé mobile). A **busca fica fixa no topo da tela** (`#m-search-bar`, pill branca flutuante, safe-area-top; o geocoder único é re-parented para lá no mobile e volta à pill à direita do painel no desktop; o chip dev de localhost pode sobrepor a barra — não é parte do design). Sobre o mapa: **chip rail** de legenda (tap filtra, long-press = só); **sem** botões de zoom nem FAB no mobile (pinch faz o zoom; o NavigationControl fica `display:none` em ≤640px, atribuição Mapbox permanece). **Tap** no polígono mostra um card de stats **ancorado** acima do sheet (✕ ou tap no vazio fecha); tap com sheet aberto só o recolhe. Safe-areas via `env(safe-area-inset-*)` + `viewport-fit=cover`. Detalhes em `docs/docs.md`.
- `js/map.js` e `js/events.js` — arquivos vazios; não assumir que a lógica mora aí.
- `config.json` — fontes `censo2022`, `censo2022_income`, `censo2022_deaths` e `hover` em `data/tiles/`.
- `makefiles.sh` — raça usa `tiles/{UF}/`; temas usam `tiles/{theme}/{UF}/`. Aceita `./makefiles.sh RR income` e `./makefiles.sh RR 3,4,5,6 deaths`. Loop nacional: `./scripts/build_theme_pair.sh` por UF com `xargs -P 2`, depois um `tile-join` por tema.
- `scripts/themes.py` — fontes, campos, categorias, unidades e escalas de raça/renda/óbitos.
- `scripts/build_municipality.py` — CSV nacional + malha municipal IBGE → `municipality_{UF}.geojson` (stdlib; sem geopandas).
- `scripts/build_census_tract.py` — CSV nacional + malha de setor IBGE por UF → `census_tract_{UF}.geojson`.
- `scripts/build_density_clusters.py` — agrupa setores adjacentes da mesma classe de densidade → `cluster_{UF}_z3.geojson` … `cluster_{UF}_z6.geojson` (stdlib + mapshaper; adjacência via TopoJSON).
- `scripts/ibge_uf.py` — códigos IBGE, download, merge do hover concatenado e `tiles` (MBTiles de hover).
- `scripts/build_municipality_rj.py` — wrapper que chama `build_municipality.py RJ`.
- `notebooks/treat_2022.ipynb` — cruza microdados do censo com geometria de setores.
- `docs/docs.md` — zoom, densidade, schema demográfico, filtro na legenda, basemap **light-v10 sem labels e sem satellite**, chrome (painel único top-left, busca à direita, bottom sheet no mobile, rodapé slim; sem rail/FAB/zoom no mobile), ordem da legenda de raça parda → branca → preta → indígena → amarela, Óbitos oculto na UI, painel dev localhost-only.
- `docs/fontes.md` — URLs e caveats dos arquivos brutos do IBGE (raça nacional já baixada).
- `docs/local-setup.md` — como juntar os tiles versionados e servir o mapa.
- `docs/structure.md` — árvore do repositório.
- `debugger.html` — visualizador OpenLayers para inspecionar PBF local.
- `tiles/` — MBTiles versionados por UF (`tiles/{UF}/zoomN-N/tiles.mbtiles`). Cobertura atual: todas as 27 UFs (AC–TO, inclusive MG e SP).
- `data/` — gitignored. GeoJSON e MBTiles mesclados não entram no git.
- `dots/`, `output/` — intermediários do pipeline; também gitignored.

## Dados e camadas do mapa

Categorias raciais (keys estáveis no código e nos tiles): `branca`, `preta`, `amarela`, `parda`, `indigena`. **Ordem de exibição** na legenda, chips e breakdowns (população decrescente, Censo 2022): **parda → branca → preta → indígena → amarela**. `RACE_KEYS` no HUD é só a ordem da paleta, não a da UI.

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
- `income-points` / `deaths-points` — 27 UFs, atributo `cat`; layers `points-income` / `points-deaths`.
- `setores` — vector tiles `hover` (`source-layer: setores`), zoom 10–12 (overzoom até 14). O GeoJSON nacional não entra no browser (trava no zoom alto).
- `municipios` — vector tiles `hover` (`source-layer: municipios`), zoom 3–9.

Atributos esperados nos GeoJSON de polígonos: `populacao`, `branca`, `preta`, `amarela`, `parda`, `indigena`; municípios também têm `municipio`, `id_municipio`, `sigla_uf`.

Basemap único: `mapbox://styles/mapbox/light-v10` (**sem satellite**, sem toggle de estilo). Todas as layers `symbol` ficam `visibility: none` (sem nomes de cidade/rua/POI); fill/line/background ficam. Hover é `#202124`/8%; em touch, o **tap** no polígono dispara a mesma lógica (`map.on('click')` compartilha `updateHoverDetails` com o mousemove), mas no layout de celular o resultado vai para o card ancorado `#stats-dock` (não um popup sob o dedo) e tap no vazio fecha. Cores dos pontos são ColorBrewer Set1 permutadas (HUD test; contraste no light-v10): `branca` `#4daf4a`, `preta` `#ff7f00`, `amarela` `#377eb8`, `parda` `#e41a1c`, `indigena` `#984ea3`. HUD **Atual** / reset usa as mesmas; produção não carrega o HUD.

Zoom do mapa: `minZoom` 2 no construtor (o Mapbox trata o mínimo como exclusivo, `zoom > min`, para o usuário alcançar o 3), `maxZoom` 15 (atalho local Rio; tiles PBF param em 14). A câmera inicial é o Brasil inteiro: fallback `center [-51.9, -14.2]` / zoom 3.5 e, no `load`, `fitBounds` `[[-74, -34], [-32, 6]]`. Em viewports estreitos o fit cai abaixo de z3 e os pontos somem; nesses casos o zoom fica em 3.01 no mesmo centro. A source `points` declara `minzoom: 3` / `maxzoom: 14`. Scroll zoom está desligado; navegação pelo `NavigationControl` no canto inferior direito (`+/-`). Painel dev local: `1` Brasil, `2` Rio @ 15.

A escala da legenda (`1 ponto = N pessoas`) em `index.html` **bate com** `makefiles.sh` em 3–14 (4500 / 2000 / 900 / 400 / 150 / 120 / 90 / 70 / 50 / 35 / 25 / 20). Zoom 15 da câmera usa o N do z14 (20). Ao mudar densidade, atualize `makefiles.sh`, a legenda (`peoplePerDot`) e `docs/docs.md` juntos.

Renda nacional usa domicílios/ponto (1500 / 700 / 300 / 130 / 50 / 40 / 30 / 24 / 17 / 12 / 8 / 7) — cerca de 1/3 da escala de raça, para ~72,4M de domicílios renderizarem com a mesma densidade visual que ~202M de pessoas. Cor = faixa da mediana `V06006`; quantidade = responsáveis/domicílios `V06001`. Não interpretar como renda individual ou per capita. Óbitos usa 200 / 100 / 50 / 25 / 12 / 10 / 8 / 6 / 4 / 3 / 2 / 1 e fica mais esparso de propósito (~3,63M de óbitos visíveis, ~1/56 da população); categorias etárias somam sexos e incluem `death_age_suppressed`, porque `X`/`.` não são zeros observados.

Tiles gerados em `makefiles.sh` (não o hover): **setor agrupado** (`cluster` / `cluster_*_z3.geojson` … `_z6.geojson`) nos zooms **3–6** (`per_dot` 4500 / 2000 / 900 / 400); **setor censitário** (`census` / `census_tract_*.geojson`) nos zooms **7–14** (`per_dot` 150 / 120 / 90 / 70 / 50 / 35 / 25 / 20). Zoom 15 da câmera só faz overzoom do z=14. Tabela completa em [`docs/docs.md`](docs/docs.md). Hover no mapa é outro corte (município < 10, setor ≥ 10). Rebuild de z3–6: `python3 scripts/build_density_clusters.py UF` então `SKIP_TILE_JOIN=1 ./makefiles.sh UF 3,4,5,6` por UF, e um `tile-join` no fim. Todas as **27 UFs** já têm tiles de cluster nesses zooms.

## Convenções

- Atualize `docs/` junto com qualquer feature, mudança de zoom/densidade, schema de dados ou comportamento de UI.
- Comentários no código explicam o **porquê**, não o óbvio.
- Implemente o pedido por completo; não deixe stubs, TODOs no lugar de código, nem extraia para `js/` sem mover de fato a lógica e atualizar o HTML.
- Não commitar `data/`, tiles intermediários, `.env` ou tokens. O token Mapbox hoje está inline em `index.html`; não espalhe em mais lugares e não o coloque em docs públicos novos.
- UI e copy do mapa em português (Brasil). O nome do produto é **Onde o Brasil mora**; o `h1` do painel e o título do sheet mobile ganham o sufixo da view ativa (**por Raça / por Renda**, reescrito no switch; **por Óbitos** quando a view for reexibida), e o `<title>` da página fica só com o nome do produto. O explainer no painel é **Cada ponto é um grupo de pessoas. A cor é a raça declarada no Censo Demográfico 2022 (IBGE). O número de pessoas por ponto muda com o zoom.** (outras views reescrevem a explicação e o sufixo, nunca o nome antes do "por"). Nomes de categoria racial no código ficam sem acento (`indigena`, `preta`) para bater com os tiles.
- Preferir `uv` para Python. Não adicionar dependências sem necessidade.
- Mudanças de UI (layout, estado, rotas, dados renderizados) precisam ser verificadas no browser, não só por leitura de código.

## O que não fazer

- Não apagar `tiles/` ou `data/tiles/*.mbtiles` sem confirmação: regenerar é caro.
- Não tratar `docs/docs.md` e `TODO` como source of truth da densidade — o código em `makefiles.sh` e `index.html` é o que roda.
- Pontos cobrem as 27 UFs. A busca ainda restringe resultados ao bbox do RJ. Hover no browser é `data/tiles/hover.mbtiles`, não o GeoJSON concatenado.
- Não inventar novas categorias raciais além das cinco do IBGE usadas aqui.
