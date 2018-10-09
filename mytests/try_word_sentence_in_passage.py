p = '''
I am a dog. I am a cat. He is a bull.
'''
p = '''
On a five to three vote,the Supreme Court knocked out much of Arizona's immigration law Monday-a modest policy victory for the Obama Aministration.But on the more important matter of the Constitution,the decision was an 8-0 defeat for the federal government and the states.
'''

p = '''
Australians have been warned to cut fresh strawberries before biting into them after several people found sewing needles hidden inside the fruit.

在一些人发现草莓内出现缝针之后，澳大利亚出当局警告人们，吃草莓时要先切开看看是否安全。

Contaminated punnets have been reported in supermarkets in the states of New South Wales, Queensland and Victoria. Contaminated zzzz.

据报道，新南威尔士州、昆士兰州和维多利亚州的超市的草莓都受到了影响。

One man was taken to hospital after eating a strawberry with a needle inside. A nine-year old boy bit into a contaminated fruit but did not swallow.

一名男子在吃了里面有针的草莓后被送往医院。而一名九岁的男孩咬了一口藏针的草莓，但没有吞下。 连发多起草莓藏针事件 澳大利亚多人中招

Several brands of strawberries have been withdrawn. These include Donnybrook strawberries and those sold by the Woolworths Group under the Berry Obsession and Berry Licious names.

目前已经有几个品牌的草莓被撤回。其中包括唐尼布鲁克莓果和沃尔沃斯集团出售的莓果迷和美味莓果。

The warnings came after a contaminated punnet was reported by Joshua Gane, who wrote in a Facebook post that a 21-year-old friend had suffered "severe abdominal pain".

网友约书亚·甘恩在他的脸书帖子上写到，他的一名21岁的朋友在吃了草莓后出现“严重的腹痛”，其后当局发出了警告。

"Until advised, consumers should cut up strawberries before consuming them," Queensland Health later said in a statement posted on Twitter.

昆士兰健康局随后在推特上发布了一份声明：“在警告解除之前，消费者应该在食用之前先切碎草莓。”

Australia's strawberry industry is worth some AUD130m a year and there are concerns that such incidents could have a lasting detrimental impact on sales.

澳大利亚的草莓产业的价值约为每年1.3亿澳元，有人担心此类事件可能对销售产生持久的不利影响。
'''

# 找出句子
import re
result = re.split('[\.[^\n]\s|(\.\n)|(\?)]', p)
result = [item.strip() +'.' for item in result if item]
result = [item for item in result if 'contaminated '.lower() in item.lower()]
for item in result:
    print(item)











