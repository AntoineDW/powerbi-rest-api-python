# Power BI REST API with Python

A Python library created to easily use the Power BI REST API with Python.

## Getting started

### Installing

The library can be installed using pip:

```
pip install pbirest
```

## Using the libary

### Importing the library

To add the library to your Python project, use the following line:

```
import pbirest
```

### Connecting to the Power BI REST API

To connect to the Power BI REST API, you need to have a Microsoft account that has access to Power BI and an [Azure AD application](https://docs.microsoft.com/fr-fr/power-bi/developer/register-app). With all that, you can connect to the Power BI REST API using the following function:

```
pbirest.connect(
    client_id = [client_id (required)],
    username = [username (required)],
    password = [password (required)],
    tenant_id = [tenant_id],
    client_secret = [client_secret]
)
```

### Getting all the workspaces that you have access

As an example, here's how you can get a list of all the workspaces that the user connected to the Power BI REST API has access:

```
pbirest.get_workspaces()
```

## Author

[**Antoine DE WILDE**](https://github.com/AntoineDW) - *Data Consultant for [Treez Data Management](https://www.treez-data.fr/)*

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details