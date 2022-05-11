import uuid

id = uuid.uuid4()
count=1
while id != uuid.uuid4():
    count+=1
print(count)