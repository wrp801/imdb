# General Use

### Activate the environment

The enviornment shoudl be activated by running `env/Scripts/activate` on Unix based system or `env\Scipts\activate` on Windows. From there you can run `pip install -r requirements.txt` to get all the necessary libraries. 

### Running the program

The program is designed to be run from the command line. Per the requirements it has been set up to run for the following shows:

- Chernobyl
- Stranger Things
- The Mandalorian
- Mr. Robot
- Game of Thrones

Those have been pre-configured in the script. If you would like to add another series to the script, you will need to get the *id* and add it in. The *id* can be found by searching for the series on the [imdb website](www.imdb.com). For example, when searching for Stranger things the link results in: https://www.imdb.com/title/tt4574334/?ref_=fn_al_tt_1. The *id* is identified as that string that begins with **tt.....** right after the title. Once you have the id, add the name of the series in lower case to the `MAPPING` constant as the key, and the id as the value. 

#### Command line args
By default the program will fetch data for all 5 of the series unless otherwise specified. If you would only like to fetch data for just one series, use the `--single` option followed by the name of the series. Example is: 

```bash
python main.py --single "stranger things"
```

