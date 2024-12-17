def write_dataset(query, answer):
    file = 'training-dataset.py'  # <-- This is the line you're asking about
    pr_chk = 0
    with open(file) as f:
        reader = csv.DictReader(f, delimiter=',')
        for row in reader:
            t1 = row['query']
            if t1 == query:
                pr_chk += 1
    if pr_chk == 0:
        file1 = 'training-dataset1.csv'
        with open(file) as f, open('training-dataset1.csv', 'w', encoding='utf-8', newline='') as csvfile:
            reader = csv.DictReader(f, delimiter=',')
            filewriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
            filewriter.writerow(['query', 'answer'])
            for row in reader:
                t1 = row['query']
                t2 = row['answer']
                filewriter.writerow([t1, t2])
            filewriter.writerow([query, answer])
        shutil.copy('training-dataset1.csv', file)
        os.remove(file1)
        return "success"
    else:
        return "Already Trained"
