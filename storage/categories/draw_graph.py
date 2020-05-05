from graphviz import Graph
import os
import xml.etree.cElementTree as ET

graph = Graph('G', filename='sb_first.gv', engine='dot', format="svg")
graph.clear()
graph.attr(bgcolor='white', label='agraph', fontcolor='white', splines="ortho")
graph.attr('node', fixedsize = "false", shape='box')
topics = []
edges = []
home = "C:/Users/Xenus/Desktop/Projects/NosferatuZodd/storage/categories"
raw_aiml = ''
for aimls in list(os.walk(home))[0][2]:
    tree = ET.ElementTree(file = home+'/'+aimls)
    for topic in tree.findall('topic'):
        topics.append(topic.attrib['name'])
        for child in topic.getiterator():
            if child.tag == 'set' and child.attrib['name'] == 'topic':
                edges.append((topic.attrib['name'], child.text))

topic_names = ['�����',
               '�����',
              '����������� ������',
              '���������',
              '�������������� �����',
              '����������� ������',
              'TV-��������',
              '������ ���������� ������',
              '������� �����������',
              'Priority Pass',
              '�����',
              '�������',
              '����������',
              '�������� ������',
              '������ ��� ����������',
              '������ � �����������',
              '������',
              '����� ��������',
              '����� ��������',
              '����� ��������',
              '���������',
              '�������� �������',
              '������',
              '������ ��������',
              '������ ��������',
              '������ ��������',
              '����',
              '������']
topic_list = zip(topics, topic_names)
edges = [i for i in set(edges) if i[0] is not None and i[1] is not None]


for uid, name in topic_list:
    graph.node(name = uid, id = uid, label = name)
for ancestor, descendant in edges:
    graph.edge(ancestor, descendant)
graph.view()
