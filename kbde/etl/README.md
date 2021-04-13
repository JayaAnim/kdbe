# ETL

The name says it all. Extract, transform, and load data.

Sources and destinations can include things like:

- Files
- Databases
- Web APIs


## Extractors

Extractors are responsible for pulling data from a source. These sources can be paginated. Extractors return an iterable which represents all data within the source.

### Overview

You can define an extractor for your specific data source. In this case, a JSON file:

```
from kbde.etl import extract


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


### Extending

You can define an extractor which can pull data from any source. A new extractor must define a `get_page()` function. This function is given a `page_number` value, representing the progress of data extraction from the source.

In the following example, we define an extractor which pulls data from an web API endpoint.

Let's assume that you have a web API which returns a JSON array of objects:

```
http://obuilds.com/api/v1/user?page=1
```

This endpoint accepts a GET parameter, `page`, which controls which subset of objects are returned in the JSON array.

A specific implementation of an extractor for this endpoint might looks like this:

```
from kbde.etl import extract
import requests


class ObuildsUserExtractor(extract.Extractor):
    
    def get_page(self, page_number):
        response = requests.get(f"http://obuilds.com/api/v1/user?page={page_number}")
        return response.json()
```

The above extractor would present all user objects within that API endpoint as a single iterable of objects:

```
all_users = ObuildsUserExtractor().extract()
```

This iterable can be fed into a "transformer", or a "loader". More on those below.


## Loaders

Loaders take an interable of data, and insert the data into a destination. The inserts are done in a paginated way, similarly to how data is extracted from sources.


### Overview

You can define a loader for your data destination. In this case, we will deposit data into a CSV file. The example assumes that each object in your data stream has `id`, `name`, and `email` attributes.

```
from kbde.etl import load


class MyCsvLoader(load.CsvLoader):
    file_path = "/path/to/my/file.csv"
    field_names = [
        "id",
        "name",
        "email",
    ]
```

You can instantiate the loader, and feed data from another source:

```
loader_instance = MyCsvLoader()
loader_instance.load(data)
```


### Extending

Loaders can place data into any source. A new loader must define a `load_page()` function. This function is given an `object_list` variable. The size of this `object_list` is controlled by the Loader's `.chunk_size` attribute.

In the following example, we define a loader which inserts data into a newline-delimited JSON file:

```python
from kbde.etl import load


class NewlineJsonLoader(load.Loader):
    file_path = "/path/to/my/file.json"
    chunk_size = 1000
    
    def load_data(self, object_list):
        with open(self.file_path, "a") as open_file:
            for obj in object_list:
                open_file.write(json.dumps(obj) + "\n")
```

The above loader would take an unlimited number of objects from an iterable, and place them into an NDJSON file, in chunks of 1000:

```
NewlineJsonLoader().load(data)
```


## Installing

See [Installing KBDE](../../../README.md#installing)
