import matplotlib.pyplot as plt
from wordcloud import WordCloud


wc = WordCloud(background_color="white")
d = {}
d['word'] = 1.2
d['cross'] = 0.3
d['me'] = 5.0
print(d)
wc.generate_from_frequencies(d)
plt.imshow(wc, interpolation="bilinear")
plt.axis("off")
plt.show()

