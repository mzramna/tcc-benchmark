from more_itertools import unique_everseen
import csv
import shutil

def remove_duplicate_file(infile,outfile):
    with open(infile,'r') as f, open(outfile,'w') as out_file:
        out_file.writelines(unique_everseen(f))

def sort_csv(infile,sort_by):
    with open(infile,newline='') as csvfile:
        a=[]
        for row in csv.DictReader(csvfile, skipinitialspace=True):
            a.append(row)
        headers=list(a[0].keys())
        csvfile.close()
    sortedlist=sorted(a, key=lambda d: d[sort_by])

    with open("./tmp.csv", 'w') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for row in sortedlist:
            writer.writerow(row)
        f.close()
    shutil.move("./tmp.csv",infile)

