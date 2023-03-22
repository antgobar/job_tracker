# Job Tracker

An ETL pipeline app which fetches job data from [USAJOBS](https://developer.usajobs.gov/API-Reference/)

### Requirements
* ETL script querying USAJOBS API
  * Search using `data engineering` keyword
  * Prase data for results of interest to a job-seeker based in Chigago IL with 5 years
of experience
  * At least the fields: 
`PositionTitle`, `PositionURI` , `PositionLocation` , `PositionRemuneration`
* Load parsed results into user database

### How to run in docker
This application was build using Docker version 20
and docker compose version 2


### Considerations
* Rate Limiting on Search Jobs API 
  * Defaults to only "Public" jobs
  * User must make additional request to search for "Status" jobs
  * Maximum of 5,000 job records per query
  * Maximum of 500 job records returned per request
