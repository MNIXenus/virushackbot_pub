import rutokenizer
import rupostagger
import rulemma
import dateparser

# подгрузка внешних данных
lemmatizer = rulemma.Lemmatizer()
lemmatizer.load()

tokenizer = rutokenizer.Tokenizer()
tokenizer.load()

tagger = rupostagger.RuPosTagger()
tagger.load()

# перевод цифр прописью в арабские
numbers_dict = {
	"первый": '1',
	"второй": '2',
	"третий": '3',
	"четвертый": '4',
	"пятый": '5',
	"шестой": '6',
	"седьмой": '7',
	"восьмой": '8',
	"девятый": '9',
	"десятый": '10',
	"двадцатый": '20',
	"двадцать": '20',
	"тридцатый": '30',
	"тридцать": '30'
}

i = 11
for j in ['один', 'две', 'три', 'четыр', 'пят', 'шест', 'сем', 'восем', 'девят']:
	numbers_dict[j+"надцатый"] = i
	i+=1

# список стран
with open('countries.txt', 'r', encoding='utf-8') as countries_file:
	countries_list_raw = countries_file.read().split('\n')
	countries_list = []
	for i in countries_list_raw:
		country = i.split('\t')
		countries_list.append(country[0].lower())



def lemmatize(string):

	# токенизируем, лемматизируем
	tokens = tokenizer.tokenize(string)
	tags = tagger.tag(tokens)
	lemmas = lemmatizer.lemmatize(tags)

	# избавляемся от ненужной пока инфы
	lemmatized = [i[2] for i in lemmas]

	# переводим цифры прописью в арабские
	lemmatized = [numbers_dict[i] if i in numbers_dict.keys() else i for i in lemmatized]

	# соединяем цифры
	i = 0
	lem_l = len(lemmatized)-1
	while i <= lem_l:
		if i == lem_l:
			pass
		else:
			if lemmatized[i].isdigit() and lemmatized[i+1].isdigit():
				lemmatized[i] = str(int(lemmatized[i])+int(lemmatized[i+1]))
				del lemmatized[i+1]
				lem_l -= 1
		i += 1
	return lemmatized

def get_countries(lemmatized):

	# ищем страны по совпадению со списком
	found_countries = []
	for i in lemmatized:
		if i in countries_list:
			found_countries.append(i)
	return found_countries

def get_dates(lemmatized):
	# ищем даты, которые может распарсить dateparse окном в два токена
	found_dates = []

	i = 0
	lem_l = len(lemmatized) - 1
	while i <= lem_l:
		if i == lem_l:
			date = dateparser.parse(lemmatized[i])
		else:
			pair = " ".join([lemmatized[i], lemmatized[i + 1]])
			date = dateparser.parse(pair)
		if date: found_dates.append(date)
		i += 1

	# если дат все еще нет, пытаемся распарсить по одному
	if len(found_dates) == 0:
		for i in lemmatized:
			date = dateparser.parse(i)
			if date: found_dates.append(date)
	return None if len(found_dates) == 0 else found_dates

string = "покажи мне информацию по России двадцать четвертого апреля"
print(lemmatize(string))