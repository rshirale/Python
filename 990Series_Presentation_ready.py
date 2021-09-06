import xml.etree.ElementTree as ET
from collections import Counter
import matplotlib.pyplot as plt
import pandas as pd
import glob
import time
from zipfile import ZipFile
import os
from tqdm import tqdm
from colorama import Fore, init
init()

while True:
    print(Fore.LIGHTYELLOW_EX + 'Enter full path of the folder where 990AllXML.zip is downloaded.')
    path = input()

    if path.endswith('990AllXML.zip'):
        path2 = '/Temp/IRS-990/'
        os.chdir(path2)
        if not os.path.isdir('990AllXML'):
            os.makedirs('990AllXML')
            with ZipFile('990AllXML.zip', 'r') as zipObj:
                # Extract all the contents of zip file in current directory
                print(Fore.GREEN + "\nunzipping files to", os.path.join(path2, '990AllXML'))
                zipObj.extractall('990AllXML')
                print(Fore.GREEN + "Completed unzipping files...\n")
            # sys.exit()
        else:
            pass

        # These column names will be used to create dataframe columns
        columns = ['EIN', 'Business Name Line1', 'Business Name Line2', 'Business Name Control', 'Phone Number',
                   'Street Address', 'City Name', 'State', 'Zip Code', 'Website URL', 'Formation Year',
                   'Employee_Count', 'Volunteers Count', 'Explanation Blob', 'Description Blob',
                   'Previous Year Grant Contribution', 'Current Year Grant Contribution',
                   'Change in Grant Contribution %']

        # Creating empty dataframe with column names created in line 12
        df = pd.DataFrame(columns=columns)

        # These are where all .xml files for IRS Tax 990 Series saved. Please change this to the path that matches your computer.

        file_path = input(Fore.CYAN + "Enter folder location where your files are unzipped\n")

        p = os.path.join(file_path, '*.*')

        # Line 47 onwards code is used to extract data from fields in every single .xml file
        # while this loop is running, you will see progress of extraction "15.78% processing done out of 100%"
        # For this project I am extracting fields that are mentioned in columns variable.
        file_num = 0
        last_time = time.time()
        current_time = time.strftime("%a, %d %b %Y %H:%M", time.localtime())
        print(Fore.YELLOW + f"It's {current_time}. Starting data extraction process.\n")
        time.sleep(5)

        for file in tqdm(glob.glob(p), desc='Data Extraction Progress'):
        #for file in glob.glob(p):

            #print(Fore.GREEN + f'{round((file_num / len(glob.glob(p))) * 100, 2)}% of 100% processing done.')


            tree = ET.parse(file)


            def xmlns(str):
                """This function removes xmlns namespace and returns on actual tag."""
                str1 = str.split('{')
                l = []
                for i in str1:
                    if '}' in i:
                        l.append(i.split('}')[1])
                    else:
                        l.append(i)
                var = ''.join(l)
                return var


            # Initializing some variables and lists to hold data
            root = tree.getroot()
            pyc = 0
            cyc = 0
            change = 0
            explanation_text = []
            description_text = []

            # Loop created to extract data from ReturnHeader tag
            for element in root[0][5].iter():

                if xmlns(element.tag) == 'EIN':
                    ein = element.text
                if xmlns(element.tag) == 'BusinessNameLine1Txt':
                    business_name_line1 = element.text
                if xmlns(element.tag) == 'BusinessNameLine2Txt':
                    business_name_line2 = element.text
                if xmlns(element.tag) == 'BusinessNameControlTxt':
                    bnc = element.text
                if xmlns(element.tag) == 'PhoneNum':
                    pn = element.text
                if xmlns(element.tag) == 'AddressLine1Txt':
                    address = element.text
                if xmlns(element.tag) == 'CityNm':
                    cn = element.text
                if xmlns(element.tag) == 'StateAbbreviationCd':
                    state = element.text
                if xmlns(element.tag) == 'ZIPCd':
                    zc = element.text

            # Loop created to extract data from ReturnData tag
            for element in root[1].iter():
                if xmlns(element.tag) == 'FormationYr':
                    fy = element.text
                if xmlns(element.tag) == 'WebsiteAddressTxt':
                    url = element.text
                if xmlns(element.tag) == 'TotalEmployeeCnt':
                    ec = int(element.text)
                if xmlns(element.tag) == 'TotalVolunteersCnt':
                    vc = int(element.text)
                if xmlns(element.tag) == 'ExplanationTxt':
                    explanation_text.append(element.text)
                if xmlns(element.tag) == 'Desc':
                    description_text.append(element.text)
                if xmlns(element.tag) == 'PYContributionsGrantsAmt':
                    pyc = int(element.text)
                if xmlns(element.tag) == 'CYContributionsGrantsAmt':
                    cyc = int(element.text)

                # This piece of code is to answer c part of the question. It calculates the change in Grant contribution vs.
                # previous year
                try:

                    change = round((cyc - pyc) / (pyc * 100), 2)

                except ZeroDivisionError:
                    change = 0

            # For every loop, after data is extracted from a XML file, the information is added to dataframe.
            df.loc[file_num] = [ein, business_name_line1, business_name_line2, bnc, pn,
                                address, cn, state, zc, url, fy, ec, vc, explanation_text, description_text,
                                pyc, cyc, change]

            file_num += 1

        # Above line is end of data extraction and transformation process. Depending on speed of computer, the time to extract
        # data may vary.

        new_cur_time = time.time()
        time_passed = int((new_cur_time - last_time) / 60)  # let's print the result in minutes


        print(Fore.RESET)
        print(Fore.GREEN + f"It took {time_passed} minutes to complete data extraction process.\n")
        time.sleep(5)


        def counter(data_frame):
            """returns frequency count of States in the dataframe"""
            return Counter(data_frame["State"])


        def printer(freq):
            """returns top 10 values that we counted using Counter"""
            print(f'State Count of NonProfits')
            for top in freq.most_common(10):
                print(f' {top[0]}   {top[1]}')


        def plotter(freq, q):
            """plots bar plot to answer question a and b"""
            name = [x for x in freq.keys()]
            value = [x for x in freq.values()]

            # Figure Size
            fig, ax = plt.subplots(figsize=(16, 9))
            # Horizontal Bar Plot
            ax.barh(name, value)

            # Remove axes splines
            for s in ['top', 'bottom', 'left', 'right']:
                ax.spines[s].set_visible(False)

            # Remove x, y Ticks
            ax.xaxis.set_ticks_position('none')
            ax.yaxis.set_ticks_position('none')

            # Add padding between axes and labels
            ax.xaxis.set_tick_params(pad=5)
            ax.yaxis.set_tick_params(pad=10)

            # Add x, y gridlines
            ax.grid(b=True, color='grey',
                    linestyle='-.', linewidth=0.5,
                    alpha=0.2)

            # Show top values
            ax.invert_yaxis()

            # Add annotation to bars
            for i in ax.patches:
                plt.text(i.get_width() + 0.2, i.get_y() + 0.5,
                         str(round((i.get_width()), 2)),
                         fontsize=10, fontweight='bold',
                         color='grey')

            # Add Plot Title
            ax.set_title(q, loc='center')

            # Show Plot
            plt.show()


        # Using collections.Counter library which counts elements of an iterable object
        freq_counter = counter(df)

        # Answering question number a:
        q1 = "What are the states with the highest number of nonprofits?"
        print(Fore.CYAN + "What are the states with the highest number of nonprofits?")
        print(Fore.GREEN + f'{freq_counter.most_common(1)[0][0]} has most number of nonprofits: '
                           f'{freq_counter.most_common(1)[0][1]}\n')
        printer(freq_counter)
        plotter(freq_counter, q1)

        # Answering question number b:
        q1 = "For each State, how many nonprofits have more than 70 employees?"
        print(Fore.RESET)
        print(Fore.CYAN + "For each State, how many nonprofits have more than 70 employees?")
        # filtering organizations with employee count of more than 70
        test = (df[df.Employee_Count > 70])
        freq_counter = counter(test)
        print(Fore.GREEN +
              f'The State {freq_counter.most_common(1)[0][0]} has most number of nonprofits: '
              f'{freq_counter.most_common(1)[0][1]} with more than 70 employees\n')
        printer(freq_counter)
        plotter(freq_counter, q1)

        # Answering question number c:
        print()
        print(Fore.RESET)
        print(Fore.CYAN + "Which are the top 10 nonprofits with the highest change in Grant Contribution vs. previous year?")
        df.rename(columns={'Change in Grant Contribution %': 'CIGC'}, inplace=True)
        # filtering organizations with Change in Grant Contribution more than 0
        test = (df[df.CIGC > 0])
        test = test.sort_values(by=['CIGC'], ascending=False)

        # Printing top 10 business that have highest Change in Grant Contribution %
        print(Fore.GREEN + f'   Business Name:')

        j = 0
        for i, row in test.iterrows():
            print(f'{j}: {row["Business Name Line1"]}')
            if j == 9:
                break
            j += 1

        # Attempting with answer question d using simple NLP:
        print(Fore.RESET)
        print(Fore.CYAN + "Imagine you are a focusing on providing cloud solutions to nonprofits with more than 70 "
                          "employees, "
              "\nwhat metrics would you be interested in looking at?"
              "\nIs there anything from the data that looks interesting to you?")
        print(Fore.RESET)
        break

    elif not path.endswith('990AllXML.zip'):
        print(Fore.RED + "\nYou entered wrong file path:", path, '\n')
        print(Fore.YELLOW + "An example of 990AllXML.zip file path is:")
        print(Fore.YELLOW + "C:\Temp\990AllXML.zip")
        print(Fore.YELLOW + "Let's try again...\n")
        print(Fore.RESET)
        continue


