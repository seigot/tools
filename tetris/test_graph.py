import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
 
plt.style.use('default')
sns.set()
sns.set_style('whitegrid')
sns.set_palette('Set1')

#x = np.array([0, 2, 4, 6, 8, 10])
score_list1 = [0.3, 1.2, 1.3, 1.8, 1.7, 1.5]
score_list2 = [2.1, 2.4, 2.3, 2.1, 2.2, 2.1, 33]
gene_1 = np.array(score_list1)
gene_2 = np.array(score_list2)

# plot graph
fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)
# plot
#ax.plot(x, gene_1, label='player1(left)')
#ax.plot(x, gene_2, label='player2(right)')
ax.plot(gene_1, label='player1(left)')
ax.plot(gene_2, label='player2(right)')
# set label
ax.legend()
ax.set_xlabel("time[sec]")
ax.set_ylabel("score")
# set ylim
max_score = max(max(score_list1), max(score_list2))
max_score = (max_score+1)//1 # clip
ax.set_ylim(0, max_score)
# show
plt.show()
