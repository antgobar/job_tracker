echo "Building containers"
docker compose build --no-cache

echo "Running application. Press ctrl-C to stop."
docker compose up