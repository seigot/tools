# 以下のデータフォーマットを分割して1秒毎に出力する
# 一番初めは無視する								
# 2024-09-20 18:45:36.655772+00:00 UTC,HR:0,RR:0,SPO2:0,HRV:0,BP:0/0										
# 2024-09-20 18:45:36.810700+00:00 UTC,HR:0,RR:0,SPO2:0,HRV:0,BP:0/0										
# 2024-09-20 18:45:36.973694+00:00 UTC,HR:0,RR:0,SPO2:0,HRV:0,BP:0/0										
# python data-fix1.py --filename data-fix1-test.csv

from argparse import ArgumentParser
import csv

# filename
def get_option(fname):
    argparser = ArgumentParser()
    argparser.add_argument('-f', '--filename', type=str,
                            default=fname,
                            help='Specify filename')
    return argparser.parse_args()

filename_default = "data-fix1-test.csv"
args = get_option(filename_default)
filename = args.filename

csvfname = filename + ".output.csv"
with open(csvfname, 'w', newline="") as f:
    writer = csv.writer(f)
#    writer.writerow(["time", "HR", "RR", "BP(MAX)", "BP(MIN)"])

# split()とかスライスを使って、文字列を分割する
with open(filename, 'r') as csvfile:
    csvreader = csv.reader(csvfile)
    prev_time = -1
    for row in csvreader:
        # 一番初めは無視する
        if prev_time == -1:
            prev_time = 0
            continue
        #STR="YYYY-MM-DD HH:MM:SS.SSSSSS+00:00 UTC,XX:0,YY:0,ZZZZ:0,AAA:0,BB:0/0"
#        STR_SPLIT=STR.split(",")
        HH = row[0].split(" ")[1].split(":")[0]
        MM = row[0].split(" ")[1].split(":")[1]
        SS = row[0].split(" ")[1].split(":")[2].split(".")[0]
        current_time = int(HH)*3600 + int(MM)*60 + int(SS)
#        STR_SPLIT=row
#        print(STR_SPLIT)
#        print(STR_SPLIT[0])
#        print("XX", STR_SPLIT[1][3:])
#        print("YY", STR_SPLIT[2][3:])
        # YYYY-MM-DD HH:MM:SS.SSSSSS+00:00 UTC
        # XX 0
        # YY 0
#        print(current_time, prev_time,row)
        if current_time == prev_time:
             continue
        prev_time = current_time
        # output .csv file.
        with open(csvfname, 'a', newline="") as f:
             writer = csv.writer(f)
             #writer.writerow(digits_only_list)
             writer.writerow(row)
        # debug
        print(current_time, prev_time,row)
        #print([f'{elapsed_time:.2f}', *digits_only_list, ' <---org:', *digits_only_list_debug])
