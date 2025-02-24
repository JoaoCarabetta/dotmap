#### How to create the dataset

If you want to create the dataset from scratch, follow these steps. Otherwise, start from step 4.

1. Run the notebook https://console.cloud.google.com/bigquery?ws=!1m7!1m6!12m5!1m3!1srj-escritorio-dev!2ssouthamerica-east1!3s371e01b4-ccd6-429a-b0ef-c73c384a1dd7!2e2

2. Download the points data and save it locally

3. Transform it in tiles:

```sh
./makefiles.sh
```

4. Serve tiles locally

```sh
tileserver-gl -c config.json --verbose
```

5. Open the map in your browser

```sh
uv run python -m http.server
```

and go to `http://localhost:8000`