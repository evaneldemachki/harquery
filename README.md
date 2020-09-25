# Documentation

## Introduction

harquery is intended to be a comprehensive HTTP profiling library for Python, integrating the retrieval, filtration, analysis, and replication of large amounts of HTTP requests into a single, intuitive library.

### HTTP Archive Format (HAR)

> The HTTP Archive format, or HAR, is a JSON-formatted archive file format for logging of a web browser's interaction with a site.

harquery is capable of quickly breaking down these archives to streamline various processes including:

1. Automating data extraction
2. Analyzing authentication flows
3. Inspecting website performance
4. Breaking down complex API requests

### Dependencies

harquery takes advantage of the well-known Selenium library to automate HTTP requests with the Firefox/Chrome web drivers to simulate the way real people interact with the web. Selenium is then coupled with browsermob-proxy, which acts as a middle-man to capture all traffic between client and server.

## Getting Started

### Installation

Clone this repository:

```bash
git clone https://github.com/evaneldemachki/harquery
```

Navigate to package directory and install Python dependencies via pip:

```bash
cd harquery
pip install -r requirements.txt
```

Download and extract core dependencies into package directory:

1. [browsermob-proxy](http://bmp.lightbody.net/)
2. [geckodriver](https://github.com/mozilla/geckodriver/releases)

### Usage

`hq.touch` establishes a harquery workspace in your working directory.

In summary, `hq.profiles.add`:

1. opens a Firefox instance and visits the given URL
2. captures the resultant HAR file via browsermob-proxy and returns a harquery Profile object

The resultant `hq.Profile` object is generated from the HAR file and all operations performed on it are automatically reflected in the newly created directory structure, allowing one to pick up where they left off at a later time. One purpose of the Profile abstraction is to provide users the ability to quickly search, filter, and select entries from HAR files using a unique query syntax.

```python
>>> import harquery as hq
>>> hq.touch()
>>> profile = hq.profiles.add("github.com/evaneldemachki")
>>> profile
```

```console
Created profile for: http://github.com 
Profile: github.com > evaneldemachki
```

`Profile.show` lists a particular output attribute of each request in the HAR file. Which attribute is shown can be set by providing a query string to `Profile.focus` as shown below.

```python
>>> profile.show()
```

```console
[0] http://github.com/evaneldemachki
[1] https://github.com/evaneldemachki
[2] https://github.githubassets.com/assets/github-fb4eca21d084d0f71f1cbbb306bb2a13.css
[3] https://content-signature-2.cdn.mozilla.net
[4] https://github.githubassets.com/assets/frameworks-9579f2ec7b17946f9187720cb1846418.css
[5] https://avatars0.githubusercontent.com/u/f4tdfe345edg4
```

*Note: Output abbreviated for this example. A typical HAR file can have anywhere from 100 to 1000 entries.*


```python
>>> profile.focus("request.method")
```

```console
[0] GET
[1] GET
[2] GET
[3] CONNECT
[4] GET
[5] POST
```

Continuing with the above example, let's filter out all non-GET requests using the query syntax and then reset the focus to show the URLs:

```python
>>> profile.filters.add("request.method = 'GET'")
```

```console
Added filter: request.method='GET'
```

```python
>>> profile.focus("request.url")
>>> profile.show()
```

```console
[0] http://github.com/evaneldemachki
[1] https://github.com/evaneldemachki
[2] https://github.githubassets.com/assets/github-fb4eca21d084d0f71f1cbbb306bb2a13.css
[3] https://github.githubassets.com/assets/frameworks-9579f2ec7b17946f9187720cb1846418.css
```

*Note: the entries originally at indices 3 and 5 have been filtered out, and the index has been reset.*

```python
>>> profile.filters
```

```console
[0] request.method='GET'
```

## Example Queries

### Equality Operator

`request.method = 'GET'` / `request.method != 'POST'`

### Containment Operator

`response.content.text # 'some string'` / `request.url !# 'githubassets'`

### @ Operator

This operator is particularly helpful when working with objects such as response headers which resemble the following structure:

```json
[
    {
        "request": {...},
        "response": {
            "content": {...},
            "headers": [
                {
                    "name": "Content-Type",
                    "value":  "application/json"
                },
                {
                    "name": "Accept-Encoding",
                    "value": "gzip"
                },
            ]
        }
    },
    {
        "request": {...},
        "response": {
            "content": {...},
            "headers": [
                {
                    "name": "Content-Type",
                    "value":  "text/css"
                },
                {
                    "name": "Accept-Encoding",
                    "value": "*"
                },
            ]
        }
    }
]

```

We can use the `@` operator to only show entries where a `response["headers"]` array entry containing `"name": "Content-Type"` also contains `"value": "application/json"`:

```console
response.headers @ name = 'content-type' -> value # 'json'
```

### Conversion Functions

Objects can be converted into and searched as strings, and string representations of objects can be converted into and searched as objects.
This can be done in-line and/or chained to a query identifier with dot notation.
For example, consider the following example object:

We can use the `$` conversion operator to:

1. convert a JSON string at `response["content"]["text"]` to a dictionary object
2. traverse that object until arriving at the value in `key2`
3. check if that value is equal to `some_value`:

`$[json](response.content.text).key.key2 = 'some_value'`

Alternatively, if we wanted to check the entire response section for the string `some_value` without knowing where the term would occur, we could convert the entire response object into a string and search accordingly:

`$[string](response) # 'some_value'`

## Coming Soon

Only a very small amount of harquery's feature set is documented here. More documentation is on the way.

















