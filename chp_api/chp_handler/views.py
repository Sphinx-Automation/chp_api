import os
import time
import multiprocessing
from django.shortcuts import render
from .apps import ChpHandlerConfig

# Create your views here.
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from chp.reasoner_std import ReasonerStdHandler

#-- Get Hosts File if it exists
parent_dir = os.path.dirname(os.path.realpath(__file__))
HOSTS_FILENAME = os.path.join(parent_dir, 'hosts')
NUM_PROCESSES_PER_HOST = multiprocessing.cpu_count()
#if not os.path.exists(HOSTS_FILENAME):
HOSTS_FILENAME = None
NUM_PROCESSES_PER_HOST = 0


#import the transaction model so that we may store queries and responses
from chp_handler.models import Transaction

class submit_query(APIView):

    def post(self, request):
        if request.method == 'POST':
            start_time = time.time()
            data = request.data

            query = data['message']
            if 'reasoner_id' in query.keys():
                source_ara = query['reasoner_id']
            else:
	        source_ara = 'default'

            print('Processing query from: {}'.format(source_ara))

            handler = ReasonerStdHandler(source_ara,
                                         dict_query=query,
                                         hosts_filename=HOSTS_FILENAME,
                                         num_processes_per_host=NUM_PROCESSES_PER_HOST)
            handler.buildChpQueries()
            print('Built Queries.')
            handler.runChpQueries()
            print('Completed Reasoning.')
            print('Total Time: {}'.format(time.time() - start_time))

            response = handler.constructDecoratedKG()

            #Store the transaction in mongodb
            transaction = Transaction()
            transaction.source_ara = source_ara
            transaction.query = query
            transaction.response = response

            transaction.save()

            return JsonResponse(response)

class check_query(APIView):

    def post(self, request):
        if request.method == 'POST':
            data = request.data

            query = data['query']
            source_ara = query['reasoner_id']

            handler = ReasonerStdHandler(source_ara, dict_query=query)

            return JsonResponse(handler.checkQuery())

class get_supported_node_types(APIView):
    
    def get(self, request):
        if requests.method == 'GET':
            return JsonResponse(None)

class get_supported_edge_types(APIView):
    
    def get(self, request):
        if requests.method == 'GET':
            predicate_map = {
                              'gene' : { 
                                         'disease' : ['gene_to_disease_association']
                                       }
                              'drug' : {
                                         'disease' : ['chemical_to_disease_or_phenotypic_feature_association']
                                       }
                              'disease' : {
                                            'phenotypicfeature' : ['disease_to_phenotypic_association']
                                          }
                            }
            return JsonResponse(predicate_map)
