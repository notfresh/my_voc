from collections import OrderedDict

str1 = '''
Text 1

　　Among the annoying challenges facing the middle class is one that will probably go unmentioned in the next presidential campaign: What happens when the robots come for their jobs?

　　Don't dismiss that possibility entirely. About half of U.S. jobs are at high risk of being automated, according to a University of Oxford study, with the middle class disproportionately squeezed. Lower-income jobs like gardening or day care don't appeal to robots. But many middle-class occupations-trucking, financial advice, software engineering — have aroused their interest, or soon will. The rich own the robots, so they will be fine.

　　This isn't to be alarmist. Optimists point out that technological upheaval has benefited workers in the past. The Industrial Revolution didn't go so well for Luddites whose jobs were displaced by mechanized looms, but it eventually raised living standards and created more jobs than it destroyed. Likewise, automation should eventually boost productivity, stimulate demand by driving down prices, and free workers from hard, boring work. But in the medium term, middle-class workers may need a lot of help adjusting.

　　The first step, as Erik Brynjolfsson and Andrew McAfee argue in The Second Machine Age, should be rethinking education and job training. Curriculums —from grammar school to college- should evolve to focus less on memorizing facts and more on creativity and complex communication. Vocational schools should do a better job of fostering problem-solving skills and helping students work alongside robots. Online education can supplement the traditional kind. It could make extra training and instruction affordable. Professionals trying to acquire new skills will be able to do so without going into debt.

　　The challenge of coping with automation underlines the need for the U.S. to revive its fading business dynamism: Starting new companies must be made easier. In previous eras of drastic technological change, entrepreneurs smoothed the transition by dreaming up ways to combine labor and machines. The best uses of 3D printers and virtual reality haven't been invented yet. The U.S. needs the new companies that will invent them.

　　Finally, because automation threatens to widen the gap between capital income and labor income, taxes and the safety net will have to be rethought. Taxes on low-wage labor need to be cut, and wage subsidies such as the earned income tax credit should be expanded: This would boost incomes, encourage work, reward companies for job creation, and reduce inequality.

　　Technology will improve society in ways big and small over the next few years, yet this will be little comfort to those who find their lives and careers upended by automation. Destroying the machines that are coming for our jobs would be nuts. But policies to help workers adapt will be indispensable.
'''

# 先把字符串切割成单词序列,在这里， 我们需要使用正则表达式， 而不是split方法了。正则表达式支持多个符号切割。
import re
str2 = '''
a b c    d,
e
'''
list1 = re.split('\s+', str1, flags=re.MULTILINE)
# 过滤1， 把空字符串去掉
list1 = [item for item in list1 if item]
# 过滤2， 把末尾的标点符号去掉， 比如逗号
# TODO: 这些过滤应该整合起来,
# TODO： 这些过滤只应该发生在头或者尾
list1 = [item.replace(',', '') for item in list1 ]
# 过滤3， 把末尾的标点符号去掉， 比如句号
list1 = [item.replace('.', '') for item in list1 ]
# TODO： 连字符，也应该被过滤掉
list1 = [item.strip('-') for item in list1 ]
list1 = [item.lower() for item in list1]

# 去掉自己熟悉的单词
# TODO: 利用自己的词库进行过滤
# TODO： 可以做差集
familiar_words = ['a', 'i', 'to', 'from', 'in', 'of', 'will', 'be', 'that', 'this', 'in', 'out', 'the', 'and', 'on', 'jobs']
list1 = [item for item in list1 if item not in familiar_words]


# 现在开始统计单词的出现个数
# TODO 函数名字有待优化
def statistic(list_words):
    dict1 = OrderedDict()
    for item in list_words:
        if not dict1.get(item):
            dict1[item] = 1
        else:
            dict1[item] += 1
    return dict1


# 输出的时候应该按照出现次数多少从高到低排序。
dict1 = statistic(list1)
sorted_words = sorted(dict1.items(), key=lambda item: item[1], reverse=True)
for k, v in sorted_words:
    print(k, v)

# TODO： 想到一个好主意， 如何录入自己的词库， 出现频率高的单词多数都认识。 可以根据出现频率自己选择是否认识， 然后加入到自己的单词库。