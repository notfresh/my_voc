r = ''
import re
import xmltodict
text = '<p>                                                    <span class="additional" title="形容词">ADJ</span>                If you describe someone as <b>inconsistent</b>, you arriticizing them for not behaving in the same way every time a similar situation occurs. 反复无常的                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               <span class="additional">[表不满]</span>                                                                                                                                 </p>'
print (re.sub(r'\s{2,}', '', text)  )

trans = r.css('div#authTrans div#collinsResult ul.ol>li')
x = trans[0].css('div.collinsMajorTrans p').extract_first()
x2 = re.sub('\s{2,}', '', x)
x3 = xmltodict.parse(x2)
x3['p']['#text']
