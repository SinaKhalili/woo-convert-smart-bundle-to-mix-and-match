# Smart Bundles to Mix and Match Converter

A script to convert woocomerce smart bundle to mix-and-match

## Usage

1. Clone this repo. Make a [virtual environment](https://docs.python.org/3/library/venv.html) if you want (recommended)
2. Run `pip install -r requirements.txt`
3. Export all your products from woo commerce, and save it somewhere on your computer
4. Run `python main.py [path to exported file]`
    - to name the output file something else you can run `python main.py [path to exported file] [output file name]`

Your file will be saved in the same directory as the script, and will be named `OUTPUT-mix-and-match.csv` by default.