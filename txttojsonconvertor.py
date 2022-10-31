import json


def main():
    i = 1
    while i < 6:
        if i == 2:
            i += 1
        fileinput = f'./TestJson/Test Example {i}.txt'
        convertTxtToJSON(i, fileinput)
        i += 1


# the file to be converted to
# json format
def convertTxtToJSON(fileNo, filename):
    # dictionary where the lines from
    # text will be stored

    # creating dictionary
    with open(filename) as fh:
        data = fh.read()

        # dict1 = data[0]
    # print(data)
    res = json.loads(data)
    print(res[0])
    # creating json file
    # the JSON file is named as test1
    out_file = open(f"./TestJson/test{fileNo}.json", "w")
    json.dump(res[0], out_file, indent=4, sort_keys=False)
    out_file.close()


main()
