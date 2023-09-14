import gzip

# To be run locally on the raw dataset.  Only zipped version to be tracked in git.
if __name__ == '__main__':
  with open('data.json', 'rb') as f_in, gzip.open('data.json.gz', 'wb') as f_out:
    f_out.writelines(f_in)
