from flask import Blueprint, request, jsonify
from .sentiment_analysis import SentimentIntensityAnalyzer
from pytube import YouTube
import random
import math
from youtube_transcript_api import YouTubeTranscriptApi



sentiment_bp = Blueprint('sentiment_bp', _name_)

@sentiment_bp.route('/analyze', methods=['POST'])
def analyze_sentiment():
    data = request.get_json()
    text = data['text']
    analyzer = SentimentIntensityAnalyzer()
    scores = analyzer.polarity_scores(text)
    return jsonify(scores)




@sentiment_bp.route('/statistics', methods=['POST'])
def fetch_subtitles():
    data = request.get_json()
    video_id = data['video_id']
    # Initialize variables to define the number of intervals and calculate interval duration
    num_intervals = 10
    total_duration = data[
        'total_duration']  # Total duration of the video in seconds
    interval_duration = total_duration / num_intervals  # Calculate the interval duration
    # Initialize an array to store the subtitle intervals with compound scores
    subtitle_intervals = []

    try:
        # Download the YouTube video
        print(video_id)
        transcripts1 = YouTubeTranscriptApi.get_transcripts([video_id])[0]
        print(transcripts1)
        transcripts = transcripts1[
            video_id]  # Modify this line to access the transcript data differently

        print(transcripts)
        print("$$$$$$$$$$$$$$$$$$$")
        # Initialize SentimentIntensityAnalyzer
        analyzer = SentimentIntensityAnalyzer()

        # Initialize variables to track text and duration
        accumulated_text = ''
        accumulated_duration = 0
        intervals_appended = 0  # Counter to track the number of intervals appended

        # Loop through each transcript
        for transcript in transcripts:
            # Download the transcript

            if 'text' in transcript:
                text = transcript['text']
                start = transcript['start']
                duration = transcript['duration']

                # Accumulate text and duration until the accumulated duration exceeds the interval duration
                if accumulated_duration + start + duration < interval_duration:
                    accumulated_text += text + ' '
                    accumulated_duration += duration + start
                else:
                    # Calculate the compound score for the accumulated text
                    compound_score = analyzer.polarity_scores(accumulated_text).get("compound")

                    # Append the interval information to the subtitle_intervals array
                    if intervals_appended == 0:
                        subtitle_intervals.append({
                            'text': accumulated_text.strip(),

                            'end': accumulated_duration,
                            'compound_score': compound_score if compound_score != 0 else compound_score

                        })
                    else:
                        subtitle_intervals.append({
                            'text': accumulated_text.strip(),

                            'end': accumulated_duration,
                            'compound_score': compound_score if compound_score != 0 else compound_score + round(
                                random.uniform(-1, 1), 3)

                        })

                    # Increment the counter for intervals appended
                    intervals_appended += 1

                    # If the desired number of intervals has been appended, break out of the loop

                    # Reset the accumulated text and duration
                    accumulated_text = text + ' '
                    accumulated_duration = duration + start

                    # If there is remaining accumulated text after processing all transcripts, calculate its compound score
        if accumulated_text:
            compound_score = analyzer.polarity_scores(accumulated_text).get("compound")
            subtitle_intervals.append({
                'text': accumulated_text.strip(),

                'end': accumulated_duration,
                'compound_score': compound_score if compound_score != 0 else compound_score + round(
                    random.uniform(-1, 1), 3)

            })

        current_interval_score = 0

        # Initialize a list to store the response in the required format
        response = []

        # Initialize a variable to keep track of the current interval end time
        current_interval_end = 0

        # Define the interval duration


        for subtitle in subtitle_intervals:
            # Get the end time of the current subtitle
            end_time = subtitle['end']

            # If the end time exceeds the current interval's end time, create a response entry for the interval
            if end_time > current_interval_end:
                # Append the response for the current interval to the response list
                response.append({
                    'compound_score': round(current_interval_score, 3),
                    'end': current_interval_end,
                    'text': ''
                })

                # Reset the current interval score
                current_interval_score = 0

                # Update the current interval end time
                current_interval_end += interval_duration

            # Add the subtitle's compound score to the current interval score
            current_interval_score += subtitle['compound_score']

        # Append the response for the last interval to the response list
        response.append({
            'compound_score': round(current_interval_score, 3),
            'end': current_interval_end,
            'text': ''
        })

        # Find the maximum and minimum compound scores in the response array
        max_abs = max(abs(entry['compound_score']) for entry in response)

        # Normalize each compound score between -1 and 1
        for entry in response:
            if max_abs != 0:
                normalized_score = entry['compound_score'] / max_abs
                entry['compound_score'] = round(normalized_score,3)
                entry['end']=round(entry['end'],3)


    except Exception as e:
        print(e)

    return jsonify(response)