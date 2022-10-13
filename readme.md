# Welcome to Content Lense Mentions API 👋

<p align="center">
  <img src="https://user-images.githubusercontent.com/15559708/195378979-701254fa-ada7-41d4-abc7-494a40207a6d.png" />
</p>

_This is a microservice APIof Content Lense, a project that aims at enabling publishers to easily gain insights into their content._
_This API extracts mentions of human beings from texts and collects additional information from Wikidata._

Please note that this repository is part of the [Content Lense Project](https://github.com/content-lense) and depends on the [Content Lense API](https://github.com/content-lense/content-lense-api).


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




## Supported by

Media Tech Lab [`media-tech-lab`](https://github.com/media-tech-lab)

<a href="https://www.media-lab.de/en/programs/media-tech-lab">
    <img src="https://raw.githubusercontent.com/media-tech-lab/.github/main/assets/mtl-powered-by.png" width="240" title="Media Tech Lab powered by logo">
</a>

---

Cloud Creators GmbH [`cloud-creators`](https://cloud-creators.de)


<a href="https://cloud-creators.de">
    <img src="https://cloud-creators.de/assets/images/cc-logo.svg" width="240" title="Supported by Cloud Creators GmbH">
</a>
