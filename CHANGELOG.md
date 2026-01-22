# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
* Introduced `CHANGELOG.md` instead of `release-notes`.
* End of support for Python 3.9.
* Replaced `pdm` with `uv`.

## [0.9.0] - 2024-11-18

### Changed
* End support for Python 3.8.
* Use `just` instead of PDM for development scripts.

## [0.8.0] - 2024-07-25

### Changed
* Enable skipping response validation for individual operations.

## [0.7.0] - 2024-04-16

### Changed
* Restore `stringcase`.

## [0.6.0] - 2024-04-16

### Changed
* Update dependencies.

### Fixed
* Fix `tox` setup.

## [0.5.0] - 2024-04-06

### Changed
* Update for latest `openapi-core`

### Added
* Add 3.12 tests to CI

## [0.4.1] - 2023-10-11

### Changed
* fix bug that removed parameter fields from spec

## [0.4.0] - 2023-10-08

### Changed
* Renamed modules.

### Added
* Added parameters to OperationSpec.

## [0.3.4] - 2023-08-25

### Changed
* Minor refactoring of creating a request inside async context.

## [0.3.3] - 2023-03-10

### Fixed
* Minor fix with loading from file.

## [0.3.2] - 2023-03-10

### Fixed
* Minor fix with loading from file.

## [0.3.1] - 2023-03-10

### Changed
* Improved spec loading from files.

## [0.3.0] - 2023-03-09

### Added
* Add support for `openapi-core 0.17`.

### Changed
* Improve OpenAPI request build to not require `asgiref`.
* Expand rules checked by `ruff`.

## [0.2.8] - 2023-03-04

### Added
* Add base URI when creating from file.
* Add custom OpenAPI request and response classes.

## [0.2.7] - 2023-03-01

### Changed
* Accept PyYAML >= 5.4.

## [0.2.6] - 2023-03-01

### Changed
* Replace Poetry with PDM.

## [0.2.5] - 2022-12-09

### Changed
* Allow for path-level path parameters.

## [0.2.4] - 2022-10-12

### Changed
* Minor refactoring.

## [0.2.3] - 2022-10-12

### Changed
* Updated dependency versions.
* Slightly improved documentation.

## [0.2.2] - 2022-10-05

### Fixed
* Bugfix: error when query arguments are present.

## [0.2.1] - 2022-09-22

### Added
* Added `py.typed` for compatibility.

### Changed
* Minor code cleanup.

## [0.2.0] - 2022-09-17

### Changed
* Updated dependencies.
* Internal refactoring to follow new `openapi-core` architecture.

## [0.1.1] - 2022-09-16

### Added
First automated release.
