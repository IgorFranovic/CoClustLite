from matplotlib import pyplot as plt



class Visualizer():
    def __init__(self, type, data, file_path, to_file=True, to_screen=False):
        # type of visualizer
        self.type = type
        self.data = data
        self.subplot_count = len(self.data)
        self.to_file = to_file
        self.to_screen = to_screen
        self.file_path = file_path + '\CoClustLite_Save.png'

    def visualize(self):
        if self.type == 'bar':
            self.visualize_bar()
        else:
            return None


    def visualize_bar(self):
        print("Visualizing...")
        #print(self.data)
        #input()
        #plt.title('Top ' + str(self.subplot_count) + ' clusters.')
        fig, axs = plt.subplots(self.subplot_count, 1, sharex=False, sharey=False, figsize=(16, 8))
        axs_cnt = 0
        for subplot in self.data:
            #print(subplot)
            names = []
            performance = []
            plt.sca(axs[axs_cnt])
            plt.xlim(0, 10)
            for i in range(len(subplot)):
                #print(subplot[i])
                name, score = subplot[i]
                names.append(name)
                performance.append(score)
                axs[axs_cnt].barh(i, score/10)
            axs_cnt += 1
            #print(axs_cnt)
            # draw subplot
            plt.yticks(range(3), names)
            plt.xticks(range(10), [str(i)+"%" for i in range(0, 101, 10)])


        if self.to_file:
            plt.savefig(self.file_path)
            print('Plot saved to file: ' + self.file_path)
        if self.to_screen:
            plt.show()
