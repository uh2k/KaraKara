from karakara.tests.conftest import unimplemented, unfinished, xfail

# Utils ------------------------------------------------------------------------

def get_queue(app):
    return app.get('/queue?format=json').json['data']['queue']

def del_queue(app, queue_item_id, expect_errors=False):
    """
    humm .. the current setup is not conforming to the REST standard,
       may need a refactor this
    response = app.delete('/queue', {'queue_item.id':queue_item_id})
    """
    return app.post('/queue', {'method':'delete', 'queue_item.id':queue_item_id}, expect_errors=expect_errors)


# Tests ------------------------------------------------------------------------

def test_queue_view_simple_add_delete_cycle(app, tracks):
    """
    View empty queue
    queue a track
    remove a track
    """
    assert get_queue(app) == []
    
    # Check no tracks in queue
    response = app.get('/queue')
    assert 'track 1' not in response.text
    
    # Queue 'Track 1'
    response = app.post('/queue', dict(track_id='t1', performer_name='testperformer'))
    
    # Check track is in queue list
    response = app.get('/queue')
    assert 'track 1' in response.text
    assert 'testperformer' in response.text
    # Check queue in track description
    response = app.get('/track/t1')
    assert 'testperformer' in response.text
    
    queue_item_id = get_queue(app)[0]['id']
    
    # Remove track from queue
    del_queue(app, queue_item_id)
    
    # Check queue is empty
    assert get_queue(app) == []


def test_queue_errors(app, tracks):
    response = app.post('/queue', dict(track_id='t1000'), expect_errors=True)
    assert response.status_code == 400
    assert 'performer' in response.text


@unimplemented
def test_queue_permissions(app, tracks):
    """
    Check only the correct users can remove a queued item
    Check only admin can move items
    """
    assert get_queue(app) == []
    
    # Queue a track
    response = app.post('/queue', dict(track_id='t1', performer_name='testperformer'))
    queue_item_id = get_queue(app)[0]['id']
    # Try to move the track (only admins can move things)
    response = app.put('/queue', {'queue_item.id':queue_item_id}, expect_errors=True)
    assert response.status_code == 403
    # Clear the cookies (ensure we are a new user)
    app.cookiejar.clear()
    # Attempt to delete the queued track (should fail)
    response = del_queue(app, queue_item_id, expect_errors=True)
    assert response.status_code == 403
    assert len(get_queue(app)) == 1, 'the previous user should not of had permissions to remove the item from the queue'
    # Become an admin, del track, remove admin status
    response = app.get('/admin')
    del_queue(app, queue_item_id)
    response = app.get('/admin')

    # TODO: assert remove button on correct elements on template
    
    assert get_queue(app) == []


@unfinished
def test_queue_view_update(app, tracks):
    """
    Update track status
    played
    performer?
    order?
    """
    assert get_queue(app) == []
    response = app.post('/queue', dict(track_id='t1', performer_name='testperformer'))
    app.cookiejar.clear()
    
    response = app.put('/queue', {'queue_item.id':'not_real_id'}, expect_errors=True)
    assert response.status_code == 400
    assert 'invalid queue_item.id' in response.text

    response = del_queue(app, queue_item_id, expect_errors=True)

    # What status's are updated?
    
    
    response = app.get('/admin')
    del_queue(app, queue_item_id)
    response = app.get('/admin')

    assert get_queue(app) == []


def test_queue_order(app, tracks):
    """
    Test the queue ordering and weighting system
    Only Admin user should be able to modify the track order
    """
    response = app.get('/admin')
    assert get_queue(app) == []
    
    # Setup queue
    for track_id, performer_name in [
        ('t1','testperformer1'),
        ('t2','testperformer2'),
        ('t3','testperformer3'),
        ('xxx','testperformer4')]:
        response = app.post('/queue', dict(track_id=track_id, performer_name=performer_name))
    queue = get_queue(app)
    assert ['t1','t2','t3','xxx'] == [q['track_id'] for q in queue]
    
    # Move last track to front of queue
    response = app.put('/queue', {'queue_item.id':queue[3]['id'], 'queue_item.move.target_id':queue[0]['id']})
    queue = get_queue(app)
    assert ['xxx','t1','t2','t3'] == [q['track_id'] for q in queue]
    
    # Move second track to back (or as back as we can)
    response = app.put('/queue', {'queue_item.id':queue[1]['id'], 'queue_item.move.target_id':queue[3]['id']})
    queue = get_queue(app)
    assert ['xxx','t2','t1','t3'] == [q['track_id'] for q in queue]
    
    # Tidy queue
    for queue_item in get_queue(app):
        del_queue(app, queue_item['id'])
    assert get_queue(app) == []
    response = app.get('/admin')


def test_queue_template(app,tracks):
    """
    The track order returned by the template should deliberatly obscure
    the order of tracks passed a configurable intavle (eg. 15 min)
    """
    pass


def test_queue_limit(app, tracks):
    """
    Users should not be able to queue over 45 minuets of tracks (settable in config)
    Users trying to add tracks after this time have a 'window period of priority'
    where they have first dibs.
    The user should be informed by the status flash message how long before they
    should retry there selection.
    """
    pass
