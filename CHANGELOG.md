# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- 

### Changed

- Pass storage to the embedded config attributes during initialization
- Simplifies config `Field` validation and casting flow
- Restructures package internal structure
- Improves unit tests
- Flatten multilevel storage during initialization
- Set type variable for `Field` children based on the returning type
- `Bool` field respects truthy strings like: "1", "Y", "T", "yes", "+" and `1` or `True`
- Import built-in **tomli** package for Python >= 3.11

### Removed

- `TypeMapper`
- Metaclass for `Config` creation
- `no_cache` flag
- class-level `Config` attributes won't be converted to `Fields` based on typing or default values;
  `Field` should be explicitly used whenever config attribute is defined
- `DebugFlag` field to use just `Bool` instead
- Drop maintenance for Python < 3.9

## [1.2.0] - 2022-05-23

### Added

- `DebuFlag` Field type
- env and dotenv storages now accept any key-value pairs if prefix is None

## [1.1.2] - 2022-05-22

### Fixed

- Fixes issue with empty line parsing in dotenv files.

## [1.1.1] - 2022-03-26

### Added

- Adds installation and quickstart sections

### Changed

- Improves alias section docs

### Removed

- Remove empty sections from CHANGELOG, they occupy too much space and
create too much noise in the file. People will have to assume that the
missing sections were intentionally left out because they contained no
notable changes.

## [1.1.0] - 2022-03-22

### Changed

- Embedded config respects default values

## [1.0.1] - 2022-03-22

### Changed

- Adds badges indicating PyPi downloads, Python versions, Licence

## [1.0.0] - 2022-03-22

### Added

- User defined config source order
- JSON support 
- INI support 
- YAML support 
- TOML support 
- Multilevel configs for environment variables and dotenv config sources
- Custom aliases 
- Type casting 
- Values validation based on type and/or value
