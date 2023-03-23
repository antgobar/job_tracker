echo "Building containers"
docker compose build

echo "Running application. Press ctrl-C to stop."
docker compose up