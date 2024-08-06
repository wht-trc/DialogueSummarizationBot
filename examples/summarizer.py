from transformers import pipeline

# Загрузка модели для суммаризации
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

# Пример текста для суммаризации
dialogue = """
Alex: Hey Jamie, do you have any plans for this weekend?
Jamie: Not yet! I was thinking about going hiking. What do you think?
Alex: That sounds great! Do you have a specific trail in mind?
Jamie: I was considering the Green Mountain Trail. It has some amazing views!
Alex: I’ve heard about that one! How long do you think it will take?
Jamie: It’s about a 5-mile hike, so maybe 3 to 4 hours including breaks.
Alex: Perfect! Should we pack some snacks and water?
Jamie: Definitely! I can bring some sandwiches and fruit. What about drinks?
Alex: I can bring some water bottles and maybe some juice.
Jamie: Awesome! Let’s meet at my place around 9 AM on Saturday?
Alex: Sounds good! I’m looking forward to it!
Jamie: Me too! It’s going to be fun! Feel free to ask if you need a different context or topic for the dialogue!
"""

# Суммаризация
summary = summarizer(dialogue, max_length=150, min_length=25, do_sample=False)
print("Summarization:", summary[0]['summary_text'])