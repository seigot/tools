#1秒毎に出力, ただし1秒をまたぐデータは前のデータで補間する
#session_id	datetime	frameNum	timeStamp	frameUsed	hr	dbp	sbp	resp	eda	source
#2.02E+13	2024-08-07 19:16:05:405691	9	6494.869	10	87.50211	70.92965	119.4948	12.68703	7.251212	webcam
#2.02E+13	2024-08-07 19:17:09:1580	5	6266.286	10	94.79957	83.24557	117.3883	13.35948	8.794392	webcam
#2.02E+13	2024-08-07 19:17:10:44284	15	7361.822	10	88.24873	71.05246	114.8953	12.47777	4.636355	webcam
#2.02E+13	2024-08-07 19:17:11:139989	25	8465.407	10	88.24873	71.05246	114.8953	12.47777	4.636355	webcam

from argparse import ArgumentParser
import csv

# filename
def get_option(fname):
    argparser = ArgumentParser()
    argparser.add_argument('-f', '--filename', type=str,
                            default=fname,
                            help='Specify filename')
    return argparser.parse_args()

filename_default = "data-fix2-test.csv"
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
        #STR="11111 YYYY-MM-DD HH:MM:SS.SSSSSS+00:00 UTC,XX:0,YY:0,ZZZZ:0,AAA:0,BB:0/0"
#        STR_SPLIT=STR.split(",")
        HH = row[0].split(" ")[1].split(":")[0]
        MM = row[0].split(" ")[1].split(":")[1]
        SS = row[0].split(" ")[1].split(":")[2].split(".")[0]
        current_time = int(HH)*3600 + int(MM)*60 + int(SS)
        print(current_time, prev_time,row)
#        if current_time == prev_time:
#             continue
        if prev_time == 0:
                # 一番初めのデータを書き込む.
                with open(csvfname, 'a', newline="") as f:
                        writer = csv.writer(f)
                        writer.writerow(row)
                prev_time = current_time
                prev_row = row
                continue
        with open(csvfname, 'a', newline="") as f:
                writer = csv.writer(f)
                for ii in range(current_time-prev_time-1):
                        # 1秒毎にデータを書き込む.
                        writer.writerow(prev_row)
                writer.writerow(row)
        prev_time = current_time
        prev_row = row
        # debug
        print(current_time, prev_time,row)
        #print([f'{elapsed_time:.2f}', *digits_only_list, ' <---org:', *digits_only_list_debug])

#with open(filename, 'r') as csvfile:
#    csvreader = csv.reader(csvfile, delimiter='\t')
#    for row in csvreader:
#        STR_SPLIT=row
#        print(STR_SPLIT)
#        STR_SPLIT_2=STR_SPLIT[1].split(" ")
#        STR_SPLIT_3=STR_SPLIT_2[-1].split(":")
#        STR_SPLIT_4=STR_SPLIT_3[:-1]
#        print(str(STR_SPLIT_4[2:3]))
#        print("XX", STR_SPLIT[5])
#        print("YY", STR_SPLIT[8])
        # YYYY-MM-DD HH:MM:SS.SSSSSS+00:00 UTC
        # XX 0
        # YY 0
