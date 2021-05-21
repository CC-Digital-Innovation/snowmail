# Changelog

## [Unreleased]

- TODO
  - Function to parse phone numbers (need to think about the regex I am going to use)
  - Cleanup docopt documentation

## [0.0.6] - 2021-05-21

### Fixed

- Fixed item
- Rationalized logic and reordered function calls

### Ack message indentation to make response more readable

- Incident numbers to responses
- Enhanced logging
- Flags for DEV, PROD, LOCAL_TEST
- Added update and status to email interface

## [0.0.5] - 2021-05-20

### Fixed

- Fixed english translation on support request ack

## [0.0.4] - 2021-05-19

### Added

- english2native() function to translate ack message to native language
- prepare_ack() function to translate ack to sender native language
- SMTP function to send ack message to sender
- snowmail.bat to remedy the issue with the shell not exiting after emailparser calls snowmail to do its thing

### Changed

- translate() function to native2english() function

## [0.0.3] - 2021-05-18

### Added

- Translation function
- config.py and import config as cfg to pull initial configuration variables and owner details

### Changed

- Changed smarttech@ccxs.support to MSA-SmartTech@ccxs.support

### Fixed

- UTF-8 international support

### Removed

- Constants from snowmail.py; these are now stored in config.py and imported into snowmail.py

## [0.0.2] - 2021-05-17

### Added

- docopt CLI description language

### Changed

- Stopped using sys.argv in favor of docopt
- Emails regex parsing now happens by emailparser and passes to snowmail as docopt options
- Changed msa@ccxs.support to smarttech@msa@ccxs.support

### Removed

- Function to parse full name and email address.

## [0.0.1] - 2021-05-14

### Added

- snowmail function to parse emails using sys.argv
- snowmail function to parse full name and email address
- snowmail function to validate email address
- snowmail function to map email to SNOW INC fields and create SNOW INC

## [0.0.0] - 2021-05-14

### Added

- Creation of ccxs.support domain; required A, C, and MX DNS records
- SMTP services
- Creation of msa@ccxs.support email address
- Configuration of Email Parser (https://www.emailparser.com/)