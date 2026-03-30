idTypes = {"auth_cert": [16,7,8,9,70],
            "IL": [10,65],
            "auth_indection": [18,12,14,15],
            "provaider": [4],
            "face":[5],
            "val":[60],
            "calibri":[72]}

for idType in list(idTypes.keys()):
    print(idTypes[idType])
    
print(type(idTypes.keys()))