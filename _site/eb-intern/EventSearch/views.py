from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import requests

def getCategoryList(request):
    '''
    Retrieves category listing via eventbrite api, builds a mapping of category id to category name into
    the user's session.
    :return: a list of categories in JSON format.
    '''
    # request each of the categories via the eventbrite api
    raw_response = requests.get("https://www.eventbriteapi.com/v3/categories", params={'token': 'BKKRDKVUVRC5WG4HAVLT'})

    # decode the response in JSON
    response = raw_response.json()

    # build the dictionary for mapping id to category name in user session
    request.session['categories'] = {cat['id']: cat['name'] for cat in response['categories']}

    # return the categories list
    return response['categories']


def getEventList(**args):
    '''
    Retrieves event listing via eventbrite api and returns event list. If optional argument 'filter' supplied, only
    events that match a category id in 'filter' argument will be returned.
    :param **args: optional argument 'filter' - a list of category ids.
    :return: a list of events in JSON format
    '''
    # request the event listing via the eventbrite api
    raw_response = requests.get("https://www.eventbriteapi.com/v3/events", params={'token': 'BKKRDKVUVRC5WG4HAVLT'})

    # decode the response in JSON
    response = raw_response.json()

    # check for the filter argument
    if 'filter' in args:
        # get the relevant ids
        rel_ids = args['filter']

         # filter relevant events in the response by category id and return as a list
        return [event for id in rel_ids for event in response['events'] if id == event['category_id']]

    # otherwise, return a list of all events
    return response['events']


def index(request):
    '''
    Renders the homepage of the application with all available categories.

    :param      request: an http/https request.
    :return:    the rendered homepage with a listing of categories.
    '''

    # delete prior rel_events session variable if it exists
    if 'rel_events' in request.session:
        del request.session['rel_events']

    # delete prior all_events session variable if it exists
    if 'all_events' in request.session:
        del request.session['all_events']

    # delete prior categories session variable if it exists
    if 'categories' in request.session:
        del request.session['categories']

    # build and store dictionary for mapping id to category name in user session
    categories = getCategoryList(request)

    # render the homepage with a listing of the retrieved categories
    return render(request, 'EventSearch/index.html', {'categories': categories})


def display_events(request):
    # verify the presence of any category selections
    if any(cat in request.GET for cat in ('cat1', 'cat2', 'cat3')):
        # View triggered with category selections
        # (example: eventbrite.com/events/?cat1=103&cat2=101&cat3=110)

        # verify that each category selection exists
        if not 'cat1' in request.GET or not 'cat2' in request.GET or not 'cat3' in request.GET:
            return render(request, 'EventSearch/index.html', {'categories': request.session['categories'],
                                                              'form_error': 'Error: You must select 3 categories.'})

        # make a list of the relevant category ids
        rel_ids = [request.GET['cat1'], request.GET['cat2'], request.GET['cat3']]

        # verify that each category selection is unique
        if len(rel_ids) != len(set(rel_ids)):
            return render(request, 'EventSearch/index.html', {'categories': request.session['categories'],
                                                              'form_error': 'Error: Selections must be unique.'})

        # verify that each category exists in the categories session variable
        if not all(cat in request.session['categories'] for cat in rel_ids):
            # retrieve updated listing
            categories = getCategoryList(request)

            return render(request, 'EventSearch/index.html', {'categories': categories,
                                                              'form_error': 'Error: One or more of the selected '
                                                                            'categories no longer exists.'})

        # if a rel_events session variable exists, retrieve the relevant events via API
        if not 'rel_events' in request.session:
            # get and store the filtered list in the user's session
            request.session['rel_events'] = getEventList(filter=rel_ids)

        # get the specified page number
        page = request.GET.get('page')

        # set-up the paginator to display 5 relevant events per page
        paginator = Paginator(request.session['rel_events'], 5)

        # try to paginate the list of relevant events
        try:
            rel_events = paginator.page(page)
        except PageNotAnInteger:
            # if the specified page number isn't a number, render the first page.
            rel_events = paginator.page(1)
        except EmptyPage:
            # if the specified page number is out of range, render last page.
            rel_events = paginator.page(paginator.num_pages)

        # render with the relevant events with the names and ids of the categories
        return render(request, 'EventSearch/results.html', {'events': rel_events,
                                                            'event_count': paginator.count,
                                                            'cat1_name': request.session['categories'][rel_ids[0]],
                                                            'cat2_name': request.session['categories'][rel_ids[1]],
                                                            'cat3_name': request.session['categories'][rel_ids[2]],
                                                            'cat1_id': rel_ids[0],
                                                            'cat2_id': rel_ids[1],
                                                            'cat3_id': rel_ids[2]})

    else:
        # View triggered by direct URL access
        # (example: eventbrite.com/events)

        # retrieve events, if all_events session variable doesn't exist
        if not 'all_events' in request.session:
            request.session['all_events'] = getEventList()

        # set-up the paginator to display 5 events per page
        paginator = Paginator(request.session['all_events'], 5)

        # get the specified page number
        page = request.GET.get('page')

        # try to paginate the list of relevant events
        try:
            all_events = paginator.page(page)
        except PageNotAnInteger:
            # if the specified page number isn't a number, render the first page.
            all_events = paginator.page(1)
        except EmptyPage:
            # if the specified page number is out of range, render last page.
            all_events = paginator.page(paginator.num_pages)

        # render with all events
        return render(request, 'EventSearch/results.html', {'events': all_events,
                                                            'event_count': paginator.count})