# Job Tracker ETL

An ETL pipeline app which fetches job data from [USAJOBS](https://developer.usajobs.gov/API-Reference/)

## Brief
* ETL script querying USAJOBS API
  * Search using `data engineering` keyword
  * Prase data for results of interest to a job-seeker based in Chigago IL with 5 years
of experience
  * At least the fields: 
`PositionTitle`, `PositionURI` , `PositionLocation` , `PositionRemuneration`
* Load parsed results into user database

## How to run in docker
This application was build using Docker version 20 and docker compose version 2
* Run the application with `./run.sh` (you may need to update permissions with `chmod +x run.sh`)
* Open port `8000` on your browser to view the FastAPI interface and trigger 
the ETL pipeline with the `update_jobs` endpoint
  * Default parameters match project brief requirements
* View current stored jobs with the `/stored_jobs` endpoint
* Alternatively open port `8081` to view the mogngo UI (mongoexpress) 
using `mexpress` for username and password

### App design
* FastAPI used as the main interface to trigger ETL pipeline and viewing current database contents
* Using the `requests` library to query the Jobs API provider
* Passing in various query parameters e.g. location, job keyword, remuneration
* Parse response and use dataclass to enforce record schema for ingestion by MongoDB
* User `upsert` operation with bulk write to mongo to update existing or insert new records
* Return results of upsert operation to view records added or modified

### Ideas for implementing cloud deployment
Since this application would be triggered on a regular schedule e.g. daily
a serverless approach is more ideal than a continuous runtime, at least if the
processing and ETL loads are relatively small
* CI/CD pipeline using GitHub actions to test application and on success
publish docker image to AWS ECR
* Build an AWS Lambda function from this image
* Use AWS EventBridge to trigger the Lambda on a regular schedule
* Using AWS DocumentDB as an analogue to MongoDB (or Mongo Atlas)
* IaC approach could be cloud formation to provision updated Lambda during
the triggering of the CI/CD pipeline

Other considerations:
* For an application which requires higher throughput this approach may not
be optimal. 
* In this case a more scalable solution could be to scale the AWS lambdas
* Or implement a continuous runtime approach such as Kubernetes for horizontal scaling with replica sets
* Eventually IO bottlenecks with MongoDB will need handling with sharding for example


### Analytics
* Extend user API interface to display results on dashboards