from django.shortcuts import render, redirect
import heapq
from spacy.lang.en.stop_words import STOP_WORDS
import en_core_web_sm
from django.http import JsonResponse
import re
import time
import subprocess
import whisper
import os
from .models import AudioFile, Audio_File_Data
from autocorrect import Speller
import nltk
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout

client_id = "1042742414542-i1k8c8vn0eebaoab42qf8tnmf58jnee8.apps.googleusercontent.com"

# from transformers import pipeline
# Create your views here.
def login(request):
    return render(request, 'login.html')

@login_required
def extract_main_points(request):
    print('function call')
    if request.method == 'POST':
        text = request.POST.get('query')
        # print(text)
        print(len(text))
        text = f'''{text}'''
        stopwords = list(STOP_WORDS)
        nlp = en_core_web_sm.load()
        docx = nlp(text)
        # for token in docx:
        #     print(token.text)
        word_frequencies = {}
        for word in docx:
            if word.text not in stopwords:
                if word.text not in word_frequencies.keys():
                    word_frequencies[word.text] = 1
                else:
                    word_frequencies[word.text] += 1
        maximum_frequency = max(word_frequencies.values())
        for word in word_frequencies.keys():
            word_frequencies[word] = (word_frequencies[word]/maximum_frequency)
        sentence_list = [sentence for sentence in docx.sents]
        sentence_scores = {}
        for sent in sentence_list:
            for word in sent:
                if word.text.lower() in word_frequencies.keys():
                    if len(sent.text.split(' ')) < 30:
                        if sent not in sentence_scores.keys():
                            sentence_scores[sent] = word_frequencies[word.text.lower()]
                        else:
                            sentence_scores[sent] += word_frequencies[word.text.lower()]
        summarized_sentences = heapq.nlargest(7, sentence_scores, key=sentence_scores.get)
        # for i in summarized_sentences:
        #     print(i)
        final_sentences = [w.text for w in summarized_sentences]
        summary = ' '.join(final_sentences)
        sentences = re.split(r'(?<=[.!?])\s', summary)
        print(sentences)
        return render(request, 'extract.html', {'summary':sentences})
    
    return render(request, 'extract.html')


@login_required
def Extract_points_from_recordings(request):
    
    if request.method == 'POST':
        audio_file = request.FILES.get('file')
        print(audio_file)
        time.sleep(3)
        new_file = AudioFile(audio_file=audio_file)
        new_file.save()
        data = Audio_File_Data(file_name=audio_file.name, user=request.user)
        data.save()
        text = transcribe_audio(audio_file.name)
        print(text)
        new_file.delete()
        try:
            
            text = f'''{text}'''
            # print("text: ", text)
            stopwords = list(STOP_WORDS)
            nlp = en_core_web_sm.load()
            docx = nlp(text)
            # print()
            # print("docx: ", docx)
            word_frequencies = {}
            for word in docx:
                if word.text not in stopwords:
                    if word.text not in word_frequencies.keys():
                        word_frequencies[word.text] = 1
                    else:
                        word_frequencies[word.text] += 1
            # print()
            # print("word frequencies: ", word_frequencies)
            maximum_frequency = max(word_frequencies.values())
            # print()
            # print("max frequency: ", maximum_frequency)
            for word in word_frequencies.keys():
                word_frequencies[word] = (word_frequencies[word]/maximum_frequency)
            # print()
            # print("word frequencies: ", word_frequencies)
            sentence_list = [sentence for sentence in docx.sents]
            # print()
            # print("sentence list ", sentence_list)
            sentence_scores = {}
            for sent in sentence_list:
                # print(len(sent.text.split(' ')))
                for word in sent:
                    if word.text.lower() in word_frequencies.keys():
                        if len(sent.text.split(' ')) < 35:
                            if sent not in sentence_scores.keys():
                                sentence_scores[sent] = word_frequencies[word.text.lower()]
                            else:
                                sentence_scores[sent] += word_frequencies[word.text.lower()]
            # print()
            # print("sentence scores: ", sentence_scores)
            size = int(len(sentence_list)*0.4)
            summarized_sentences = heapq.nlargest(size, sentence_scores, key=sentence_scores.get)
            
            # for i in summarized_sentences:
            #     print(i)
            final_sentences = [w.text for w in summarized_sentences]
            print("final_sentences: ", final_sentences)
            summary = ' '.join(final_sentences)
            print()
            print("summary: ", summary)
            sentences = re.split(r'(?<=[.!?])\s', summary)
            print(sentences)
            data.main_points = summary
            data.save()
            return render(request, 'extract.html', {'sentences':sentences})
        
        except Exception as e:
            print(e)
    
    return render(request, 'extract.html')





def generatewav():
    wavfilename = "output4.mp4"
    import pyttsx3 as tts
    engine = tts.init()
    engine.save_to_file(
        '''Cricket is a bat-and-ball game played between two teams of eleven players on a field at the centre of which is a 22-yard (20-metre) pitch with a wicket at each end, each comprising two bails balanced on three stumps. The batting side scores runs by striking the ball bowled at one of the wickets with the bat and then running between the wickets, while the bowling and fielding side tries to prevent this (by preventing the ball from leaving the field, and getting the ball to either wicket) and dismiss each batter (so they are "out"). Means of dismissal include being bowled, when the ball hits the stumps and dislodges the bails, and by the fielding side either catching the ball after it is hit by the bat, but before it hits the ground, or hitting a wicket with the ball before a batter can cross the crease in front of the wicket. When ten batters have been dismissed, the innings ends and the teams swap roles. The game is adjudicated by two umpires, aided by a third umpire and match referee in international matches. They communicate with two off-field scorers who record the match's statistical information.

Forms of cricket range from Twenty20 (also known as T20), with each team batting for a single innings of 20 overs (each "over" being a set of 6 fair opportunities for the batting team to score) and the game generally lasting three to four hours, to Test matches played over five days. Traditionally cricketers play in all-white kit, but in limited overs cricket they wear club or team colours. In addition to the basic kit, some players wear protective gear to prevent injury caused by the ball, which is a hard, solid spheroid made of compressed leather with a slightly raised sewn seam enclosing a cork core layered with tightly wound string.

The earliest reference to cricket is in South East England in the mid-16th century. It spread globally with the expansion of the British Empire, with the first international matches in the second half of the 19th century. The game's governing body is the International Cricket Council (ICC), which has over 100 members, twelve of which are full members who play Test matches. The game's rules, the Laws of Cricket, are maintained by Marylebone Cricket Club (MCC) in London. The sport is followed primarily in South Asia, Australia, New Zealand, the United Kingdom, Southern Africa and the West Indies.[1]

Women's cricket, which is organised and played separately, has also achieved international standard.

The most successful side playing international cricket is Australia, which has won seven One Day International trophies, including five World Cups, more than any other country and has been the top-rated Test side more than any other country.''',
        wavfilename
    )
    engine.runAndWait()


# generatewav()
@login_required
def Extract_points_from_meetings(request):
    if request.method == 'POST':
        text = request.POST.get('query')
        print(text)
        if text != '':
            # print(text)
            # print(len(text))
            
            text = f'''{text}'''
            # print(text)
            stopwords = list(STOP_WORDS)
            nlp = en_core_web_sm.load()
            docx = nlp(text)
            
            word_frequencies = {}
            for word in docx:
                if word.text not in stopwords:
                    if word.text not in word_frequencies.keys():
                        word_frequencies[word.text] = 1
                    else:
                        word_frequencies[word.text] += 1
            # print()
            # print("word frequency: ", word_frequencies)
            maximum_frequency = max(word_frequencies.values())
            # print()
            # print("maximum frequency: ", maximum_frequency)
            for word in word_frequencies.keys():
                word_frequencies[word] = (word_frequencies[word]/maximum_frequency)
            # print()
            # print("word frequency: ", word_frequencies)
            sentence_list = [sentence for sentence in docx.sents]
            # print()
            # print("sentence list: ", sentence_list)
            sentence_scores = {}
            for sent in sentence_list:
                # print(len(sent.text.split(' ')))
                for word in sent:
                    if word.text.lower() in word_frequencies.keys():
                        if len(sent.text.split(' ')) < 30:
                            if sent not in sentence_scores.keys():
                                sentence_scores[sent] = word_frequencies[word.text.lower()]
                            else:
                                sentence_scores[sent] += word_frequencies[word.text.lower()]
            # print()
            # print("sentence scores: ", sentence_scores)
            summarized_sentences = heapq.nlargest(7, sentence_scores, key=sentence_scores.get)
            # print()
            # print("summarize sentences: ", summarized_sentences)
            final_sentences = [w for w in summarized_sentences]
            # print()
            # print("final sentences: ", final_sentences)
            summary = ' '.join(map(str, final_sentences))
            print()
            print("summary: ",summary)
            sentences = re.split(r'(?<=[.!?])\s', summary)
            print(sentences)
            return JsonResponse(sentences, safe=False)
    else:
        return render(request, 'extract.html')

@login_required
def all_files(request):
    all_files = Audio_File_Data.objects.filter(user=request.user)
    return render(request, 'all_files.html', {'all_files':all_files})

@login_required
def show_points(request, id):
    points = Audio_File_Data.objects.get(id=id)
    sentences = points.main_points
    print(sentences)
    summary = ''.join(map(str, sentences))
    print(summary)
    sentences = nltk.sent_tokenize(summary)
    print(sentences)
    return render(request, 'points.html', {'sentences':sentences})

@login_required
def delete_file(request, id):
    file = Audio_File_Data.objects.get(id=id)
    file.delete()
    return redirect('audio_files')

def transcribe_audio(filename):
        
        print(filename)
        if filename.endswith('.mp4') or filename.endswith('.mkv'):
            file = f"{filename}"
            location = r"C:\Users\shree\Desktop\projects\Summarization_project\Point_Extraction\media\audio_files"
            mp4_path = os.path.join(location, file)
            
            mp3_folder = r"C:\Users\shree\Desktop\projects\Summarization_project\Point_Extraction\mp3_files"
            mp3_file = "output.mp3"
            mp3_path = os.path.join(mp3_folder, mp3_file)
            
            command = ["ffmpeg", "-i", mp4_path, mp3_path]
            subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            print(f"Conversion from {mp4_path} to {mp3_file} complete.")
            os.remove(mp4_path)
            
            model = whisper.load_model("base")
            result = model.transcribe(mp3_path)
            text = result['text']
            text = auto_correct_text(text)
            print(text)
            
            os.remove(mp3_path)
            print(f"Deleted: {filename}")
            return text
        else:
            
            location = r"C:\Users\shree\Desktop\projects\Summarization_project\Point_Extraction\media\audio_files"
            mp3_path = os.path.join(location, filename)
            
            result = model.transcribe(mp3_path)
            text = result['text']
            return text

def auto_correct_text(text):
    spell = Speller(lang='en')
    corrected_text = spell(text)
    return corrected_text


def User_logout(request):
    logout(request)
    return redirect('user_login')

# summarizer = pipeline('summarization')
# article = '''Python is a high-level, general-purpose programming language. Its design philosophy emphasizes code readability with the use of significant indentation.[32]

#         Python is dynamically typed and garbage-collected. It supports multiple programming paradigms, including structured (particularly procedural), object-oriented and functional programming. It is often described as a "batteries included" language due to its comprehensive standard library.[33][34]

#         Guido van Rossum began working on Python in the late 1980s as a successor to the ABC programming language and first released it in 1991 as Python 0.9.0.[35] Python 2.0 was released in 2000. Python 3.0, released in 2008, was a major revision not completely backward-compatible with earlier versions. Python 2.7.18, released in 2020, was the last release of Python 2.[36]

#         Python consistently ranks as one of the most popular programming languages'''

# summary = summarizer(article, max_length=130, min_length=30, do_sample=False)
# print(summary)

