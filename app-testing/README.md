# Opentrons Installed Run App End to End Testing

> The purpose of this module is to allow tests to run against the installed Electron run app.

Slices of the tests will be selected as candidates for automation and then performed against the Opentrons run app executable on [Windows,Mac,Linux] and various robot configurations [Real Robot, Emulation, No Robot].

## Notes

- This folder is not plugged into the global Make ecosystem of the Opentrons mono repository. This is intentional, the tools in this folder are independent and will likely be used by only a few and are in no way a dependency of any other part of this repository.

## Steps

1. Have python installed per [CONTRIBUTING.md](../CONTRIBUTING.md)
2. Install the Opentrons application on your machine.
   1. https://opentrons.com/ot-app/
   2. This could also be done by building the installer on a branch and installing the App.
      1. for Mac
         1. `make -C app-shell dist-osx`
3. Install Chromedriver
   1. in the app-testing directory
      1. `sudo ./ci-tools/mac_get_chromedriver.sh 13.1.8` per the version of electron in the root package.json for electron
         1. if you experience `wget: command not found`
            1. brew install wget and try again
   2. when you run `chromedriver --version`
      1. It should work
      2. It should output the below. The chromedriver version must match Electron version we build into the App.
         1. ChromeDriver 91.0.4472.164 (6c672af59118e1b9f132f26dedbd34fdce3affb1-refs/heads/master@{#883390})
4. Create .env from example.env `cp example.env .env`
   1. Fill in values (if there are secrets)
   2. Make sure the paths work on your machine
5. Install pipenv globally against the python version you are using in this module.
   1. pip install -U pipenv
6. In the app-testing directory (make, python, pipenv required on your path)
   1. `make teardown`
   2. `make setup`
7. Run all tests
   1. `make test`
8. Run specific test(s)
   1. `pipenv run python -m pytest -k test_labware_landing`
      1. [See docs on pytest -k flag](https://docs.pytest.org/en/6.2.x/usage.html#specifying-tests-selecting-tests)

## Tools

python 3.10.2 - manage python with [pyenv](https://realpython.com/intro-to-pyenv)
[pipenv](https://pipenv.pypa.io/en/latest/)

## Locator Tool

Using the python REPL we can launch the app and in real time compose element locator strategies.
Then we can execute them, proving they work.
This alleviates having to run tests over and over to validate element locator strategies.

> Using this tool is imperative to reduce time of development when creating/troubleshooting element locators.

From the app-testing directory

```bash
pipenv run python -i locators.py
```

- `clean_exit()` should be used to exit the REPL.
- when you add a new Page Object (PO) you must add it to the imports, list of POs, and reload method so that you can change it and then call `reload()` to use the changes without exiting and restarting the REPL.
- `reload()` will allow the app to stay open but changes in your PO to be reflected.

> sometimes chromedriver does not cleanly exit.
> `pkill -x chromedriver`

## Emulation

We have made the choice to setup all test runs local and in CI against this emulator [config](./ci-tools/ot2_with_all_modules.yaml)

To use locally setup the [emulator](https://github.com/Opentrons/opentrons-emulation)

run our expected config

```shell
make run file_path=$MONOREPOPATH/app-testing/ci-tools/ot2_with_all_modules.yaml
```

ctrl-c to stop

remove the containers (this resets calibration, stopping them does not)

```shell
make remove file_path=$MONOREPOPATH/app-testing/ci-tools/ot2_with_all_modules.yaml
```

## Gotchas

- Only have 1 robot connected at once.
  - Build locators like you have more than 1 to future proof.
