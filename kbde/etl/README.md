# ETL

The name says it all. Extract, transform, and load data.

Sources and destinations can include things like:

- Files
- Databases
- Web APIs


## Overview

You can define an extractor for your specific data source. In this case, a JSON file:

```
from kbde.etl import extractor

class MyJsonFileExtractor(extractor.JsonExtractor):
    file_name = "/path/to/my/json/file.json"
```

You can then instantiate that extractor, and extract data from the file:

```
extractor_instance = MyJsonFileExtractor()
data = extractor_instance.extract()
```

At this point, `data` is an iterable of all data within the source. This is true for all extractors, regardless of the data source type (file, database, API, etc).

To examine the data:

```
for obj in data:
    print(obj)
```


## Installing

See [Installing KBDE](../../../README.md#installing)
