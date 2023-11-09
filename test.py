found = dict()
data = open('ports.txt').read()
for item in data.split('\n'):
	if item in found:
		found[item] += 1
	else:
		found[item] = 1


for item in found:
	if found[item] > 50:
		print(item.ljust(10) + str(found[item]))
