import os
from django.conf import settings
from django.shortcuts import render
from django.utils.translation import get_language
from django.http import JsonResponse
from google.cloud import bigquery
from datetime import datetime, timedelta
import logging
import json
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import ensure_csrf_cookie

logger = logging.getLogger(__name__)

def index(request):
    logger.info('Index view called')
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

@require_http_methods(["POST"])
@ensure_csrf_cookie
def search_words(request):
    logger.info('Search view called')
    try:
        logger.info('Received search request')
        logger.debug(f'Request method: {request.method}')
        logger.debug(f'Content-Type: {request.headers.get("Content-Type")}')
        logger.debug(f'Accept: {request.headers.get("Accept")}')
        logger.debug(f'Request body: {request.body.decode()}')
        logger.debug(f'GOOGLE_APPLICATION_CREDENTIALS: {os.getenv("GOOGLE_APPLICATION_CREDENTIALS")}')
        
        # Ensure we're dealing with JSON
        if not request.headers.get('Content-Type', '').startswith('application/json'):
            logger.error('Invalid Content-Type')
            return JsonResponse(
                {'error': 'Content-Type must be application/json'}, 
                status=400
            )

        try:
            data = json.loads(request.body)
            search_term = data.get('searchTerm', '').strip()
            logger.info(f'Got search term from JSON: {search_term}')
        except json.JSONDecodeError as e:
            logger.error(f'JSON decode error: {str(e)}')
            return JsonResponse(
                {'error': 'Invalid JSON format'}, 
                status=400
            )
        
        if not search_term:
            logger.warning('Empty search term')
            return JsonResponse([], safe=False)

        try:
            client = bigquery.Client(project="usavm-334506")
            logger.info('BigQuery client created successfully')
        except Exception as e:
            logger.error(f'Error creating BigQuery client: {str(e)}', exc_info=True)
            return JsonResponse(
                {'error': 'Failed to initialize BigQuery client'}, 
                status=500
            )

        # Create a list of words from the search term
        search_words = search_term.lower().split()
        logger.debug(f'Search words: {search_words}')
        
        # Create conditions for each word
        word_conditions = []
        for word in search_words:
            word_conditions.append(f"STRPOS(LOWER(transcript_text), LOWER('{word}')) > 0")
        
        word_condition = ' AND '.join(word_conditions)
        logger.debug(f'Word condition: {word_condition}')
        
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
        logger.debug(f'Query: {query}')

        try:
            query_job = client.query(query)
            results = [dict(row) for row in query_job]
            logger.info(f'Query executed successfully, found {len(results)} results')
        except Exception as e:
            logger.error(f'Error executing BigQuery query: {str(e)}', exc_info=True)
            return JsonResponse(
                {'error': 'Failed to execute search query'}, 
                status=500
            )

        # Convert dates to string format for JSON serialization
        for row in results:
            row['date'] = row['date'].isoformat()

        logger.info(f'Found {len(results)} results')
        logger.debug(f'First result: {results[0] if results else None}')
        
        response = JsonResponse(results, safe=False)
        response['Content-Type'] = 'application/json'
        logger.debug(f'Response headers: {dict(response.items())}')
        return response

    except Exception as e:
        logger.error(f'Error in search_words: {str(e)}', exc_info=True)
        return JsonResponse(
            {'error': str(e)}, 
            status=500, 
            content_type='application/json'
        )
