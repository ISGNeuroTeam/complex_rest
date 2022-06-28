All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.3] - 2022-06-28
### Added
- Add [drf-spectacular](https://drf-spectacular.readthedocs.io/en/latest/) package
- Add `/schema/`, `/schema/redoc/`, `/schema/swagger-ui/` paths
- Add `collectstatic.sh` script
### Changed 
- Add `stopasgroup` and `killasgroup` settings to all services in supervisor base config
- Set complex rest image version in docker compose file
- Configure `media` and `static` directory

## [1.0.2] - 2022-05-17
### Changed
- Set forced celery task autodiscover
- Split services in docker compose file

## [1.0.1] - 2022-04-27
### Changed
- Set celery concurrency option
- Plugin loggers propagates to root logger
- Root logger level to WARN

## [1.0.0] - 2022-04-25
### Added
- Allow plugins to have custom configs for nginx unit
- Load plugin CELERY BEAT settings to schedule tasks
- clean_dev section in Makefile
- phone and photo fields to User model
- Logout and isLogged endpoints
### Fixed
- Terminating nginx unit processes
- Override empty stings in config with default values
- Allow login url without slash in the end
- Fix GroupCoordinatorNotAvailableError when first launch
### Changed
- Plugin admin handled by plugin process
- Change default port for complex rest to 55555
- Python version in plugin template to 3.9.7

## [0.1.1] - 2022-01-20
### Fixed
- Invoke celery app configuration from core.apps.py 
- Fix mistyping in start.sh and start_dev.sh
- complex_rest and celery services waiting for kafka in supervisord config

## [0.1.0] - 2021-12-29
### Added
- Changelog.md.

### Changed
- Start using "changelog".