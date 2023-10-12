str1 = "hello world abcdxz"

# grab the first character
str1[:1]

# remove the first character, grab everything else
str1[1:]

# grab the last character
str1[-1:]

# remove the last cahracter, grab everything else
str1[:-1]

# reverse the entire string
str2 = str1[::-1]

# this equal true lmfao
str1[1:] == str1[1::]
