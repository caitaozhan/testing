import os
import glob

counter = 1
for filename in glob.glob('*.pdf'):
    new_filename = f'{counter}.pdf'
    os.rename(filename, new_filename)
    counter += 1
