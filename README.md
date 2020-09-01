Usage:

Load haranalyze, create profile
```python
import haranalyze as har
profile = har.create_profile(my-profile)
```
```shell
listening for HAR file...
```

Add HAR file to dump folder:
```shell
created profile: my-profile
```

Select view structure: (example)
```python
profile.set_view("request.url")
```

Add filters (example):
```python
profile.filters.add("request.method!=POST")
```

```shell
added filter: request.method!=POST
```

Output contains view structure of elements based on filters
```shell
[0] https://google.com/api/query?example=1
[1] https://google.com/api/query?example=2
Total entries: 2
```

Save filters for later use (does not affect )
```python
profile.save()
```

Load profile again later
```python
profile = har.Profile(test-profile)
```

Other features:
```python
# undo last filter
profile.filters.undo()
# list all filters
profile.filters
# reset view structure
profile.reset_view()
```