# Snowmail

## Summary

Snowmail ServiceNow Email Helper

_Note: If you have any questions or comments you can always use GitHub discussions, or DM me on the twitter @rbocchinfuso._

### Why

Needed and extensible way to take allow users to interact with ServiceNow via email.

## Requirements

- Python 3
  - [Anaconda](https://www.anaconda.com/products/individual) is a good choice, and what I use regardless of platform.

- All other requirements are in the requirements.txt file.
```pip install -r requirements.txt```

## Usage

- Download code from GitHub

  ```bash
  git clone https://github.com/CC-Digital-Innovation/snowmail.git
  ```

  _Note: If you don't have Git installed you can also just grab the zip:
  [https://github.com/CC-Digital-Innovation/snowmail/archive/master.zip](https://github.com/CC-Digital-Innovation/snowmail/archive/master.zip)_

- Copy config.ini.example to config.ini and modify as required

```text
Snowmail ServiceNow Email Helper

Usage:
    snowmail.py
    snowmail.py create (--name <NAME> --email <EMAIL> --subject <SUBJECT> --body <BODY>)
    snowmail.py update (--incident <INC#> --name <NAME> --email <EMAIL> --subject <SUBJECT> --body <BODY>)
    snowmail.py status (--incident <INC#> --name <NAME> --email <EMAIL>)

Arguments:
    crete           Create new incident.
    update          Update an existing incident.
    status          Check the status of an existing incident.

Options:
    -h --help       Show this screen.
    --version       Show version.
    --incident      Incident number.
    --name          Sender full name.
    --email         Sender Email.
    --subject       Email Subject.
    --body          Email body.
```

## Compatibility

This is was built and tested on Ubuntu 20.04 and most likely will only work on any Linux distro.

## Disclaimer

The code provided in this project is an open source example and should not be treated as an officially supported product. Use at your own risk. If you encounter any problems, please log an [issue](https://github.com/CC-Digital-Innovation/snowmail/issues).

## Contributing

1. Fork it!
2. Create your feature branch: `git checkout -b my-new-feature`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin my-new-feature`
5. Submit a pull request ツ

## History

- version 0.0.1 (initial release) - 2021/05/17

## Credits

Rich Bocchinfuso <<rbocchinfuso@gmail.com>>

## License

MIT License

Copyright (c) [2021] [Richard J. Bocchinfuso]

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
