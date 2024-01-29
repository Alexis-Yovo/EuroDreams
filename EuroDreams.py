import random

main_numbers = []
bonus_numbers = []
main_numbers_count=0
bonus_numbers_count=0

while main_numbers_count<6:
    number=random.randint(1,40)
    if number not in main_numbers:
         main_numbers.append(number)
         main_numbers_count+=1
while bonus_numbers_count<1:
    number=random.randint(1,5)
    if number not in bonus_numbers:
        bonus_numbers.append(number)
        bonus_numbers_count+=1

print(main_numbers,bonus_numbers)

        
