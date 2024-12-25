rm -fr build
rm -fr dist

pyinstaller --name FreeHttp --windowed --icon=src/assets/icon.ico --add-data "src/assets/*;src/assets" --collect-all PyQt6 --collect-all aiohttp --collect-all qasync --collect-all chardet --exclude-module PyQt5 --distpath dist --noconfirm --debug all src/main.py