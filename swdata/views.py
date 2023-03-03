from django.views.generic.base import View
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.generic.list import ListView
from django.views.generic import TemplateView
from django.shortcuts import redirect

from .models import FileMetadata
from datetime import datetime
import requests
import petl as etl
import string
import random
import json


# View for fetching new data and saving it in the csv
class FileFetchView(View):
    # Function turning planet endpoint to planet name
    def endpoint_to_planet(self, endpoint, planets):
        endpoint = endpoint[:-1]
        number = int(endpoint.rsplit('/', 1)[1])

        return planets[number][0]

    # Function fetching all resource from given endpoint
    def get_all_resources(self, url):
        next = True
        data = []

        while next:
            response = requests.get(url)
            json_res = response.json()
            data += response.json().get('results')

            if bool(json_res['next']):
                url = json_res['next']
            else:
                next = False

        return data
    
    def parse_date(self, date):
        date = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S.%fZ')
        return date.strftime('%Y-%m-%d')

    # Running this view as async can provide substantial improvement in time.
    # I tested this solution (It was around 1.5 seconds faster then current implementation):
    #   async def get_all_resources(...):
    #   ...
    #       async with httpx.AsyncClient() as client:
    #           response = await client.get(url)
    #           json_res = response.json()
    #   ...
    #   
    #   async def get(...):
    #       response_p, response_r = await asyncio.gather(
    #           self.get_all_resources('https://swapi.dev/api/people/'),
    #           self.get_all_resources('https://swapi.dev/api/planets')
    #       )
    #   ...
    # It required running development ASGI server (I used daphne), instead of WSGI.
    # Another option to improve performance is to use task queue like Celery.
    # I left simplest synchronous implementation to not use different dependencies/servers.

    def get(self, request, *args, **kwargs):
        people = self.get_all_resources('https://swapi.dev/api/people/')
        people = etl.fromdicts(people)
        people = etl.cutout(people, 'films', 'species', 
                            'vehicles', 'created', 'url', 'starships')

        # Fetching all planets is much more efficient then resolving single endpoints.
        planets = self.get_all_resources('https://swapi.dev/api/planets')
        planets = etl.fromdicts(planets)

        people = etl.convert(people, 'homeworld', 
                             lambda planet : self.endpoint_to_planet(planet, planets))
        people = etl.rename(people, 'edited', 'date')
        people = etl.convert(people, 'date', 
                             lambda date : self.parse_date(date))

        file = FileMetadata.objects.create()
        file.name = ''.join(random.choices(string.ascii_uppercase +
                            string.digits, k=20))
        file.save()
        etl.tocsv(people, 'csv/{}.csv'.format(file.name))

        return redirect('file-list')


# View rendering template with file list
class FileListView(ListView):
    model = FileMetadata
    template_name = "swdata/files.html"

    def get_queryset(self):
        queryset = FileMetadata.objects.all().order_by('-date')
        return queryset


# View rendering template with detailed file data
class PeopleView(TemplateView):
    template_name = "swdata/people.html"

    def get_context_data(self, file, **kwargs):
        context = super().get_context_data(**kwargs)
        context['headers'] = etl.fromcsv('csv/{}.csv'.format(file))[0]
        context['filename'] = file
        return context


# View parsing and returning given part of csv file
class PeopleLoadView(View):
    def get(self, request, file, *args, **kwargs):
        beg = int(request.GET.get('beg', 0))
        end = int(request.GET.get('end', 0))

        if end <= beg:
            return JsonResponse({'message': "wrong parameters"}, status=400) 

        data = etl.fromcsv('csv/{}.csv'.format(file))
        data_part = list(etl.data(data))[beg:end]

        return JsonResponse({ 'data': json.dumps(data_part), 'max_size': len(data) })


# View rendering template with counting functionality
class CountView(TemplateView):
    template_name = "swdata/people_count.html"

    def get_context_data(self, file, **kwargs):
        context = super().get_context_data(**kwargs)
        context['headers'] = etl.fromcsv('csv/{}.csv'.format(file))[0]
        context['filename'] = file
        return context


# View with implemented counting functionality
class CountLoadView(View):
    def count_distinct(self, key, rows):
        if type(key) == tuple:
            key_arr = [e for e in key ]
        else: 
            key_arr = [key]

        return key_arr + [len(list(rows))]

    def get(self, request, file, *args, **kwargs):
        params = request.GET.get("params")

        if params is None:
            return JsonResponse({'message': "wrong parameters"}, status=400) 

        params_array = params.split(',')

        data = etl.fromcsv('csv/{}.csv'.format(file))
        data_count = etl.rowreduce(data, key=params_array, reducer=self.count_distinct,
                                    header=params_array)

        json_header = json.dumps(list(data_count[0]) + ['count'])
        json_data = json.dumps(list(data_count[1:]))

        return JsonResponse({ 'data': json_data, 'header': json_header })