#分割して1秒毎に出力										
#2024-09-20 18:45:36.655772+00:00 UTC,HR:0,RR:0,SPO2:0,HRV:0,BP:0/0										
#2024-09-20 18:45:36.810700+00:00 UTC,HR:0,RR:0,SPO2:0,HRV:0,BP:0/0										
#2024-09-20 18:45:36.973694+00:00 UTC,HR:0,RR:0,SPO2:0,HRV:0,BP:0/0										

#1秒毎に出力										
#session_id	datetime	frameNum	timeStamp	frameUsed	hr	dbp	sbp	resp	eda	source
#2.02E+13	2024-08-07 19:16:05:405691	9	6494.869	10	87.50211	70.92965	119.4948	12.68703	7.251212	webcam
#2.02E+13	2024-08-07 19:17:09:1580	5	6266.286	10	94.79957	83.24557	117.3883	13.35948	8.794392	webcam
#2.02E+13	2024-08-07 19:17:10:44284	15	7361.822	10	88.24873	71.05246	114.8953	12.47777	4.636355	webcam
#2.02E+13	2024-08-07 19:17:11:139989	25	8465.407	10	88.24873	71.05246	114.8953	12.47777	4.636355	webcam
#										
#時間フォーマット

import csv
filename = "data-fix2-test.csv"
with open(filename, 'r') as csvfile:
    csvreader = csv.reader(csvfile, delimiter='\t')
    for row in csvreader:
        STR_SPLIT=row
        print(STR_SPLIT)
        STR_SPLIT_2=STR_SPLIT[1].split(" ")
        STR_SPLIT_3=STR_SPLIT_2[-1].split(":")
        STR_SPLIT_4=STR_SPLIT_3[:-1]
        print(str(STR_SPLIT_4[2:3]))
#        print("XX", STR_SPLIT[5])
#        print("YY", STR_SPLIT[8])
        # YYYY-MM-DD HH:MM:SS.SSSSSS+00:00 UTC
        # XX 0
        # YY 0
