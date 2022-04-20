# 
# OFFSET ASSIGNMENT ANALYSIS
# 
# Make boxplots
#
# Developped by Yuri Hérouard
# LIAS (ISAE-ENSMA)


import matplotlib.pyplot as plt

def printBoxplot4(functionNames, maxDelays, maxDelays_T, maxDelays_C, maxDelays_D, outputFileName):
    plt.figure(figsize=(16, 8))

    plt.subplot(141)
    # plt.boxplot(relativeMean, showmeans=True,meanprops={"marker":"s"})
    plt.boxplot(maxDelays, showmeans=True, meanline=True, showfliers=False)
    # plt.ylim(0, 14)
    plt.gca().xaxis.set_ticklabels(functionNames)
    plt.xticks(rotation=45, ha='right')
    plt.title('Maximum Delays')
    plt.minorticks_on()
    plt.tick_params(axis='x', which='minor', bottom=False)
    plt.grid(axis='x', linestyle = '--', which='major', linewidth = 0.5)
    plt.grid(axis='y', linestyle = '--', which='both', linewidth = 0.5)
    
    plt.subplot(142)
    plt.boxplot(maxDelays_T, showmeans=True, meanline=True, showfliers=False)
    # plt.ylim(0, 14)
    plt.gca().xaxis.set_ticklabels(functionNames)
    plt.xticks(rotation=45, ha='right')
    plt.title('MaxDelay / Period')
    plt.minorticks_on()
    plt.tick_params(axis='x', which='minor', bottom=False)
    plt.grid(axis='x', linestyle = '--', which='major', linewidth = 0.5)
    plt.grid(axis='y', linestyle = '--', which='both', linewidth = 0.5)

    
    plt.subplot(143)
    plt.boxplot(maxDelays_C, showmeans=True, meanline=True, showfliers=False)
    # plt.ylim(0, 14)
    plt.gca().xaxis.set_ticklabels(functionNames)
    plt.xticks(rotation=45, ha='right')
    plt.title('MaxDelay / max(ExecTimes)')
    plt.minorticks_on()
    plt.tick_params(axis='x', which='minor', bottom=False)
    plt.grid(axis='x', linestyle = '--', which='major', linewidth = 0.5)
    plt.grid(axis='y', linestyle = '--', which='both', linewidth = 0.5)

    plt.subplot(144)
    plt.boxplot(maxDelays_D, showmeans=True, meanline=True, showfliers=False)
    # plt.ylim(0, 14)
    plt.gca().xaxis.set_ticklabels(functionNames)
    plt.xticks(rotation=45, ha='right')
    plt.title('Max Deadline Miss')
    plt.minorticks_on()
    plt.tick_params(axis='x', which='minor', bottom=False)
    plt.grid(axis='x', linestyle = '--', which='major', linewidth = 0.5)
    plt.grid(axis='y', linestyle = '--', which='both', linewidth = 0.5)

    plt.subplots_adjust(bottom=0.3)
    plt.savefig(outputFileName+'.pdf')
    plt.savefig(outputFileName+'.png')
    return