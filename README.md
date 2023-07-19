
# Application-manager 

[![Actions Status][actions badge]][actions]
[![CodeCov][codecov badge]][codecov]
[![LICENSE][license badge]][license]

This component is charged to handle the starting and closure processes for specified docker containers. It is a container that connects to its own host machine in order to handle commands coming from the DHT.
## 1. Running Manager
### Application Managare Side
- [x] ``` docker build -t application_manager . ```
- [x] ``` docker run --network host -it -p 5000:5000 application_manager ```
- [x] ``` python3 script.py ```
### Application Manager Host Side
- [x] ``` docker engine installation  ``` https://docs.docker.com/engine/install/ubuntu/
- [x] ``` python3 Support_Manager.py ``` 
## 2. Usage &rarr; DHT Emulator
### Run a Container:
```console
$curl -X POST -H "Content-Type: application/json" -d '{"image": "hello-world"}' http://localhost:5000/run
```
### List Running Containers:
```console
$curl -X POST http://localhost:5000/list
```
### Stop a Container:
```console
$curl -X POST -H "Content-Type: application/json" -d '{"container_id": "bda1903f326e"}' http://localhost:5000/stop
```
### Stop a Container:
```console
$curl -X POST -H "Content-Type: application/json" -d '{"container_id": "bda1903f326e"}' http://localhost:5000/remove
```
### Check Application Manager Log
```console
$curl -X POST http://localhost:5000/check
```


# Acknowledgements

<!-- Links -->
[actions]: https://github.com/sifis-home/Application-Manager/actions
[codecov]: https://codecov.io/gh/sifis-home/Application-Manager
[license]: LICENSES/MIT.txt

<!-- Badges -->
[actions badge]: https://github.com/sifis-home/Application-Manager/workflows/Application-Manager/badge.svg
[codecov badge]: https://codecov.io/gh/sifis-home/Application-Manager/branch/master/graph/badge.svg
[license badge]: https://img.shields.io/badge/license-MIT-blue.svg


<!-- Badges -->
[actions badge]: https://github.com/sifis-home/Application-Manager/workflows/Application-Manager/badge.svg
[codecov badge]: https://codecov.io/gh/sifis-home/Application-Manager/branch/master/graph/badge.svg
[license badge]: https://img.shields.io/badge/license-MIT-blue.svg
