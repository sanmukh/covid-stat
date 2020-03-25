import matplotlib.pyplot as plt
import numpy as np
import argparse
import re
import os


class Covid():
    #Dataset Dependent Constants
    COVID_DIR='COVID-19'
    CNF_FILE=os.path.join(COVID_DIR,'csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv')
    DT_FILE=os.path.join(COVID_DIR,'csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv')


    #Struct for filenames
    class ftypes:
        pass

    ftypes.cnf = CNF_FILE
    ftypes.dt = DT_FILE

    #struct for relevant indices from the dataset
    class lindices:
        pass

    lindices.state = 0
    lindices.country = 1
    lindices.start = 4
    lindices.startc = 5 #start location for countries with comma

    #class level variables (static in c++)
    gcountry = None

    #these two variables contain the entire start to end range 
    x_all_data = None
    y_all_data = None

    #read_csv a global function which fills x_all_data, y_all_data
    @staticmethod
    def read_csv():
        countryregex1 = Covid.gcountry+","
        countryregex2 = '"' + Covid.gcountry + '"' + ','
        entries = None

        f = open(Covid.ftypes.cnf, 'r')
        header = f.readline()

        Covid.x_all_data = header.rstrip('\n').split(',')[Covid.lindices.start:]


        for line in f:
            if re.search(countryregex1, line) or re.search(countryregex2, line):
                mline = line.rstrip('\n').split(',')
                if ',' in Covid.gcountry:
                    matched_entries = [int(i) for i in mline[Covid.lindices.startc:]] 
                else:
                    matched_entries = [int(i) for i in mline[Covid.lindices.start:]] 
                if entries is None:
                    entries = matched_entries
                else:
                    for i in range(len(entries)):
                        entries[i] += matched_entries[i]
        Covid.y_all_data = entries 
        if Covid.y_all_data is None:
            print("Could not find the country/province name. Please check the name from the data file")
            exit(0)

    def generate_y_new(self, start, end):
        y_data = [0] 
        for i in range(start+1, end+1):
            y_data.append(Covid.y_all_data[i] - Covid.y_all_data[i-1])

        return y_data


    def generate_y_t2d(self, start, end):
        y_data = []

        half_locs = np.searchsorted(self.y_all_data, [ x/2.0 for x in self.y_all_data[start:end+1]], side='left')
        act_locs = range(start, end+1)

        for half_loc, act_loc in zip(half_locs, act_locs):
            if self.y_all_data[act_loc] == 0:
                y_data.append(0) #put zero if actual cases are zero for clarity in plot
            else:
                num_days = act_loc - half_loc
                if half_loc > 0:
                    new_cases = self.y_all_data[half_loc] - self.y_all_data[half_loc - 1]
                    nth_case = self.y_all_data[act_loc]/2.0 - self.y_all_data[half_loc - 1]
                    num_days = num_days + nth_case/new_cases
                y_data.append(num_days)
        return y_data



    #function definitions begin here
    def __init__(self, lcountry, start, end, plot, plottype):
        if Covid.gcountry is None:
            Covid.gcountry = lcountry

        self.plot = plot
        self.plottype = plottype
        
        if Covid.x_all_data is None and Covid.y_all_data is None:
            Covid.read_csv()
    
        if start < 0:
            self.start = 0
        else:
            self.start = start

        if end < 0 or end >= len(Covid.y_all_data):
            self.end = len(self.y_all_data) - 1
        else:
            self.end = end
        
        self.x_data = Covid.x_all_data[self.start:self.end+1]
        if plot == "all":
            self.y_data = Covid.y_all_data[self.start:self.end+1]
        elif plot == "new":
            self.y_data = self.generate_y_new(self.start, self.end)
        elif plot == "t2d":
            self.y_data = self.generate_y_t2d(self.start, self.end)
        else:
            self.y_data = Covid.y_all_data[self.start:self.end] #default is all 

   

    def plot_COVID(self, xkcd):
        if xkcd == True:
            plt.xkcd()
        x_vals = [x for x in self.x_data[0:len(self.x_data):7]]
        xticks = np.arange(0,len(self.x_data),7)
        if (len(self.x_data) - 1)%7 != 0:
            x_vals.append(self.x_data[len(self.x_data)-1])
            xticks = np.append(xticks, xticks[len(xticks)-1] + (len(self.x_data) - 1)%7)

        if self.plottype == 'line':
            plt.plot(self.x_data, self.y_data, 'r--')
            plt.text(self.x_data[len(self.x_data)-1], self.y_data[len(self.y_data)-1], str(self.y_data[len(self.y_data)-1]))
        else:
            width = 0.8
            plt.bar(self.x_data, self.y_data, width)
            locs, labels = plt.xticks()
            st = np.abs(((len(locs) % 2) - 1)) #the [st::2] ensures only alternate labels are printed to remove clutter. Also, st offset ensures that last label is printed.
            for x, y in zip(locs[st::2], self.y_data[st::2]):
                plt.text(x-width/2, y, str(np.round(y,2)))

        plt.xticks(xticks, x_vals)
        plt.show()



def main():
    parser = argparse.ArgumentParser(description="generate plots on COVID-19")
    parser.add_argument('--plot', action='append', help="what to plot: all, new, t2d")
    parser.add_argument('--country', help='country name as per the timeseries csv file')
    parser.add_argument('--start', type=int, help='offset of first entry to read starting from 1/22/20')
    parser.add_argument('--end', type=int, help='offset of last entry to read starting from 1/22/20')
    parser.add_argument('--plottype', help="type of plot: bar, line")
    parser.add_argument('--plotxkcd', action="store_true", help="plot xkcd style")


    args = parser.parse_args()
    
    if args.country is None:
        print("Invalid country")
        exit(0)

    if args.start is None:
        args.start = 0

    if args.end is None:
        args.end = -1


    if args.start < 0:
        print("Invalid start date")
        exit(0)

    if args.end != -1 and args.end < args.start:
        print("End date cannot be less than start date")
        exit(0)

    for plt in args.plot:
        cvd = Covid(args.country, args.start, args.end, plt, args.plottype)
        cvd.plot_COVID(args.plotxkcd)



main()

