# brim-growth-challenge



### Docker
Building the Docker container

```
docker-compose up --build
```

Accessing the container
```
docker ps
```
This will returns a list of availables containers. For example:
| CONTAINER ID | IMAGE        | COMMAND                | CREATED     | STATUS       | PORTS                                       | NAMES                       |
|--------------|--------------|------------------------|-------------|--------------|---------------------------------------------|-----------------------------|
| bab9838834a1 | 2dfaac32d7f9 | "uvicorn app.main:ap…" | 2 hours ago | Up 7 minutes | 0.0.0.0:8000->8000/tcp, [::]:8000->8000/tcp | brim-growth-challenge-app-1 |

Copy the name of the container (in this case ```brim-growth-challenge-app-1```) and then execute the following command to access it
```
docker exec -it brim-growth-challenge-app-1 /bin/bash
```
Once you are inside the container, you will now be able to access the database. To do so, execute:
```
sqlite3 brim_challenge.db
```

Now we are able to execute queries and verify the logged events.
For example:
```
SELECT * FROM events;

# Output example:
1|score_calculated|a90a20985cc85ff|balanced|70|2025-07-04 18:11:33
2|score_calculated|b0841fd8abb6fed|balanced|0|2025-07-04 18:29:23
```

### Tests
To run the tests, execute the following command:
```
docker-compose exec app pytest -s
```

Scenarios covered:
