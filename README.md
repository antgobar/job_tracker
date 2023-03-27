# Job Tracker ETL

An ETL pipeline app which fetches job data from [USAJOBS](https://developer.usajobs.gov/API-Reference/)

## Brief
* ETL script querying USAJOBS API
  * Search using the `data engineering` keyword
  * Prase data for results of interest to a job-seeker based in Chicago IL with 5 years
of experience
  * At least the fields: 
`PositionTitle`, `PositionURI`, `PositionLocation`, `PositionRemuneration`
* Load parsed results into the mongo database

## Running this application locally
This application was created using `docker version 20` and `docker compose version 2`
**Make sure you create a `.env` file in the root directory with the keys `API_USER=<your USAJobAPI username>` and `API_KEY=<your api key>`**
* Run the application with `./run.sh` (you may need to update permissions with `chmod +x run.sh`)
* Open your browser on `localhost:8000/docs` to view the Swagger interface and trigger 
the ETL pipeline with the `/etl` endpoint
  * Default parameters match project brief requirements
* View current stored jobs with the `/jobs` endpoint
* Alternatively got to port `8081` to view the mongo UI (mongo express) 
using `mexpress` for username and password
* Wipe the collection with `/wipe`

## App design
* FastAPI used as the main interface to trigger the ETL pipeline and view current database contents
* Using the `requests` library to query the Jobs API provider
* Passing in various query parameters e.g. location, job keyword, remuneration
* Parse response and use dataclass to enforce record schema for ingestion by MongoDB
* MongoDB is used here because multiple tables with relationships are not being created
for simple ETL a NoSQL approach is appropriate
* User `upsert` operation with bulk write to mongo to update existing or insert new records
* Return results of upsert operation to view records added or modified

## CI/CD
* Pipeline using GitHub actions to test the application, build a docker image
push it to AWS ECR and create an AWS Lambda from the image
* The docker container has access to a Mongo Atlas cluster
* (My) lambda function is available here https://s5ybntl5ns36qxvh3uvddxs64u0nemes.lambda-url.eu-west-2.on.aws/

## Secrets
Include the following secrets if you want to deploy this yourself
* `API_KEY`: Jobs API key
* `API_USER`: Jobs API user
* `AWS_ACCESS_KEY_ID`
* `AWS_DEFAULT_REGION`
* `AWS_ECR_IMAGE_URI`
* `AWS_SECRET_ACCESS_KEY`
* `MONGO_URI`: e.g. Mongo Alass connection URI


## Further ideas for implementing cloud deployment
Since this application would be triggered on a regular schedule e.g. daily
a serverless approach is more ideal than a continuous runtime, at least if the
processing and ETL loads are relatively small
* Use AWS EventBridge to trigger the Lambda on a regular schedule
* Email user updated jobs report
* Using AWS DocumentDB as an analogue to MongoDb
* IaC approach could be cloud formation to provision Lambda and EventBridge rules during CI/CD

## Other considerations:
* For an application which requires higher throughput this approach may not
be optimal. E.g. I had to increase the Lambda memory allocation
* In this case a more scalable solution could be to scale the AWS lambdas
* Or implement a continuous runtime approach such as Kubernetes for horizontal scaling with replica sets
or AWS ECS architecture
* Eventually IO bottlenecks with MongoDB will need handling with sharding for example

## Future state ...
* Analytics: Extend user API interface to display results on dashboards
* Further testing to include `db.py` unittests
