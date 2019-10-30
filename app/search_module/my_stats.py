def get_my_youtube():

        my_criteria = YOUTUBE.playlistItems().list(
          mine=True, 
          maxResults=50
          ).execute()

        return my_youtube


def crunch_my_numbers(videoId):


    video_stats = YOUTUBE.videos().list(id=videoId, 
            part='snippet, recordingDetails, statistics'
            ).execute()

    try:
        like_count = video_stats['items'][0]['statistics']['likeCount']
        dislike_count = video_stats['items'][0]['statistics']['dislikeCount']
        comment_count = video_stats['items'][0]['statistics']['commentCount']
        view_count = video_stats['items'][0]['statistics']['likeCount']
        total_count = like_count + dislike_count
        
    except KeyError:
        print("KeyError: A stat is not accessable.")
        return False
    
    my_video_stats = [like_count, dislike_count, comment_count, view_count, total_count]
    return my_video_stats


        
for playlist in my_youtube.get('items', []):
    for video in playlist:
        videoId = video['id']['videoId']
        my_numbers = crunch_my_numbers(videoid)
        
        my_like = int(redis_server.get('MY_LIKE').decode('utf-8')) + my_numbers[0]
        redis_server.set('MY_LIKE', my_like)

        my_dislike = int(redis_server.get('MY_DISLIKE').decode('utf-8')) + my_numbers[1]
        redis_server.set('MY_DISLIKE', my_dislike)

        my_comments = int(redis_server.get('MY_COMMENTS').decode('utf-8')) + my_numbers[2]
        redis_server.set('MY_COMMENTS', my_comments)

        my_view_count = int(redis_server.get('MY_VIEW_COUNT').decode('utf-8')) + my_numbers[3]
        redis_server.set('MY_VIEW_COUNT', my_view_count)

        my_total_count = int(redis_server.get('MY_TOTAL_COUNT').decode('utf-8')) + my_numbers[4]
        redis_server.set('MY_TOTAL_COUNT', my_total_count)

    my_like_ratio = int(redis_server.get('MY_DISLIKE').decode('utf-8')) / int(redis_server.get('MY_LIKE').decode('utf-8'))
