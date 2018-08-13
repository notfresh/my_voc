p = '''
I am a dog. I am a cat. He is a bull.
'''
p = '''
On a five to three vote,the Supreme Court knocked out much of Arizona's immigration law Monday-a modest policy victory for the Obama Aministration.But on the more important matter of the Constitution,the decision was an 8-0 defeat for the federal government and the states.
'''

p = '''
An arizona.United States,the majority overturned three of the four contested provisions of Arizona's controversial plan to have state and local police enfour federal immigrations law.The Constitutional principles that Washington alone has the power to "establish a uniform Rule of Anturalization" and that federal laws precede state laws are noncontroversial.Arizona had attempted to fashion state police that ran to the existing federal ones.

　　Justice Anthony Kennedy,joined by Chief Justice John Roberts and the Court's liberals,ruled that the state flew too close to the federal sun .On the overturned provisions the majority held the congress had deliberately "occupied the field " and Arizona had thus intruded on the federal's privileged powers
'''

# 找出句子
import re
result = re.split('[\.|\.\n]', p)
result = [item.strip() +'.' for item in result if item]
result = [item for item in result if ' controversial ' in item]
for item in result:
    print(item)








