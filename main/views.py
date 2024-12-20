import os
from django.conf import settings
from django.shortcuts import render
from django.utils.translation import get_language
from django.http import JsonResponse
from google.cloud import bigquery
from datetime import datetime, timedelta
import logging
import json

def index(request):
    current_language = get_language()
    base_dir = os.path.join(settings.BASE_DIR, 'main')
    file_path = os.path.join(base_dir, f'description_{current_language}.txt')
    file_path2 = os.path.join(base_dir, f'links_{current_language}.txt')
    file_path3 = os.path.join(base_dir, f'ds_{current_language}.txt')

    with open(file_path, 'r', encoding='utf-8') as file:
        description = file.read()

    with open(file_path2, 'r', encoding='utf-8') as file2:
        links = file2.read()
    
    with open(file_path3, 'r', encoding='utf-8') as file3:
        ds = file3.read()
    
    context = {'description': description, 'links': links, 'ds': ds}
    return render(request, 'main/index.html', context)

def search_words(request):
    logger = logging.getLogger(__name__)
    try:
        logger.info('Received search request')
        logger.debug(f'Request method: {request.method}')
        logger.debug(f'Request headers: {request.headers}')
        logger.debug(f'Request body: {request.body}')
        
        if request.method != 'POST':
            logger.warning(f'Invalid method: {request.method}')
            return JsonResponse({'error': 'Method not allowed'}, status=405)
        
        # Try both JSON and form data
        try:
            data = json.loads(request.body)
            search_term = data.get('searchTerm', '').strip()
            logger.info(f'Got search term from JSON: {search_term}')
        except json.JSONDecodeError:
            search_term = request.POST.get('searchTerm', '').strip()
            logger.info(f'Got search term from POST: {search_term}')
        
        if not search_term:
            logger.warning('Empty search term')
            return JsonResponse([])

        # Create a list of words from the search term
        search_words = search_term.lower().split()
        
        # Create conditions for each word
        word_conditions = []
        for word in search_words:
            word_conditions.append(f"STRPOS(LOWER(transcript_text), LOWER('{word}')) > 0")
        
        word_condition = ' AND '.join(word_conditions)
        
        # Calculate date range (last 30 days)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)

        query = f"""
        WITH WordCounts AS (
            SELECT
                channel,
                DATE(timestamp) as date,
                COUNT(*) as occurrences
            FROM `usavm-334506.rtlm.channel_transcripts`
            WHERE 
                DATE(timestamp) BETWEEN '{start_date.date()}' AND '{end_date.date()}'
                AND {word_condition}
            GROUP BY channel, DATE(timestamp)
        )
        SELECT
            date,
            IFNULL(MAX(CASE WHEN channel = 'ORT' THEN occurrences END), 0) as ORT,
            IFNULL(MAX(CASE WHEN channel = 'belarusone' THEN occurrences END), 0) as belarusone,
            IFNULL(MAX(CASE WHEN channel = 'oneplusone' THEN occurrences END), 0) as oneplusone,
            IFNULL(MAX(CASE WHEN channel = 'russiaone' THEN occurrences END), 0) as russiaone
        FROM WordCounts
        GROUP BY date
        ORDER BY date
        """

        client = bigquery.Client(project="usavm-334506")
        query_job = client.query(query)
        results = [dict(row) for row in query_job]
        
        # Convert dates to string format for JSON serialization
        for row in results:
            row['date'] = row['date'].isoformat()

        logger.info(f'Found {len(results)} results')
        logger.debug(f'First result: {results[0] if results else None}')
        
        return JsonResponse(results, safe=False)

    except Exception as e:
        logger.error(f'Error in search_words: {str(e)}', exc_info=True)
        return JsonResponse({'error': str(e)}, status=500)
