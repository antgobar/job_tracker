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
the ETL pipeline with the `/update_jobs` endpoint
  * Default parameters match project brief requirements
* View current stored jobs with the `/stored_jobs` endpoint
* Alternatively got to port `8081` to view the mongo UI (mongo express) 
using `mexpress` for username and password

## App design
* FastAPI used as the main interface to trigger the ETL pipeline and view current database contents
* Using the `requests` library to query the Jobs API provider
* Passing in various query parameters e.g. location, job keyword, remuneration
* Parse response and use dataclass to enforce record schema for ingestion by MongoDB
* MongoDB is used here because multiple tables with relationships are not being created
for simple ETL a NoSQL approach is appropriate
* User `upsert` operation with bulk write to mongo to update existing or insert new records
* Return results of upsert operation to view records added or modified

## Ideas for implementing cloud deployment
Since this application would be triggered on a regular schedule e.g. daily
a serverless approach is more ideal than a continuous runtime, at least if the
processing and ETL loads are relatively small
* CI/CD pipeline using GitHub actions to test the application, and on success
publish docker image to AWS ECR
* Build an AWS Lambda function from this image
* Use AWS EventBridge to trigger the Lambda on a regular schedule
* Using AWS DocumentDB as an analogue to MongoDB (or Mongo Atlas)
* IaC approach could be cloud formation to provision updated Lambda during
the triggering of the CI/CD pipeline

## Other considerations:
* For an application which requires higher throughput this approach may not
be optimal. 
* In this case a more scalable solution could be to scale the AWS lambdas
* Or implement a continuous runtime approach such as Kubernetes for horizontal scaling with replica sets
* Eventually IO bottlenecks with MongoDB will need handling with sharding for example

## Future state ...
* Analytics: Extend user API interface to display results on dashboards
* Testing: thorough unit testing with pytest, especially for Transformation steps in `jobs.py`, as 
well as end-to-end tests for ETL
