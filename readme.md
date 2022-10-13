# Content Lense Mentions API

This API extracts mentions of human beings from texts and collects additional information from Wikidata.

## Building the Docker image

Build the Docker image by running:

`docker build -f Docker/Dockerfile -t content-lense-mentions:latest .`

## Running the service

Start the container with

`docker run -it --rm -p 5000:5000 content-lense-mentions`

## Using the api

### Analyse articles

To analyse an article send it to the `/articles` endpoint as `Content-Type: application/json` with the following stucture:

```json
{
    "id": 0, 
    "heading":"The Headline of the Article",
    "summary":"A short summary / abstract of the article",
    "authors": ["First Author", "Second Author"],
    "body": "The entire fulltext"
}
```

### Get available information for previously mentioned people

Information on the (most likely) human being mentioned in a previously analyzed text can be retrieved by name from the `/people` route. The name is given as the `name` query parameter, e. g.:

`http://localhost:5000/people?name=Angela%20Merkel`