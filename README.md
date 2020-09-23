## Example Usage:
### Introduction

```python
>>> import harquery as hq
>>> hq.touch()
>>> profile = hq.scan("github.com/evaneldemachki")
>>> profile
```
```
created profile for: http://github.com 
Profile: github.com > evaneldemachki
```
`hq.touch` creates the `/.hq` folder in your working directory.
`hq.scan` then adds a directory structure to `/.hq/profiles` corresponding to the base URL (github.com) and returns a `hq.Profile` object.

```python
>>> profile.show()
```
```
[0] http://github.com/evaneldemachki
[1] https://github.com/evaneldemachki
[2] https://github.githubassets.com/assets/github-fb4eca21d084d0f71f1cbbb306bb2a13.css
[3] https://content-signature-2.cdn.mozilla.net
[4] https://github.githubassets.com/assets/frameworks-9579f2ec7b17946f9187720cb1846418.css
[5] https://avatars0.githubusercontent.com/u/f4tdfe345edg4
``` 
*Note: Output abbreviated for this example*
`Profile.show` lists a particular output attribute of each request in the HAR file. Which attribute is shown can be set with `Profile.focus` as shown below.
```python
>>> profile.focus("request.method")
```
```
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
```
Added filter: request.method='GET'
```
```python
>>> profile.focus("request.url")
>>> profile.show()
```
```
[0] http://github.com/evaneldemachki
[1] https://github.com/evaneldemachki
[2] https://github.githubassets.com/assets/github-fb4eca21d084d0f71f1cbbb306bb2a13.css
[3] https://github.githubassets.com/assets/frameworks-9579f2ec7b17946f9187720cb1846418.css
```
*Note: the entries originally at indices 3 and 5 have been filtered out, and the index has been reset*
```python
>>> profile.filters
```
```
[0] request.method='GET'
```
```python
>>> profile.filters.drop(0)
```
```
Dropped filter: request.method='GET'
```
```python
>>> profile.show()
```
```
[0] http://github.com/evaneldemachki
[1] https://github.com/evaneldemachki
[2] https://github.githubassets.com/assets/github-fb4eca21d084d0f71f1cbbb306bb2a13.css
[3] https://content-signature-2.cdn.mozilla.net
[4] https://github.githubassets.com/assets/frameworks-9579f2ec7b17946f9187720cb1846418.css
[5] https://avatars0.githubusercontent.com/u/f4tdfe345edg4
```
Using `Profile.drop`, the filter was removed and `Profile.show` now returns the full data set
### Syntax
**Equals**
`request.method = 'GET'` / `request.method != 'POST'`
**Contains**
`response.content.text # 'some string'` / `request.url !# 'githubassets'`
**Locate** 
`response.headers @ name = 'content-type' -> value # 'json'` 
This notation is helpful when working with objects such as response headers which resemble the following structure:
```json
{
    headers: [
        {"name": "Content-Type", "value": "application/json"},
        {"name": "Location", "value": "https://github.com/evaneldemachki"}
    ]
}
```
**Conversion Operators**
Objects can be converted into and searched as strings, and string representations of objects can be converted into and searched as objects.
This can be done in-line and/or chained to a query identifier with dot notation.
For example, consider the following response object:
```json
{
    response: {
        "content": {
            "text": "{'key': {'key2': 'value'}"
        }
    }
}
```
The value at `key2` can be accessed in a single query and checked against a constant despite it being located in a string using Conversion Operators:
`~(response.content.text).key.key2 # 'v'` <- True because 'value' contains 'v'
Alternatively, if we wanted to check the entire response section for the term 'value' without knowing where the term would occur, we could convert the entire response object into a string and search accordingly:
`$(response) # 'value'` <- True because 'value' is somewhere in the response


















